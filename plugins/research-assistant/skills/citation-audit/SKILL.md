---
name: citation-audit
description: Audit LaTeX citations and BibTeX integrity, then assess whether important manuscript claims are actually supported by cited project literature. Use before review, submission, or after substantial reference changes.
---

# Citation audit

Separate mechanical citation integrity from substantive claim support.

1. Run the deterministic audit:

   ```bash
   python3 "<skill-dir>/scripts/citation_audit.py" --project-root .
   ```

2. Report missing BibTeX keys, unused entries, duplicate DOI values, unreadable files, and citation counts. Fix only when requested.
3. For central empirical or theoretical claims, follow `../literature-rag/SKILL.md`, retrieve the cited paper, and compare the manuscript statement with the source passage.
4. Classify claim support as `supported`, `partially supported`, `contradicted`, or `not verifiable`. Include manuscript location and source/page evidence.

Bibliographic existence does not prove that a citation supports a claim. Never infer support from title or abstract alone when full text is available.
