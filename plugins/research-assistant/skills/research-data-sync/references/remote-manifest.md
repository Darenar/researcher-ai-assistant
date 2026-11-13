# Remote manifest

Track `data/raw.remote.json` after a successful synchronization:

```json
{
  "schema_version": 1,
  "provider": "google-drive",
  "remote_folder_id": "stable-provider-folder-id",
  "remote_folder_url": "stable-provider-folder-url",
  "dvc_remote": null,
  "synced_at": "2026-11-13T00:00:00Z",
  "files": [
    {
      "path": "data/raw/example.csv",
      "sha256": "...",
      "size": 123,
      "remote_file_id": "stable-provider-file-id"
    }
  ]
}
```

Use `google-drive` or `dropbox` for provider names. Sort entries by path. Never record access tokens, refresh tokens, cookies, local absolute paths, or short-lived signed URLs. A DVC-only project may set provider fields to `null` and record the configured DVC remote name.
