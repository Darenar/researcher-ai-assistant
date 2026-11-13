---
name: research-data-sync
description: Keep raw research files outside Git while preserving reproducible pointers and restore information. Use for Google Drive or Dropbox uploads, DVC setup, raw-data restoration, remote manifests, pre-commit raw-data checks, or synchronization of research datasets.
---

# Raw-data synchronization

Treat `data/raw/` as immutable payload storage. Git stores pointers and metadata, not the payloads.

## Choose the storage path

- Prefer DVC when the project requires reproducible versions and pull/push semantics.
- Use a connected Google Drive or Dropbox integration when the user wants provider-native folders or share links.
- The provider is a project choice. Read `config/research-assistant.json`; if it is unset, ask before creating a remote or uploading.

## Synchronize safely

1. Inspect `git ls-files data/raw` and `git status --short data/raw`. Stop if raw payloads are tracked or staged. Propose removing them from the Git index without deleting local files; require confirmation before changing the index.
2. Compute or obtain stable content hashes before upload.
3. Immediately before an external upload, share-link creation, deletion, or overwrite, summarize the provider, target folder, files, and visibility and obtain the required approval.
4. Upload through the connected provider or run the agreed DVC operation. Never place credentials in commands, repository files, or output.
5. Update `data/raw.remote.json` only after the remote operation succeeds. Store stable provider IDs/links and hashes, not expiring download URLs. Follow [references/remote-manifest.md](references/remote-manifest.md).
6. Verify restoration using `dvc pull` or a provider download into a temporary location before replacing anything local.

For DVC, track `.dvc` pointer files, `dvc.yaml`, `dvc.lock`, and non-secret remote configuration. Do not commit `.dvc/cache/` or provider credentials.

If Google Drive or Dropbox is not connected, explain that connection is required for provider operations and continue with local checks. Do not substitute an unrequested storage provider.
