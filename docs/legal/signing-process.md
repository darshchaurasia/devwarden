---
type: Procedure
title: Contributor assignment process
description: Prepare and verify a private assignment before accepting contributed work.
status: stable
sources:
  - resource: contributor-assignment.md
  - resource: ../../.github/CONTRIBUTING.md
  - resource: https://www.copyright.gov/title17/92chap2.html
---

# Contributor assignment process

## Current status

The owner adopted [assignment version 1.0](contributor-assignment.md) on October 18, 2026.
It names Darsh Chaurasia as the recipient of the assigned copyright.
It covers identified existing contributions and future contributions within its stated scope.
It uses Arizona law and competent courts in Maricopa County or the federal court in Phoenix.

The owner approved the terms and the private PDF signing process without a lawyer-review prerequisite.
The agreement has not been reviewed or approved by a lawyer.
The process is available for use. No contributor is approved merely because this form is published.

Before a merge, the owner must verify each actual rights holder's signed assignment.
A contributor license agreement or commit sign-off is not a substitute for that assignment.

## Private intake setup

Use the existing owner mailbox for a private PDF exchange.
No new paid service or public email address is needed.
Store the actual contact address in `~/.config/devwarden/assignment-intake.json`.
Do not put it in the source repository.
The [intake template](../../config/assignment-intake.example.json) contains no personal address.

Use `~/.local/state/devwarden/assignments/` for the private register and documents.
Create these directories with mode `700`:

- `pending/` for documents that have not been verified.
- `executed/` for the complete signed agreements.
- `evidence/` for original correspondence and authority evidence.

Copy the [register template](../../config/assignment-register.example.csv) to `register.csv` only if that file does not exist.
Use mode `600` for the register, contact configuration, and individual documents.
For custom DevWarden state paths, use an equivalent directory outside the checkout.
Do not overwrite an existing register during setup.
Back up actual records to access-controlled storage that the owner selects.
No remote backup is provisioned by this setup.

The owner's local intake settings and empty register have been prepared.
They do not contain an executed agreement or approve any contributor.
The mailbox has been tested with the existing SMTP delivery test.
That test does not prove that a contributor's identity or signature is valid.

## Private signature exchange

1. Export the complete adopted agreement and schedules to PDF.
2. Record its version and SHA-256 hash.
3. Use the [private request template](signing-request.example.md) to prepare the message.
4. Send it through the private channel agreed with the rights holder.
5. Obtain the signed complete PDF and any electronic-signature evidence.
6. Save the original email or other delivery record in `evidence/`.
7. Verify the identity, signature intent, rights holder, and included schedules.
8. Obtain the owner's signature.
9. Give both parties the same complete executed copy.
10. Record the executed file's hash and private location in the register.

A signature can be handwritten or electronic under this process.
An electronic signature must be attached to the complete agreement and used with intent to sign it.
If mandatory law requires additional formalities, satisfy them before accepting that contributor's assignment.
An unsigned attachment, public checkbox, or Git commit sign-off is not this process.
The project does not send request messages automatically.

## Process a contributor

1. Identify the contributor and the GitHub accounts used for contributions.
2. Determine who owns the proposed work.
3. If an employer or another entity owns it, obtain that entity's authorized signature.
4. Give the rights holder the adopted agreement through the private channel.
5. Ask the rights holder to identify existing contributions in Schedule A.
6. Ask the rights holder to identify exclusions and restrictions in Schedule B.
7. Obtain all required signatures through the approved method.
8. Examine the signed version, its scope, and the signatory's authority.
9. Save the executed agreement and evidence in private storage.
10. Record the result in the private register.
11. Verify coverage for all authors before the merge.

One adopted agreement can cover future contributions if its terms and applicable law permit that coverage.
A different rights holder, changed employer, or material agreement change can need a new signature.
A company signature does not automatically cover personal work that the company does not own.

## Private register

Keep signed agreements outside the public repository.
Use access controls and backups for the register and executed documents.

Record these fields:

- Contributor legal name or rights-holding entity.
- GitHub accounts and the identity verification method.
- Agreement version and signature dates.
- Private document location and signature evidence.
- Covered contributions, future coverage, and disclosed exclusions.
- Employer or entity authorization where applicable.
- Owner verification date and merge eligibility.

Public pull requests need only the coverage result. Do not post the private register.
Do not make a contributor's email address or legal document public through an automated check.

## Merge gate

The owner verifies assignments manually.
The repository test matrix and CODEOWNERS review do not validate legal signatures.
The owner must examine the assignment record before approval.

An automated coverage check is optional. The current process uses manual verification.
That check must examine all authors, not only the person who opens the pull request.
It must block a merge when coverage is missing or uncertain.
A successful automated check does not establish the validity of the legal agreement.
