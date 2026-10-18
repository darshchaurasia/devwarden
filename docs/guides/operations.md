---
type: Playbook
title: Operation and recovery
description: Examine service results and recover from common failures.
status: stable
sources:
  - resource: ../../src/devwarden/update.py
  - resource: ../../src/devwarden/report.py
  - resource: ../../src/devwarden/cli.py
---

# Operation and recovery

## Computer and WSL availability

The computer cannot run this service while it is off.
A persistent timer starts one catch-up run when the user service manager becomes available.
It starts only one update, even if more than one week was missed.

In WSL, Windows startup alone does not guarantee WSL startup.
This project does not install a Windows Task Scheduler task.
Start WSL before you expect a catch-up run.
The timer does not deliberately wake a powered-off computer.

Examine user lingering with `devwarden doctor`.
Without lingering, service availability can depend on an active login session.
If background operation without login is required, ask the system administrator to enable lingering for your user.

## Read results

```sh
devwarden logs
systemctl --user list-timers 'devwarden*' --no-pager
```

Open `latest-report.html` or `latest-report.txt` in private state storage.
Read timestamped `.log` files for the full recorded output.
GitHub access requires working Git credentials, independent of email credentials.

## Keep development work

The updater does not change a checkout on a development branch.
It updates the local default branch in a separate temporary Git worktree.
Staged, unstaged, ignored, and untracked files stay in the original checkout.

If the active default branch has local changes, the updater reports an error.
Examine these changes before the next update.
The service does not automatically make a commit or a Git stash for those changes.

A default branch already checked out elsewhere prevents a new worktree.
Examine `git worktree list` before recovery.
Do not force removal of another active checkout.

## Interrupted worktrees

Temporary worktrees are under the state directory's `worktrees/` folder.
After a successful update, the updater removes the clean temporary worktree.
A sudden shutdown, timeout, or unexpected local file can leave one behind.

1. Examine `git worktree list` in the affected repository.
2. Examine the kept worktree with `git -C PATH status`.
3. Keep any local work before removal.
4. Remove a clean kept worktree with `git worktree remove PATH`.
5. Start the updater again.

**CAUTION:** Do not force worktree removal before you examine its files.
Forced removal can delete local work.
Do not delete a Git lock while its process operates.

## Limits

- Each Git command has a 180-second time limit.
- A failed network command has up to three attempts.
- The update service has a four-hour time limit.
- The email retry service has a five-minute limit.
- A process lock prevents simultaneous updater runs.
- A separate process lock prevents simultaneous email queue delivery.

The service does not stop an editor or another Git process.
Checks decrease conflicts. They cannot prevent all conflicts with other programs or user commands.
Run the service during a quiet work period.

The service disables repository hooks for merge and worktree creation.
Submodules, LFS objects, dependency installs, and builds are outside its scope.
Only use repository code and Git configuration that you trust.

## Mail delivery

The service saves a report before it tries to send email.
If delivery fails, the queue keeps the report.
An hourly timer retries the queue.
The next update also retries queued reports.

If email is off, reports stay local and queued.
If email is later enabled, the queue can contain older reports.
If old reports must not be sent, examine the queue before you enable delivery.

SMTP acceptance means that the provider accepted the message.
Spam filters and recipient rules can stop delivery.
If the connection fails after the server accepts a message, the next attempt can send a duplicate.

To check mail delivery, run `devwarden email-test`.
To retry the queue, run `devwarden email-retry`.
If credentials expire, update them with `devwarden email-configure`.

A sudden power loss can prevent the report handler from running.
A service cannot send an outage notification while its computer is offline.
Use an independent monitor if outage notification is required.

## Retention

The next update removes timestamped run logs older than the configured retention period.
The current report is kept.
Unsent reports and kept worktrees are not automatically deleted.
Monitor state storage if delivery stays unavailable for a long period.
