# Embedding providers

Configure embeddings in `config/research-assistant.json`.

## Local default

```json
"embeddings": {
  "provider": "local",
  "model": "BAAI/bge-small-en-v1.5",
  "dimensions": 384
}
```

Requires the `fastembed` Python package. The model is downloaded and cached on first use. Documents use passage embeddings and searches use query embeddings.

## OpenAI

```json
"embeddings": {
  "provider": "openai",
  "model": "text-embedding-3-small",
  "dimensions": 1536
}
```

Requires the `openai` Python package and an `OPENAI_API_KEY` environment variable. API usage may incur charges and sends literature chunks to OpenAI.

## Voyage

```json
"embeddings": {
  "provider": "voyage",
  "model": "voyage-4-lite",
  "dimensions": 1024
}
```

Requires a `VOYAGE_API_KEY` environment variable. API usage may incur charges and sends literature chunks to Voyage. Use this as the hosted alternative for a Claude-oriented workflow; Anthropic does not provide a first-party embedding endpoint.

Changing any provider, model, or dimension requires a complete rebuild because vectors from different embedding spaces are not interchangeable.
