# Repository conventions

Expected layout:

```text
data/{raw,intermediate,final}/
artifacts/{tables,figures}/
literature/{pdfs,notes}/
literature/references.bib
src/
scripts/
tests/
config/research-assistant.json
paper/main.tex
paper/sections/
```

Rules that affect decisions:

- `data/raw/` contains immutable source data and is ignored by Git. A `.gitkeep`, `.dvc` pointer, and `data/raw.remote.json` may be tracked.
- `.research-assistant/`, secrets, virtual environments, caches, and LaTeX build by-products are ignored.
- Put transformations in code and write their results to `data/intermediate/` or `data/final/`.
- Put final tables in `artifacts/tables/` as LaTeX and figures in `artifacts/figures/` as Plotly HTML plus a static LaTeX-compatible export.
- Keep one bibliography at `literature/references.bib` unless the existing project deliberately uses another layout.
- Paper PDFs use `first-author-year-short-title.pdf`; matching notes use the same stem with `.md`.
- Never store credentials, expiring signed URLs, or provider refresh tokens in repository files.
