---
type: Playbook
title: Operation and recovery
description: Check service results and recover from common failures.
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
It does not repeat every missed week.

In WSL, Windows startup alone does not guarantee WSL startup.
This project does not install a Windows Task Scheduler task.
Start WSL before you expect a catch-up run.
The timer does not deliberately wake a powered-off computer.

Check user lingering with `devwarden doctor`.
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

## Preserve development work

The updater does not change a checkout on a development branch.
It updates the local default branch in a separate temporary Git worktree.
Staged, unstaged, ignored, and untracked files stay in the original checkout.

Local changes on the active default branch cause an error.
Review these changes yourself before the next run.
The service does not automatically commit or stash them.

A default branch already checked out elsewhere prevents a new worktree.
Inspect `git worktree list` before recovery.
Do not force removal of another active checkout.

## Interrupted worktrees

Temporary worktrees are under the state directory's `worktrees/` folder.
Normal completion removes a clean temporary worktree.
A sudden shutdown, timeout, or unexpected local file can leave one behind.

1. Inspect `git worktree list` in the affected repository.
2. Inspect the retained worktree with `git -C PATH status`.
3. Preserve any local work before removal.
4. Remove a clean retained worktree with `git worktree remove PATH`.
5. Start the updater again.

Do not use forced removal without a separate review.
Do not delete a Git lock while its owning process runs.

## Limits

- Each Git command has a 180-second time limit.
- A failed network command has up to three attempts.
- The service has a four-hour start limit.
- The email retry service has a five-minute limit.
- A process lock prevents concurrent updater runs.
- A separate process lock prevents concurrent email queue delivery.

The service does not stop an editor or another Git process.
Checks reduce conflicts but do not make concurrent user activity atomic.
Run the service during a quiet work period.

The service disables repository hooks for merge and worktree creation.
Submodules, LFS objects, dependency installs, and builds are outside its scope.
Only use repository code and Git configuration that you trust.

## Mail delivery

The service saves a report before attempting mail delivery.
Failed delivery retains the queued report.
An hourly timer retries the queue.
The next update also retries queued reports.

If email is off, reports stay local and queued.
If email is later enabled, the queue can contain older reports.
Inspect the queue before you enable delivery if old reports must not be sent.

SMTP acceptance means that the provider accepted the message.
Spam filtering or recipient rules can still affect delivery.
A lost connection after acceptance can cause a duplicate on retry.

To check mail delivery, run `devwarden email-test`.
To retry the queue, run `devwarden email-retry`.
If credentials expire, update them with `devwarden email-configure`.

A sudden power loss can prevent the report handler from running.
No service on an offline computer can send its own outage notification.
Use an independent monitor if outage notification is required.

## Retention

The next update removes timestamped run logs older than the configured retention period.
The current report is retained.
Unsent reports and retained worktrees are not automatically deleted.
Monitor state storage if delivery remains unavailable for a long period.
