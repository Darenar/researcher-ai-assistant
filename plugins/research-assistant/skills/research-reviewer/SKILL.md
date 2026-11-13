---
name: research-reviewer
description: Perform a critical, domain-agnostic audit across research code, data lineage, results, manuscript text, citations, and internal consistency. Use when the user asks whether the overall project is correct, suspicious, inconsistent, or ready for independent review.
---

# Research reviewer

Act independently of the implementation author and look for evidence that could falsify the project's conclusions.

1. Agree on scope when a full audit would be unbounded. Otherwise sample the highest-risk claims and result-producing paths first.
2. Read [references/review-rubric.md](references/review-rubric.md). Use sibling skills as focused procedures:
   - `../reproducibility-audit/SKILL.md` for code, environments, data-to-result lineage, and regenerated outputs.
   - `../manuscript-review/SKILL.md` for logic, reporting, and internal prose consistency.
   - `../citation-audit/SKILL.md` for reference integrity and claim support.
   - `../git-version-compare/SKILL.md` when a regression or unexplained change may be version-specific.
3. Test claims against code and artifacts. Check units, joins, filters, denominators, missing-data handling, statistical assumptions, leakage, seeds, and mismatches between displayed and computed values when applicable.
4. Report findings first, ordered by severity. Each finding needs a location, evidence, consequence, and a reproducible check or corrective action.

Do not modify code or prose during an audit unless the user separately asks for fixes. Clearly separate confirmed defects, credible risks, and unverified questions.
