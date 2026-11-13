# Overleaf Git workflow

Overleaf exposes a project-specific Git URL through Integrations. Its Git integration is a premium feature and uses token-based authentication.

Safety invariants:

- Use the exact remote URL supplied by Overleaf and the remote name `overleaf`.
- Discover the remote default branch after fetching; do not assume `main` or `master`.
- Never put a token in a remote URL committed to configuration, a script, or chat output.
- Never use `--force`, reset, or an ours/theirs merge strategy as an automatic conflict fix.
- Overleaf does not support Git LFS or nested submodules inside the Overleaf project.
- GitHub synchronization in the Overleaf UI is manual, not continuous.
- Pull collaborator changes before pushing local paper edits. Compile after every merge.

Repository shapes:

- A dedicated paper repository is simplest for new projects.
- A monorepo may synchronize the whole repository if it stays within Overleaf limits and raw data is excluded.
- A subtree or submodule design can isolate `paper/`, but migrating an existing repository requires an explicit plan and user approval.
