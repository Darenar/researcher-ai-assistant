# Output contract

For every generated table or figure, preserve:

- The source dataset or deterministic upstream artifact.
- The exact code entry point that generated it.
- A stable output filename referenced by LaTeX.
- Units, transformations, filters, sample size, and uncertainty definition.
- A regeneration path that does not require manual editing.

Table requirements:

- Valid LaTeX tabular output with escaped text.
- `booktabs` rules rather than vertical lines.
- Machine-generated numeric precision chosen deliberately and consistently.

Figure requirements:

- Plotly source figure.
- Interactive `.html` for exploration.
- Static `.pdf`, `.svg`, or high-resolution `.png` for LaTeX.
- No Matplotlib or Seaborn dependency for new output code.
