---
name: git-version-compare
description: Compare research code, manuscript text, results, and repository structure between Git commits, branches, tags, or the working tree. Use when explaining what changed, why outputs differ, or whether a later version introduced inconsistencies.
---

# Git version comparison

Perform a read-only, research-aware comparison.

1. Confirm the base and target. Default to the user's named revisions; if only one is named, compare it with the working tree.
2. Generate a machine-readable overview:

   ```bash
   python3 "<skill-dir>/scripts/git_compare.py" --project-root . --base BASE --target TARGET
   ```

   Omit `--target` to compare the base with the working tree. Add `--path PATH` to narrow scope.
3. Inspect relevant diffs directly with Git. Explain changes by effect: research question, data processing, statistical method, result values, tables/figures, claims, citations, or formatting.
4. Trace changed generated outputs back to code and data pointers when possible. Do not claim causation from file proximity alone.
5. Report revision IDs, dirty-working-tree state, changed files, substantive differences, and anything that cannot be compared because data or artifacts are unavailable.

Never check out, reset, clean, or rewrite history as part of a comparison.
