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
3. Fork the project and create a development branch.
4. Make a focused change and add relevant tests.
5. Run the offline test command below.
6. Open a pull request with the contribution template.
7. Wait for the test matrix and the owner's review.

Do not publish signed agreements or private contact details in issues or pull requests.
The owner supplies a private submission channel for legal documents.

## Ownership requirements

Darsh Chaurasia is the project owner and designated recipient of contribution assignments.
Accepted copyrightable code, documentation, and assets require a signed assignment to the owner.
A license grant alone does not satisfy this ownership policy.

The owner must verify that each relevant contributor signed the applicable assignment.
Employer-owned work also requires authorization from its actual rights holder.
Do not submit third-party material as your own work.
A contributor cannot assign rights that they do not own.

A pull-request checkbox, commit sign-off, or GitHub account does not by itself establish a completed assignment.
The owner verifies legal records privately before approving the contribution.
The assignment form is being finalized. Code contributions must not be merged until it is adopted and executed.

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
Repository administrators retain GitHub's administrative bypass capability.
The owner must still verify contribution rights before accepting third-party work.
A required code-owner approval includes a manual verification of the signed assignment.
No automated legal-signature verification is claimed.
An optional signing integration can be added after the agreement is adopted.

## Development

Use Python 3.10 or later and Git 2.28 or later.
The runtime and offline tests require no third-party Python packages.

```sh
python3 -m unittest discover -s . -p 'test_*.py'
python3 manage.py --help
```

Do not use real credentials in tests.
Use temporary Git repositories for update tests.
Use mocked SMTP connections for email tests.
Do not run setup against your live user manager during an automated test.

## Required checks

- Preserve staged, unstaged, ignored, and untracked development files.
- Preserve local-only commits.
- Distinguish empty remotes from remote access failures.
- Check HTML escaping and diagnostic redaction.
- Check TLS before SMTP authentication.
- Check retry queue retention after delivery failure.
- Check environment parsing without shell execution.
- Check private file permissions.
- Check installer behavior with isolated paths and mocked systemd commands.

Every public function needs a docstring.
Use comments to explain safety decisions that the code does not make clear.
Keep configuration outside application code.
Do not add an AI service dependency.

## Documentation

Use OKF v0.2 metadata for each concept document.
Use short sentences, active instructions, and consistent technical terms.
Use [technical terms](docs/terms.md) for software-specific meanings.
See the [review record](docs/documentation-review.md) before making a conformance claim.

## Release

1. Run the offline tests.
2. Review the source for credentials and personal information.
3. Check setup in an isolated user environment.
4. Check a live local report and, when configured, SMTP delivery.
5. Update the release notes and review record.

GitHub Actions repeats the offline tests on the supported Python matrix.
A workflow file alone does not prove that a remote CI run passed. Check the Actions tab for results.
