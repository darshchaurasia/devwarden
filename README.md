---
type: Application Manual
title: DevWarden
description: Install a local service that updates GitHub repositories and reports the results.
status: stable
tags: [git, automation, systemd]
sources:
  - resource: manage.py
  - resource: update.py
  - resource: report.py
  - id: gmail
    resource: https://support.google.com/accounts/answer/185833
---

# DevWarden

[![Tests](https://github.com/darshchaurasia/devwarden/actions/workflows/tests.yml/badge.svg)](https://github.com/darshchaurasia/devwarden/actions/workflows/tests.yml)

**Keep your local Git projects current. Keep your development work safe.**

DevWarden is a local service for Linux and WSL with systemd.
It checks GitHub repositories on a schedule and saves a report after each run.
Email delivery is optional.

## Where to use DevWarden

Use DevWarden on a Linux workstation, in a WSL development environment, or on a Linux server with systemd.
It is useful when one development folder contains many independent Git projects.

- Keep your open-source reference clones current.
- Prepare local projects before your regular development sessions.
- Check which default branches need manual attention.
- Maintain a local project collection without disturbing active development branches.

DevWarden maintains default branches. It does not synchronize development changes between computers.

[Quick start](#quick-start) · [Operation](#operation) · [Update rules](#update-rules) · [Configuration](docs/configuration.md) · [Troubleshooting](docs/operations.md)

## Features

| Feature | Behavior |
|---|---|
| Automatic updates | Discover repositories directly inside the selected folder. |
| Default branch detection | Use the remote default branch, including branches with names other than `main`. |
| Development work protection | Update the default branch in a separate worktree when another branch is active. |
| Clear reports | Show errors, exclusions, updates, and current repositories in separate sections. |
| Email queue | Retain unsent reports and retry delivery each hour. |
| Missed schedule recovery | Run once after a missed schedule when the user service manager starts. |
| Local operation | Use Python, Git, and systemd. No AI service is required. |

## Requirements

- Linux, or WSL with systemd enabled.
- Python 3.10 or later.
- Git 2.28 or later.
- A systemd user manager and `systemd-analyze`.
- Network access to GitHub. SMTP access is required only for email.
- Git credentials that operate without a prompt for private repositories.

Native Windows and macOS services are not supported.
The installer does not require administrator access.

## Quick start

Clone the project and open its directory:

```sh
git clone https://github.com/darshchaurasia/devwarden.git
cd devwarden
```

1. Create your local configuration:

   ```sh
   cp .env.example .env
   chmod 600 .env
   ```

2. Edit `.env` to select the repository folder and schedule.
   Keep `.env` private. Git ignores this file.

3. Install the service:

   ```sh
   python3 manage.py setup
   ```

4. Check the installation:

   ```sh
   ~/.local/bin/devwarden doctor
   ```

5. Preview the next update:

   ```sh
   ~/.local/bin/devwarden preview
   ```

6. Start an update:

   ```sh
   ~/.local/bin/devwarden run
   ```

The default schedule is Friday at 06:00 in the system time zone.
A delay of up to five minutes distributes service starts.
The installer does not update repositories during setup.
A pending persistent timer can cause a catch-up run after installation.

If `~/.local/bin` is on your `PATH`, use `devwarden` without its full path.

### Optional email

Configure an SMTP account with verified TLS:

```sh
~/.local/bin/devwarden email-configure
~/.local/bin/devwarden email-test
```

The password prompt does not display its input.
The service supports SMTP over SSL and SMTP with STARTTLS.
For Gmail, use an app password from an account with 2-Step Verification.[^gmail]
No paid email service is required by this application.
Your email provider's limits still apply.

Without email configuration, the service saves local reports.
It does not attempt SMTP delivery.
See the [configuration reference](docs/configuration.md) for environment settings and private file locations.

## Operation

| Command | Purpose |
|---|---|
| `devwarden run` | Start the background service now. |
| `devwarden preview` | Inspect readiness without changing Git branches or repository files. |
| `devwarden status` | Show the last service state. |
| `devwarden logs` | Show update and email logs. |
| `devwarden doctor` | Check settings and service prerequisites. |
| `devwarden email-configure` | Set the SMTP account and recipient. |
| `devwarden email-test` | Send a real test email. |
| `devwarden email-retry` | Retry queued email now. |
| `devwarden uninstall` | Remove installed services and keep private data. |

Use `python3 manage.py COMMAND` from the project as an alternative.
A successful completed service returns to the inactive state.
A repository error produces a failed service state and an error report.

## Update rules

| Condition | Result |
|---|---|
| Default branch is current | Report `CURRENT`. |
| Default branch can advance without a merge commit | Advance the branch and report `UPDATED`. |
| Another branch is active | Preserve that checkout and update the default branch in a temporary worktree. |
| Local changes exist on the active default branch | Report `ERROR`. Preserve the changes. |
| Default branch has local-only commits | Report `ERROR`. Preserve the commits. |
| Git operation, lock, sparse checkout, or detached HEAD | Report `ERROR`. |
| Remote has branches but no default branch | Report `ERROR`. |
| Remote has no branches | Report an exclusion. Check again on the next run. |
| Origin is not GitHub | Report an exclusion. |
| Repository contains `.no-auto-update` | Report an exclusion. |
| Remote access fails | Retry network commands, then report `ERROR`. |

An error means that the default branch was not confirmed current.
Other repositories continue after one repository fails.
The service never automatically resets branches, discards local work, creates merge commits, or pushes commits.

Repository discovery does not enter nested directories or follow directory symlinks.
The service does not install dependencies or download submodules or LFS objects.
See [operation and recovery](docs/operations.md) for limits and recovery steps.

## Reports

[Open a sample HTML report](docs/report-example.html). The sample uses fictional repositories.

Each run saves a text log, a text report, and an HTML report in private state storage.
Email contains HTML and plain-text versions.

| Section | Columns |
|---|---|
| Errors | Repository, branch, reason, diagnostics, suggested action |
| Updated | Repository, branch, commits added, changes link |
| Current | Repository and branch |
| Excluded | Repository and reason |

Diagnostics include failed commands, exit codes, attempts, and timeouts where available.
Diverged history includes local and remote commit counts.
Repository links open GitHub. Change links compare the exact before and after commits.

A preserved development branch is identified in the report.
Counts from an interrupted run cover only recorded results.
SMTP acceptance does not guarantee inbox placement.

## Update this service

Obtain and review the next project version.
Then run setup again from that version:

```sh
python3 manage.py setup --yes
```

Setup refreshes the installed runtime and keeps private credentials.
Wait for an active update to finish before setup.
Review `.env` before reinstalling. Nonempty values can override stored settings.

## Remove this service

```sh
~/.local/bin/devwarden uninstall
```

The source project, private settings, credentials, and reports remain.
Use the paths in the [configuration reference](docs/configuration.md) to review retained data.
Do not delete state storage until you inspect retained worktrees.

## License and ownership

Copyright (c) 2026 Darsh Chaurasia.
DevWarden uses [PolyForm Perimeter 1.0.1](LICENSE).
It is source-available software, not OSI open-source software.

Individuals and businesses can use DevWarden internally and make changes for permitted purposes.
The license prohibits providing a competing product, including a competing free substitute.
It does not prohibit every commercial use.
Read the complete license before redistribution or external service use.

Contributions are welcome under the separate [ownership requirements](CONTRIBUTING.md#ownership-requirements).
Accepted copyrightable contributions require a signed copyright assignment to Darsh Chaurasia.
Submitting a pull request alone does not transfer ownership.

The owner may offer future versions under other terms where the owner holds the necessary rights.
A future private version does not withdraw permissions already granted for a released version.

## Contribute

Bug reports, feature proposals, and reviewed contributions are welcome.
Read [Contributing](CONTRIBUTING.md) before you start.
It explains the fork-and-pull-request process, test matrix, owner review, and required copyright assignment.

Darsh Chaurasia is the project owner and the designated recipient of contribution assignments.
Do not assume that a pull request transfers ownership automatically.
The owner must verify a signed assignment before merging contributed work.
The agreement is being finalized, so code contributions remain pending until that process is in place.

## Documentation and development

- [Configuration](docs/configuration.md)
- [Operation and recovery](docs/operations.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Release notes](CHANGELOG.md)
- [Documentation review](docs/documentation-review.md)
- [Technical terms](docs/terms.md)
- [License](LICENSE)

Run the offline tests:

```sh
python3 -m unittest discover -s . -p 'test_*.py'
```

The documentation targets Open Knowledge Format v0.2.
See the review record for ASD-STE100 Issue 9 review scope and remaining items.

[^gmail]: [Google: Sign in with app passwords](https://support.google.com/accounts/answer/185833).
