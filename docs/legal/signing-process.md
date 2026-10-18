---
type: Procedure
title: Contributor assignment process
description: Prepare and verify a private assignment before accepting contributed work.
status: draft
sources:
  - resource: contributor-assignment-draft.md
  - resource: ../../.github/CONTRIBUTING.md
  - resource: https://www.copyright.gov/title17/92chap2.html
---

# Contributor assignment process

## Current status

The [assignment document](contributor-assignment-draft.md) is a draft.
It names Darsh Chaurasia as the recipient of the assigned copyright.
It covers identified existing contributions and proposes coverage for future contributions.
It is not ready for signatures.
External copyrightable contributions must not be merged yet.

## Prepare the final agreement

1. Select the governing law.
2. Select the dispute forum.
3. Obtain legal review of the assignment and its use across contributor jurisdictions.
4. Confirm the requirements for consideration and execution.
5. Select an approved signature method.
6. Set up a private channel for completed documents.
7. Adopt the final agreement with a version and effective date.
8. Replace the draft links in the contribution instructions with the adopted agreement.

The review must examine future contributions, employer-owned work, patent permissions, and personal rights that cannot be assigned.
Legal review must also establish the evidence needed for the chosen signature method.
A repository comment alone is not an approved assignment process.
A contributor license agreement or commit sign-off is not a substitute for the required assignment.

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

The owner currently verifies assignments manually.
The repository test matrix and CODEOWNERS review do not validate legal signatures.
The owner must examine the assignment record before approval.

An automated coverage check can be added after the final agreement and identity process are adopted.
That check must examine all authors, not only the person who opens the pull request.
It must block a merge when coverage is missing or uncertain.
A successful automated check does not establish the validity of the legal agreement.
