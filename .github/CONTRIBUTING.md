---
type: Procedure
title: Contributing
description: Change the service and check repository safety before release.
status: stable
---

# Contributing

## Contribution process

1. Open an issue to discuss the change before substantial work.
2. Contact the project owner to arrange the required copyright assignment.
3. Fork the project.
4. Create a development branch.
5. Enable the hooks.
6. Make the agreed change.
7. Add the related tests.
8. Run the offline test command below.
9. Open a pull request with the contribution template.
10. Wait for the test matrix and the owner's review.

Do not publish signed agreements or private contact details in issues or pull requests.
The owner supplies a private submission channel for legal documents.

## Ownership requirements

Darsh Chaurasia is the project owner and designated recipient of contribution assignments.
Accepted copyrightable code, documentation, and assets require a signed assignment to the owner.
A license grant alone does not satisfy this ownership policy.

The owner must make sure that each applicable contributor signed the assignment.
Employer-owned work also requires authorization from its actual rights holder.
Do not submit third-party material as your own work.
A contributor cannot assign rights that they do not own.

A pull-request checkbox, commit sign-off, or GitHub account does not by itself establish a completed assignment.
Before approval, the owner examines the private legal records.
The [assignment draft](../docs/legal/contributor-assignment-draft.md) and [signing process](../docs/legal/signing-process.md) are available for review.
The assignment form is not final.
The owner must adopt the agreement before accepting signed copies.
Before a merge, the owner must verify the signed assignment.

## Pull-request pipeline

GitHub Actions runs the offline tests on Python 3.10, 3.12, and 3.14.
The workflow uses read-only repository permissions and does not use SMTP or production credentials.
The CODEOWNERS file routes all code changes to the project owner.
The pull-request template records tests, documentation changes, and contribution-rights review.

The public repository uses main-branch protection for contributor changes:

- Require a pull request before merge.
- Require the test matrix checks to pass.
- Require code-owner review.
- Dismiss approvals when new commits change a pull request.
- Block force pushes and branch deletion.

These settings are enforced on GitHub, not by a README or CODEOWNERS alone.
Repository administrators keep GitHub's administrative bypass capability.
Before a merge, the owner must verify the rights to contributed work.
A required code-owner approval includes a manual verification of the signed assignment.
No automated legal-signature verification is claimed.
An optional signing integration can be added after the agreement is adopted.

## Development

Use Python 3.10 or later and Git 2.28 or later.
The runtime and offline tests require no third-party Python packages.

```sh
python3 scripts/checks.py install
python3 scripts/test.py
python3 scripts/devwarden.py --help
```

### Git hooks and commit subjects

Enable hooks once for each clone with `python3 scripts/checks.py install`.
Git does not enable repository hooks automatically when you clone a project.
The command sets this clone's `core.hooksPath` to `.githooks`.
The hooks require Python 3, Git, and `tar` on Linux or WSL.

| Hook | Check |
|---|---|
| `pre-commit` | Examine staged whitespace and run the offline tests on an exported copy of the staged tree. |
| `commit-msg` | Require a Conventional Commit subject of at most 72 characters and a blank line before the body. |
| `pre-push` | Examine new commit subjects and run offline tests on each distinct pushed commit tip. Deleted refs are skipped. |

Use a colon after the type or scope. Examples:

```text
feat(hooks): validate staged code before commit
fix(smtp): retain reports after delivery failure
docs: explain missed timer recovery
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, and `revert`.
An optional scope identifies the component.
For a breaking change, add `!` before the colon.
Use `fix` for a bug correction.
In the commit body, explain the change. Give the test results.
Pull-request titles must follow the same subject rule because releases use squash merges.

Local hooks can be bypassed. GitHub Actions also checks commit subjects,
pull-request titles, and the test suite through the required test matrix.
Hooks and CI never send email or use production SMTP credentials.

Do not use real credentials in tests.
Use temporary Git repositories for update tests.
Use mocked SMTP connections for email tests.
Do not run setup against your live user manager during an automated test.

## Required checks

- Keep staged, unstaged, ignored, and untracked development files.
- Keep local-only commits.
- Distinguish empty remotes from remote access failures.
- Examine HTML escaping and diagnostic redaction.
- Examine TLS before SMTP authentication.
- Examine retry queue retention after delivery failure.
- Examine environment parsing without shell execution.
- Examine private file permissions.
- Examine installer behavior with isolated paths and mocked systemd commands.

Every public function needs a docstring.
Use comments to explain safety decisions that the code does not make clear.
Keep configuration outside application code.
Do not add an AI service dependency.

## Documentation

Use OKF v0.2 metadata for each concept document.
Use short sentences, active instructions, and consistent technical terms.
Keep runtime code in `src/devwarden/` and offline checks in `tests/`.
Use [technical terms](../docs/reference/terms.md) for software-specific meanings.
See the [review record](../docs/reference/documentation-review.md) before making a conformance claim.

## Release

1. Run the offline tests.
2. Review the source for credentials and personal information.
3. Examine setup in an isolated user environment.
4. Examine a report from a local service run.
5. If SMTP is configured, test email delivery.
6. Update the release notes.
7. Update the review record.

GitHub Actions repeats the offline tests on the supported Python matrix.
A workflow file alone does not prove that a remote CI run passed. Examine the Actions tab for results.
