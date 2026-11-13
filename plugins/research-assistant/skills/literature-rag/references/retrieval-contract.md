# Retrieval contract

The indexer searches only configured roots inside the resolved project. Its JSON search results contain:

- `path`: project-relative source path.
- `page`: one-based PDF page when available; otherwise `null`.
- `chunk`: zero-based chunk number within that page or text file.
- `text`: retrieved source text.
- `score`: hybrid reciprocal-rank score when hybrid search is used.
- `semantic_score`: cosine similarity when semantic search contributes the result.
- `lexical_score`: FTS relevance when lexical search contributes the result.
- `citation`: stable human-readable citation assembled from path and page.

Quality requirements:

- Index changes incrementally using content hashes; deleted sources must disappear.
- Keep chunks within a single PDF page so page citations remain valid.
- Treat notes as secondary commentary unless the note clearly quotes or links a primary source.
- Hybrid retrieval combines semantic similarity and lexical full-text ranking. Semantic-only and lexical-only modes remain available.
- Build embeddings incrementally. A provider, model, or dimension change requires a deliberate complete rebuild.
- Never infer that a low-scoring or absent result proves the literature contains no evidence.
