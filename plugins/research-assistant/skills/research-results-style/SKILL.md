---
name: research-results-style
description: Create or review publication results using LaTeX tables and Plotly figures. Use for analysis outputs, manuscript tables, charts, figure exports, or audits that should prevent Matplotlib/Seaborn output and keep results reproducible.
---

# Publication results

Follow existing analysis architecture while enforcing these output contracts for new work.

## Tables

- Generate final tables as `.tex` under `artifacts/tables/` using `booktabs` conventions.
- Keep values derived from code; do not hand-copy computed results into the manuscript.
- Include the table from the paper with `\input{../artifacts/tables/<name>.tex}` or the project's established equivalent.
- Put captions, labels, units, sample sizes, and uncertainty definitions in the generated table or its stable wrapper.

## Figures

- Use Plotly for figures. When in-scope code uses Matplotlib, Seaborn, or another plotting library, propose or perform a Plotly migration as the task permits. Keep the old library only when the user explicitly chooses it or a required pipeline cannot reasonably be migrated, and disclose that exception.
- Save interactive HTML to `artifacts/figures/<name>.html` and a deterministic static PDF, SVG, or high-resolution PNG for LaTeX. Plotly static export normally requires Kaleido.
- Keep figure-generating code in `src/` or `scripts/`; never treat an edited image as the source of truth.
- Use stable colors, explicit axis labels and units, accessible contrast, and a fixed ordering for categorical data.

Read [references/output-contract.md](references/output-contract.md) when implementing or auditing generated outputs. Compile the paper with `$latex-paper-preview` after changing included results.
