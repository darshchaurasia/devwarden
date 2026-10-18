---
type: Review Record
title: Documentation review
description: Record the format review, language changes, evidence, and limits.
status: stable
sources:
  - id: okf
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
    title: Open Knowledge Format specification v0.2
  - id: ste
    resource: https://www.asd-ste100.org/
    title: ASD-STE100 Issue 9, January 2025
---

# Documentation review

## Review result

The agent language review is complete for the scope below, as of October 18, 2026.
The review used the official ASD-STE100 Issue 9 writing rules and dictionary.[^ste]
The project does not distribute the standard or its dictionary.
This record does not claim independent certification or full STE conformance.

## Scope

The review covered these project texts:

- README and the documentation index.
- Configuration and operation guides.
- Contribution instructions, security policy, and pull-request form.
- Technical terms, release notes, and report examples.
- Python module, class, and function docstrings.
- Python source comments.
- Application report notes and error recovery instructions.

The agent examined wording, sentence structure, procedure steps, and technical terms.
The agent used dictionary entries to select alternatives for general verbs.
The [glossary](terms.md) records software-specific nouns and verbs.
These terms have meanings within this project, not general dictionary approval.

## Rules and changes

| Issue 9 rules | Examination and changes |
|---|---|
| 1.1–1.14: words | Replace general verbs such as `inspect`, `retain`, and `preserve` with simpler alternatives. Record software terms separately. |
| 2.1–2.2: groups of nouns | Examine headings, glossary terms, report labels, and configuration descriptions. Explain software terms in the glossary. |
| 3.1–3.7: verbs | Use direct instructions and active descriptions. Rewrite unnecessary passive constructions and complex verb phrases. |
| 4.1–4.5: sentences | Shorten sentences. Use explicit subjects and articles where needed. Keep exact command names unchanged. |
| 5.1–5.5: procedures | Separate the contribution steps and report recovery instructions. Put necessary conditions before their instructions. |
| 6.1–6.6: descriptions | Keep each paragraph on one topic. Examine prose for the descriptive sentence-length limit. |
| 7.1–7.3: safety instructions | Keep commands about data loss and credentials direct. Keep the cause and consequence near the instruction. |
| 8.1–8.7: punctuation and counts | Examine punctuation and sentence lengths. Treat code, identifiers, and table labels separately from prose sentences. |
| 9.1–9.4: writing practice | Rewrite sentences instead of replacing words mechanically. Use consistent names for software items and operations. |

Examples of project changes:

| Previous wording | Revised wording |
|---|---|
| Preserve development work. | Keep development work. |
| Inspect the diagnostics and saved run log; resolve the issue before rerunning. | Examine the diagnostics and saved log. Correct the problem. Start the updater again. |
| Failed delivery retains the queued report. | If delivery fails, the queue keeps the report. |
| The default branch was not confirmed current. | The updater could not make sure that the default branch is current. |

## Format

The documentation targets Open Knowledge Format v0.2.[^okf]
Concept documents have YAML frontmatter with a nonempty `type`.
The root `index.md` declares the bundle version and lists the documents.
Code, environment examples, unit templates, and the license are not OKF concepts.
The license keeps its standard legal text without added metadata.

## Evidence

| Examination | Result |
|---|---|
| Offline tests | 20 tests passed after the language changes. |
| Python documentation | All Python modules, classes, and functions have docstrings. The offline tests enforce this requirement. |
| Local links | The offline tests resolve the local Markdown links. |
| Compatibility | The source passes Python 3.10 syntax parsing. CI also tests Python 3.10, 3.12, and 3.14. |
| Installed service after this review | The run completed with 82 current repositories, 1 update, 2 exclusions, and no repository errors. |
| Email after this review | SMTP accepted the test message and live report. The delivery queue was empty afterward. |

The service and email evidence above refers to the installed runtime with the revised report text.
CI results remain available in [GitHub Actions](https://github.com/darshchaurasia/devwarden/actions).

## Exact text and limits

These items keep their original forms:

- Git and Python identifiers, commands, file paths, protocol names, and configuration keys.
- Log status markers such as `ERROR`, `SKIP`, and `CURRENT`.
- External Git and SMTP error text, which DevWarden does not author.
- Standard license text and legal terms that require their exact legal meaning.

The test suite does not establish approved word meaning or part of speech for every occurrence.
The review is an agent examination with the stated scope, not a certified language assessment.
A full conformance claim needs evidence beyond sentence counts and a terminology list.
No full conformance claim is made here.
The service has no dependency on AI or on this review process.

[^okf]: Open Knowledge Format v0.2, concept documents and the bundle index.
[^ste]: ASD-STE100 Issue 9, writing rules and dictionary, January 15, 2025.
