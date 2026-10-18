---
type: Release Notes
title: Release notes
description: Record user-visible changes to DevWarden.
status: stable
---

# Release notes

## 0.1.0

- Use DevWarden as the product name and `devwarden` as the command.

- Adopt PolyForm Perimeter 1.0.1 and require copyright assignment for contributed work.
- Add issue forms, a pull-request template, and owner review requirements.
- Add setup and service management commands.
- Move account and schedule settings out of application code.
- Add `.env.example` and private installed configuration.
- Add optional SMTP over SSL or STARTTLS.
- Keep development checkouts through temporary worktrees.
- Exclude remotes without branch code.
- Add HTML reports with diagnostic columns and plain-text alternatives.
- Add offline tests and a GitHub Actions test matrix.
- Add OKF v0.2 documentation and an explicit language review record.

The source repository is published on GitHub. See the Actions tab for remote test results.

## Layout and documentation update

- Move runtime code into `src/devwarden/` and tests into `tests/`.
- Group guides, references, examples, and release notes under `docs/`.
- Bundle systemd templates with the application package.
- Add source launchers, a rendered Markdown report example, and a pending-work register.
- Examine all Python docstrings, Python 3.10 syntax, and local documentation links in CI.

## Commit checks

- Add native pre-commit, commit-message, and pre-push hooks.
- Test staged and pushed snapshots without private local configuration.
- Require Conventional Commit subjects and pull-request titles in CI.

## Language review

- Separate instructions into individual steps.
- Simplify report recovery instructions and source documentation.
- Record software terminology and the limits of the agent language review.
