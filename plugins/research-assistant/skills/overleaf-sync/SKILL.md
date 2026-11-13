---
name: overleaf-sync
description: Configure and synchronize a research paper with Overleaf through Git. Use when linking an Overleaf project, fetching collaborator changes, pushing compiled local paper changes, checking divergence, or resolving a safe two-way synchronization workflow.
---

# Overleaf synchronization

Use Overleaf as a Git remote named `overleaf`. Git integration requires an eligible Overleaf plan and token-based authentication. Never store the token in the repository or print it.

## Setup

Read [references/overleaf-git.md](references/overleaf-git.md) before initial setup or conflict handling. Obtain the exact Git URL from the project's Overleaf Integrations menu. Do not infer it. Inspect the repository layout and preserve an existing monorepo, subtree, or dedicated-paper-repository design; do not restructure automatically.

## Synchronize

1. Require a clean or intentionally staged working tree before integration.
2. Run `git fetch overleaf` and inspect branches and divergence before merging or pushing.
3. If only Overleaf is ahead, pull its changes through the configured integration and show the resulting diff.
4. If only local is ahead, compile the paper first, then request confirmation before pushing to Overleaf.
5. If both sides changed, stop and present the conflicting commits/files. Resolve explicitly; never force-push or discard either side.
6. Compile again after a merge and report the resulting PDF.

Overleaf's Git and GitHub synchronization are not continuously automatic. This skill should make synchronization timely and low-friction, but it must not claim background synchronization occurred. Recommend `$research-checkpoint` after meaningful paper edits or before ending a session.
