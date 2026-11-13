---
name: literature-embeddings
description: Create, check, incrementally update, or rebuild the persistent semantic embedding index for a research project's literature. Use on first setup, after literature files change, when semantic retrieval is missing or stale, or when changing the embedding provider, model, or dimensions.
---

# Literature Embeddings

Create one project-local semantic index and reuse it across conversations.

## Check before building

1. Resolve `<plugin-root>` as the directory two levels above this skill directory.
2. Run:

   ```bash
   python3 "<plugin-root>/skills/literature-rag/scripts/literature_rag.py" embeddings status --project-root .
   ```

3. If `ready` is true, do not rebuild. If `pending` is positive or `literature_stale` is true, run the incremental build. It hashes sources and embeds only new or changed chunks:

   ```bash
   python3 "<plugin-root>/skills/literature-rag/scripts/literature_rag.py" embeddings build --project-root .
   ```

The disposable index lives at `.research-assistant/literature-index.sqlite3`. Never commit it.

## Set up a provider

The default is the small local model `BAAI/bge-small-en-v1.5`. It needs the `fastembed` Python package and downloads the model on first use. Ask before installing software or downloading model files.

Provider settings live in `config/research-assistant.json`. Read [references/providers.md](references/providers.md) before configuring an alternative provider.

- `local` keeps text on the machine and needs no API key.
- `openai` uses `OPENAI_API_KEY` and defaults to `text-embedding-3-small`.
- `voyage` uses `VOYAGE_API_KEY` and is the supported hosted option for Claude-oriented workflows. Claude itself has no first-party embedding endpoint.

Never put API keys in the project configuration or commit them.

## Change a model safely

Embedding spaces from different providers, models, or dimensions cannot be converted or mixed. After changing configuration, status reports `requires_rebuild`. Recreate all vectors explicitly:

```bash
python3 "<plugin-root>/skills/literature-rag/scripts/literature_rag.py" embeddings build --project-root . --rebuild
```

Do not use `--rebuild` for ordinary literature changes; the regular build is incremental. Report the number created, pending, and whether the final status is ready.
