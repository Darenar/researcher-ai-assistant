---
name: research-checkpoint
description: Detect unsynchronized research work and recommend the exact checkpoint needed. Use after meaningful changes to raw data, derived results, literature, tables, figures, or paper text; before commits; and before ending work when results may exist only locally.
---

# Research checkpoint

Inspect state before recommending synchronization. Avoid generic reminders when everything is already safe.

1. Inspect `git status --short` and the current branch/upstream divergence.
2. Check whether `data/raw/` changed since `data/raw.remote.json` or the relevant DVC pointer/lock file.
3. Check whether generated tables or figures are newer than their committed state and whether their generating code is present.
4. Check whether paper sources changed since the last successful PDF build.
5. When an `overleaf` remote exists, fetch only when authorized and compare local and remote paper history.

Recommend synchronization when any meaningful result exists only locally, a remote manifest/hash is stale, a DVC push is outstanding, Overleaf is ahead/behind, or the paper has not been rebuilt. State exactly what is unsynchronized and which command or skill should handle it.

Never upload, share, push, pull, commit, or overwrite merely because synchronization is recommended. Obtain the applicable approval at the point of the external write or consequential Git operation. Read [references/checkpoint-rules.md](references/checkpoint-rules.md) for the decision table.
