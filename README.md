---
type: Application Manual
title: DevWarden
description: Install a local service that updates GitHub repositories and reports the results.
status: stable
tags: [git, automation, systemd]
sources:
  - resource: src/devwarden/cli.py
  - resource: src/devwarden/update.py
  - resource: src/devwarden/report.py
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

- Keep your local copies of open-source projects current.
- Prepare local projects before your regular development sessions.
- Examine which default branches need manual attention.
- Keep a local project collection current. Leave active development branches unchanged.

DevWarden maintains default branches. It does not synchronize development changes between computers.

[Quick start](#quick-start) · [Operation](#operation) · [Update rules](#update-rules) · [Configuration](docs/guides/configuration.md) · [Troubleshooting](docs/guides/operations.md)

## Features

| Feature | Behavior |
|---|---|
| Automatic updates | Discover repositories directly inside the selected folder. |
| Default branch detection | Use the remote default branch, including branches with names other than `main`. |
| Development work protection | Update the default branch in a separate worktree when another branch is active. |
| Clear reports | Show errors, exclusions, updates, and current repositories in separate sections. |
| Email queue | Keep unsent reports and retry delivery each hour. |
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

Clone the project. Then open its directory:

```sh
git clone https://github.com/darshchaurasia/devwarden.git
cd devwarden
```

1. Create your local configuration:

   ```sh
   cp config/.env.example .env
   chmod 600 .env
   ```

2. Edit `.env` to select the repository folder and schedule.
   Keep `.env` private. Git ignores this file.

3. Install the service:

   ```sh
   python3 scripts/devwarden.py setup
   ```

4. Examine the installation:

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
A persistent timer can start an update after installation if a scheduled update was missed.

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
DevWarden does not need a paid email service.
Your email provider's limits still apply.

Without email configuration, the service saves local reports.
It does not attempt SMTP delivery.
See the [configuration reference](docs/guides/configuration.md) for environment settings and private file locations.

## Operation

| Command | Purpose |
|---|---|
| `devwarden run` | Start the background service now. |
| `devwarden preview` | Examine readiness without changing Git branches or repository files. |
| `devwarden status` | Show the last service state. |
| `devwarden logs` | Show update and email logs. |
| `devwarden doctor` | Examine settings and service prerequisites. |
| `devwarden email-configure` | Set the SMTP account and recipient. |
| `devwarden email-test` | Send a real test email. |
| `devwarden email-retry` | Retry queued email now. |
| `devwarden uninstall` | Remove installed services and keep private data. |

Use `python3 scripts/devwarden.py COMMAND` from the project as an alternative.
After a successful update, the service returns to the inactive state.
A repository error produces a failed service state and an error report.

## Update rules

| Condition | Result |
|---|---|
| Default branch is current | Report `CURRENT`. |
| Default branch can advance without a merge commit | Advance the branch and report `UPDATED`. |
| Another branch is active | Keep that checkout and update the default branch in a temporary worktree. |
| Local changes exist on the active default branch | Report `ERROR`. Keep the changes. |
| Default branch has local-only commits | Report `ERROR`. Keep the commits. |
| Git operation, lock, sparse checkout, or detached HEAD | Report `ERROR`. |
| Remote has branches but no default branch | Report `ERROR`. |
| Remote has no branches | Report an exclusion. Examine again on the next run. |
| Origin is not GitHub | Report an exclusion. |
| Repository contains `.no-auto-update` | Report an exclusion. |
| Remote access fails | Retry network commands, then report `ERROR`. |

An error means that the updater could not make sure that the default branch is current.
Other repositories continue after one repository fails.
The service does not automatically reset branches or discard local work.
It does not create merge commits or push commits.

Repository discovery does not enter nested directories or follow directory symlinks.
The service does not install dependencies or download submodules or LFS objects.
See [operation and recovery](docs/guides/operations.md) for limits and recovery steps.

## Reports

[View a sample report](docs/examples/report.md). The sample uses fictional repositories.

GitHub displays the Markdown example as a formatted document.
For the email layout, download [the HTML example](docs/examples/report.html).
Open the file in a local browser.
GitHub displays HTML source. It does not display HTML files as web pages.

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

The report identifies the development branch that the updater keeps.
Counts from an interrupted run cover only recorded results.
An SMTP server can accept a message that a spam filter then stops.

## Update this service

Get the next project version. Examine its changes.
Then run setup again from that version:

```sh
python3 scripts/devwarden.py setup --yes
```

Setup updates the installed runtime and keeps private credentials.
Wait for an active update to finish before setup.
Review `.env` before reinstalling. Nonempty values can override stored settings.

## Remove this service

```sh
~/.local/bin/devwarden uninstall
```

The source project, private settings, credentials, and reports stay.
Use the paths in the [configuration reference](docs/guides/configuration.md) to examine the data that stays after removal.
Do not delete state storage until you examine the worktrees in that storage.

## License and ownership

Copyright (c) 2026 Darsh Chaurasia.
DevWarden uses [PolyForm Perimeter 1.0.1](LICENSE.md).
It is source-available software, not OSI open-source software.

Individuals and businesses can use DevWarden internally.
They can change it for purposes that the license permits.
The license prohibits providing a competing product, including a competing free substitute.
It does not prohibit every commercial use.
Read the complete license before redistribution or external service use.

Contributions are welcome under the separate [ownership requirements](.github/CONTRIBUTING.md#ownership-requirements).
Accepted copyrightable contributions require a signed copyright assignment to Darsh Chaurasia.
A pull request alone does not transfer ownership.

The owner may offer future versions under other terms where the owner holds the necessary rights.
A future private version does not withdraw permissions already granted for a released version.

## Contribute

Bug reports, feature proposals, and reviewed contributions are welcome.
Read [Contributing](.github/CONTRIBUTING.md) before you start.
It explains the fork-and-pull-request process, test matrix, owner review, and required copyright assignment.

Darsh Chaurasia is the project owner and the designated recipient of contribution assignments.
Do not assume that a pull request transfers ownership automatically.
Before a merge, the owner must make sure that the contributor has signed the applicable assignment.
The owner adopted [assignment version 1.0](docs/legal/contributor-assignment.md) and the [private signing procedure](docs/legal/signing-process.md).
The agreement has not been reviewed by a lawyer. The owner approved proceeding without that prerequisite.
Contributions can proceed through this process once the actual rights holder signs and the owner verifies coverage.

## Project layout

```text
config/                        Environment example
scripts/                       Source launchers and test command
src/devwarden/                 Application package
  resources/systemd/           Service and timer templates
tests/                         Offline tests
docs/
  guides/                      Configuration and operation
  reference/                   Technical terms and review record
  examples/                    Report examples
  releases/                    Release notes
  legal/                       Contribution assignment and signing procedure
.github/                       CI, contribution guide, security policy, and forms
```

The README, license, package metadata, and documentation index stay at the root.
GitHub and Python tools use these standard locations.
Your private `.env` stays outside version control.

## Documentation and development

- [Configuration](docs/guides/configuration.md)
- [Operation and recovery](docs/guides/operations.md)
- [Security](.github/SECURITY.md)
- [Contributing](.github/CONTRIBUTING.md)
- [Release notes](docs/releases/changelog.md)
- [Pending work](docs/reference/pending.md)
- [Documentation review](docs/reference/documentation-review.md)
- [Technical terms](docs/reference/terms.md)
- [License](LICENSE.md)

Enable commit and push checks for this clone:

```sh
python3 scripts/checks.py install
```

The hooks check staged code, commit subjects, and pushed commits.
See [Contributing](.github/CONTRIBUTING.md#git-hooks-and-commit-subjects) for the commit format.

Run the offline tests:

```sh
python3 scripts/test.py
```

The documentation targets Open Knowledge Format v0.2.
See the review record for ASD-STE100 Issue 9 review scope and limits.

[^gmail]: [Google: Sign in with app passwords](https://support.google.com/accounts/answer/185833).
