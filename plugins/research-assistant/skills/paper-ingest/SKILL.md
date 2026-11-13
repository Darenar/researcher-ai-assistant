---
name: paper-ingest
description: Import research papers into the active project with verified metadata, conventional filenames, BibTeX records, duplicate checks, and semantic-index updates. Use when adding PDFs or normalizing newly collected literature.
---

# Paper ingest

Add papers without losing provenance or silently accepting incorrect metadata.

1. Resolve the project root and the files the user intends to import. Never scan unrelated personal folders.
2. Resolve `<skill-dir>` as this skill directory and plan the import before changing files:

   ```bash
   python3 "<skill-dir>/scripts/paper_ingest.py" --project-root . FILE [FILE ...]
   ```

3. Review detected DOI, title, authors, year, BibTeX key, duplicate status, and proposed destination. Treat missing or ambiguous metadata as requiring manual confirmation.
4. Renaming or moving source files and changing the bibliography require user authorization. After approval, repeat with `--apply`.
5. Follow `../literature-embeddings/SKILL.md` to incrementally update the index after successful imports.

The script uses Crossref only when it finds a DOI. It never invents missing metadata. Read [references/ingest-contract.md](references/ingest-contract.md) when changing naming or metadata behavior.
