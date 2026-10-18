---
type: Glossary
title: Technical terms
description: Define software terms used in the documentation and code comments.
status: stable
---

# Technical terms

These technical nouns have the meanings below in this project.
Commands and code identifiers keep their exact spelling.

| Term | Meaning |
|---|---|
| branch | A Git reference to a sequence of commits. |
| commit | A recorded Git change. |
| default branch | The branch identified by the remote's symbolic `HEAD`. |
| development branch | A branch other than the remote default branch. |
| fast-forward | A Git update that advances a branch without a merge commit. |
| Git | The version-control program used by the service. |
| GitHub | The repository host supported by discovery. |
| HEAD | The Git reference for the active checkout. |
| LFS | Git Large File Storage. |
| origin | The remote named `origin` in each repository. |
| repository | A directory managed by Git. |
| runtime | The installed application files used by the service. |
| SMTP | The email transport protocol. |
| SSL | The SMTP connection mode with TLS from connection start. |
| staged | Included in the Git index for a future commit. |
| STARTTLS | The command that starts TLS on an SMTP connection. |
| systemd | The Linux service and timer manager. |
| TLS | The protocol that protects SMTP transport. |
| untracked | Present in the checkout but absent from the Git index. |
| worktree | A Git checkout with its own files and index. |
| WSL | Windows Subsystem for Linux. |
| YAML frontmatter | The metadata block at the start of an OKF concept. |

The list supports technical usage. It is not a substitute for a full ASD-STE100 dictionary review.

## Technical nouns for software

These terms identify software items or data. They do not approve the same words as general verbs.

| Term | Meaning in this project |
|---|---|
| application, program | The DevWarden software or a program that it starts. |
| atomic operation | An operation whose result appears as one change to other processes. |
| authentication | The process that establishes an account identity. |
| certificate verification | The TLS checks of the server certificate and host name. |
| checkout | The files and active branch in a Git working directory. |
| CI, test matrix | Continuous integration and its selected Python versions. |
| clone, fork | A local copy of a repository, or a copy hosted by another GitHub account. |
| code review, language review | Examination of source changes or of the language in project text. |
| commit subject, commit body | The first line of a Git commit message and its optional explanation. |
| configuration, settings | Values that select service behavior. |
| credential, token | Data that a service uses to establish identity or access. |
| default | A value or branch that the software selects without a different selection. |
| dependency, submodule | Software that a project needs, or another Git project linked from that project. |
| diagnostic, exit status | Recorded information about an operation and its numerical result. |
| docstring | Documentation inside a Python module, class, or function. |
| environment variable | A named value that a process gives to a child process. |
| hook | A program that Git starts at a specified operation. |
| HTML, Markdown | Formats that the reports and documentation use. |
| index, staged tree | Git records of the files selected for a commit. |
| JSON, metadata | A data format, and descriptive fields about a document or update. |
| lock | A record or mechanism that prevents simultaneous operations. |
| merge, fast-forward | Git operations that combine history or advance a branch to an existing commit. |
| origin URL, remote | The address of the origin repository, and a named external Git repository. |
| outbox, queue | Private storage for reports that await delivery. |
| process, runtime | An operating program, and the installed application files. |
| prompt | A request for input in a terminal. |
| pull request, PR | A proposed repository change submitted through GitHub. |
| run log | Recorded output from one service operation. |
| sparse checkout | A Git checkout that selects only part of the repository file tree. |
| state storage | Private files that record operation results, locks, worktrees, and the email queue. |
| timer, user manager | A systemd schedule, and the systemd manager for one operating-system user. |
| untracked file | A file that is not in the Git index. |

## Technical verbs for software

These verbs have only the stated computer meanings in this project.
The categories follow rule 1.12 for computer input, application processes, and system operations.

| Verb | Meaning |
|---|---|
| clone, fork | Create the related local or hosted Git repository. |
| commit, merge, stash | Perform the named Git operation. |
| configure | Set the application parameters. |
| copy, delete, save | Perform the related operation on computer data. |
| disable, enable | Turn a software function off or on. |
| download, export, fetch, push | Transfer computer data through the named software operation. |
| escape, redact | Encode text characters, or remove supported secret patterns from diagnostic text. |
| install, load, update | Put software files in place, read computer data, or bring software data to the selected version. |
| parse, format, render | Read structured text, build a specified text format, or display formatted text. |
| reset, switch | Perform the named Git operation on a branch or checkout. |
| validate | Examine software input against its specified format or permitted values. |

These are project terminology decisions. They are not a claim that the STE dictionary approves each word for general use.
Commands, API names, and their exact arguments are identifiers.
Legal terms in the license and assignment draft have their legal meanings.
