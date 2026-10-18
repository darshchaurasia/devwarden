---
type: Policy
title: Security
description: Keep credentials and local development data private.
status: stable
---

# Security

## Report a defect

Use the repository's private vulnerability reporting feature, when available.
If it is unavailable, ask the maintainer for a private reporting channel without sharing the defect details.
Do not put credentials, private repository URLs, or database files in a public issue.
If no private channel exists, request one without publishing sensitive details.

## Credentials

The project contains no personal account or recipient default.
The real `.env`, SMTP settings, reports, and credentials must remain outside version control.
Git ignores common local configuration files.
Git ignore rules do not remove files that were already committed.

Private configuration uses owner-only file permissions.
Passwords remain plaintext on local disk because the unattended service must read them.
Protect your operating-system account and backups.
Use a separate SMTP app password where the provider supports it.
Revoke that password if it is exposed.

SMTP uses verified TLS before authentication.
The application does not support plaintext SMTP transport.
Git uses your existing noninteractive credential helper or SSH configuration.
The application does not request a GitHub token in email settings.

## Repository safety

The updater only fast-forwards default branches.
It does not push, reset branches, discard development work, or force worktree removal.
Repository hooks are disabled for automated merges and temporary worktree creation.
Git configuration and external Git filters can still run programs.
Only operate on repositories and configuration that you trust.

GitHub token patterns and HTTP URL credentials are redacted from Git command errors.
This filter cannot identify every possible secret.
Review a diagnostic report before sharing it publicly.

## Local data

Reports can contain private repository names, branch names, paths, and Git errors.
Email sends those details to the configured recipient and SMTP provider.
Review the recipient before the first delivery test.
The service does not send data to an AI provider.
