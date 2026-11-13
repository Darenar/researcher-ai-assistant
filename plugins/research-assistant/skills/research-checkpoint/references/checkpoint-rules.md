# Checkpoint decision table

| Observed state | Recommendation |
| --- | --- |
| Raw file hash differs from remote manifest or DVC pointer | Run `$research-data-sync` before commit or cleanup. |
| Raw payload is staged/tracked by Git | Stop the commit and run `$research-data-sync`. |
| Analysis code changed but outputs were not regenerated | Regenerate and validate results before synchronization. |
| Table/figure changed without corresponding source code | Explain the reproducibility gap; do not sync as final. |
| Paper source is newer than the PDF | Run `$latex-paper-preview`. |
| Local paper is ahead of Overleaf | Compile, then offer `$overleaf-sync`. |
| Overleaf is ahead | Offer `$overleaf-sync` before further paper edits. |
| Both sides diverged | Require explicit merge/conflict resolution. |
| Git, data remote, build, and Overleaf are current | Do not produce a synchronization warning. |
