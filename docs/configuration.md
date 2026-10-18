---
type: Reference
title: Configuration
description: Set repository, schedule, retention, and mail parameters without code changes.
status: stable
sources:
  - resource: ../config.py
  - resource: ../manage.py
  - id: timer
    resource: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
---

# Configuration

## Environment file

Copy `.env.example` to `.env` before setup.
The parser accepts literal `KEY=VALUE` entries, comments, and quoted values.
It does not execute commands or expand shell variables.
Use `~` or an absolute path for the repository folder.
Quote values that contain spaces.

Process environment values have priority over `.env` values.
An environment file beside the executing code has priority over the private environment file.
Nonempty environment values have priority over stored JSON settings.
Empty SMTP values do not erase stored credentials.

Setup copies selected environment values into private configuration storage.
It copies application files into private runtime storage.
It does not copy the source `.env` into the runtime directory.
Changes to the source `.env` take effect in the installed service after setup runs again.

## Parameters

| Variable | Default | Meaning |
|---|---|---|
| `DEVWARDEN_ROOT` | `~/code` | Folder whose immediate children are checked. |
| `DEVWARDEN_CALENDAR` | `Fri *-*-* 06:00:00` | systemd calendar expression. |
| `DEVWARDEN_RETENTION_DAYS` | `90` | Retention period for timestamped run logs. Minimum: 1. |
| `DEVWARDEN_SMTP_HOST` | `smtp.gmail.com` | SMTP server name. |
| `DEVWARDEN_SMTP_PORT` | `465` | SMTP server port. |
| `DEVWARDEN_SMTP_SECURITY` | `ssl` | `ssl` or `starttls`. Plaintext transport is not supported. |
| `DEVWARDEN_SMTP_SENDER` | Empty | Sender email address. |
| `DEVWARDEN_SMTP_RECIPIENT` | Empty | One report recipient. |
| `DEVWARDEN_SMTP_USERNAME` | Sender | SMTP login name. |
| `DEVWARDEN_SMTP_PASSWORD` | Empty | SMTP password. Prefer the hidden configuration prompt. |

Email remains off if no sender or recipient is configured.
Both addresses are required to send mail.
Set port `587` when you select `starttls`, unless your provider specifies another port.

### Select a time zone

Append a time zone to the calendar expression:

```dotenv
DEVWARDEN_CALENDAR="Fri *-*-* 06:00:00 Etc/UTC"
```

Validate a schedule with `systemd-analyze calendar`.
Calendar expressions follow systemd rules.[^timer]

## File locations

| Location | Content |
|---|---|
| `~/.config/devwarden/.env` | Installed environment settings. |
| `~/.config/devwarden/settings.json` | Selected repository folder, schedule, and retention. |
| `~/.config/devwarden/smtp.json` | Private SMTP settings and password. |
| `~/.local/share/devwarden/` | Installed runtime and unit templates. |
| `~/.local/bin/devwarden` | Installed command. |
| `~/.config/systemd/user/devwarden*` | Active user units. |
| `~/.local/state/devwarden/` | Logs, reports, queue, locks, and retained worktrees. |

Advanced users can set `DEVWARDEN_CONFIG_DIR` and `DEVWARDEN_STATE_DIR` in the process environment before setup.
Do not put these two variables in `.env`.
Installed units retain the selected storage paths.

Private JSON files and the installed environment file use mode `600`.
New state directories use mode `700`.
The source `.env` must also remain private.

## Installation without prompts

```sh
python3 manage.py setup --yes --root ~/code \
  --calendar 'Fri *-*-* 06:00:00 Etc/UTC'
```

The repository folder must exist before setup.
The installer validates the schedule before it installs units.

## Migrate an older installation

Run setup from this project version.
If `gmail.json` exists in private configuration storage, setup creates `smtp.json` when necessary.
The older sender becomes the initial recipient.
The original private credential file remains for recovery.
Review the recipient with `devwarden email-configure` if necessary.
No credential is copied into the project.

[^timer]: [systemd timer reference](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html).
