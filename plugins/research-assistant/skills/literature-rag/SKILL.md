---
name: literature-rag
description: Search and synthesize evidence from the active research project's literature folder. Use for literature questions, evidence comparisons, related-work summaries, research-gap analysis, or any answer that should be grounded in local papers and notes.
---

# Literature retrieval

Ground answers in the active project, never in another project's index.

## Retrieve evidence

1. Resolve the project root from the active workspace. Use `config/research-assistant.json` when present; otherwise search `literature/pdfs`, `literature/notes`, then `literature`.
2. Resolve `<skill-dir>` as the directory containing this `SKILL.md`. Check semantic-index health before searching:

   ```bash
   python3 "<skill-dir>/scripts/literature_rag.py" embeddings status --project-root .
   ```

   If it is not ready, use `$literature-embeddings` to create or incrementally update it. The index is a disposable local cache at `.research-assistant/literature-index.sqlite3`; never commit it.
3. Use hybrid retrieval by default. It combines semantic similarity with exact-term full-text matching:

   ```bash
   python3 "<skill-dir>/scripts/literature_rag.py" search --project-root . --query "..." --limit 8 --mode hybrid
   ```

   Use `--mode semantic` for conceptual similarity or `--mode lexical` when exact wording, identifiers, or names matter. Lexical mode remains available if an embedding provider is temporarily unavailable.

4. Prefer passages supported by more than one source. Open the original source when a claim is central, ambiguous, or surprising.
5. Answer with citations copied from the retrieval result. Preserve page numbers when available. Clearly label synthesis or inference rather than attributing it to a paper.

If PDF extraction is unavailable or a file produced no text, report the coverage gap instead of pretending the search was exhaustive. Do not upload literature or create a hosted index unless the user explicitly requests it.

Read [references/retrieval-contract.md](references/retrieval-contract.md) when changing the indexer, interpreting its JSON, or evaluating retrieval quality.
