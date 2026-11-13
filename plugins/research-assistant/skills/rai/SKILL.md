---
name: rai
description: Route an explicitly invoked Research AI Assistant request to the appropriate research-project workflow. Use when the user invokes $rai for literature retrieval, semantic embeddings, repository conventions, research data, LaTeX, Overleaf, tables, figures, or synchronization checks.
---

# Research AI Assistant

Act as the single front door for the Research AI Assistant plugin.

## Route the request

Resolve `<skills-dir>` as the parent directory containing this skill and the sibling skills below. Read and follow only the sibling `SKILL.md` files needed for the request:

- Literature questions, evidence synthesis, related work, or cited search: `literature-rag/SKILL.md`.
- Create, check, update, or change the semantic index: `literature-embeddings/SKILL.md`.
- Import PDFs, verify metadata, normalize names, or add BibTeX: `paper-ingest/SKILL.md`.
- Extract comparable study methods, outcomes, and findings: `evidence-matrix/SKILL.md`.
- Check citation keys, bibliography integrity, or claim support: `citation-audit/SKILL.md`.
- Manage a formal systematic or scoping review: `systematic-review/SKILL.md`.
- Draft a thematic review from semantically similar papers: `literature-review/SKILL.md`.
- Compare commits, branches, tags, or the working tree: `git-version-compare/SKILL.md`.
- Trace data and code to reported results: `reproducibility-audit/SKILL.md`.
- Critically review manuscript logic, reporting, and conclusions: `manuscript-review/SKILL.md`.
- Audit code, results, evidence, and prose together: `research-reviewer/SKILL.md`.
- Record decisions, progress, assumptions, and open questions: `research-log/SKILL.md`.
- Repository structure, naming, or convention audits: `research-repo-format/SKILL.md`.
- Raw-data storage, DVC, Google Drive, Dropbox, or Git exclusions: `research-data-sync/SKILL.md`.
- Compile or preview a LaTeX paper: `latex-paper-preview/SKILL.md`.
- Pull, push, or configure Overleaf Git synchronization: `overleaf-sync/SKILL.md`.
- LaTeX tables or Plotly figures: `research-results-style/SKILL.md`.
- Decide whether work should be committed, pushed, or synchronized: `research-checkpoint/SKILL.md`.

For literature retrieval or review writing, check the semantic index as required by `literature-rag`. If setup or repair is needed, follow `literature-embeddings` first and then continue the original request. After importing papers, update embeddings incrementally.

For requests spanning several workflows, use the smallest necessary sequence and keep one coherent response. Do not merely tell the user which skill to invoke; perform the routed workflow. Preserve each specialist skill's safety checks and authorization boundaries.
