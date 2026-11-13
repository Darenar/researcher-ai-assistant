---
name: evidence-matrix
description: Build or update an auditable structured evidence matrix from project literature. Use when comparing studies, extracting methods and findings, preparing synthesis, or recording evidence with source and page provenance.
---

# Evidence matrix

Store reusable evidence, not just conversational summaries.

1. Define the review question and extraction fields before extracting. Use the default schema in [references/schema.md](references/schema.md) unless the project needs domain-specific fields.
2. Follow `../literature-rag/SKILL.md` to retrieve relevant passages. Open original sources for central or ambiguous claims.
3. Create the matrix when missing:

   ```bash
   python3 "<skill-dir>/scripts/evidence_matrix.py" init --path research/evidence-matrix.csv
   ```

4. Add one row per study-outcome combination. Use `not reported` rather than guessing. Every substantive finding must include a project-relative source and page when available.
5. Validate before synthesis:

   ```bash
   python3 "<skill-dir>/scripts/evidence_matrix.py" validate --path research/evidence-matrix.csv --project-root .
   ```

Preserve existing human decisions and columns. Do not overwrite the matrix wholesale unless explicitly requested.
