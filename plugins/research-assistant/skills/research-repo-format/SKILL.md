---
name: research-repo-format
description: Create, audit, or repair a reproducible research repository and its naming conventions. Use when initializing a project, checking structure, reviewing a commit, renaming literature files, or verifying that raw data and generated files are handled safely.
---

# Research repository conventions

Inspect before changing. Preserve existing work and make additive repairs unless the user explicitly approves a migration.

## Workflow

1. Read `config/research-assistant.json` and the existing `README.md`, `.gitignore`, `dvc.yaml`, and `.dvc` files when present.
2. Preview the standard scaffold with `research-assistant format . --dry-run` when that command is available. Otherwise compare the repository to [references/repository-conventions.md](references/repository-conventions.md).
3. Report three categories: compliant, missing, and conflicting. Do not replace an existing file merely because it differs from the starter.
4. Apply only agreed fixes. Keep raw data immutable, code reusable, generated outputs reproducible, and secrets untracked.
5. Before a commit, inspect `git status --short`, `git diff --cached`, and `git ls-files data/raw`. Raw payloads must not be staged or tracked; DVC pointer files and a remote manifest may be tracked.

Normalize paper filenames to `first-author-year-short-title.pdf` using lowercase ASCII kebab-case. Confirm metadata from the PDF, BibTeX, or trusted notes before renaming. Update matching notes and references in the same change. Do not guess an author or year, and do not perform a bulk rename without showing the mapping first.

When the audit finds valuable local results that exist only on one machine, invoke or recommend `$research-checkpoint`.
