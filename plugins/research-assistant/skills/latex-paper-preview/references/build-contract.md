# Build contract

- Default main document: `paper/main.tex`.
- Default engine: `latexmk -pdf -interaction=nonstopmode -halt-on-error`.
- Run from the directory containing the main document so relative `\input`, bibliography, and figure paths behave consistently.
- A zero exit code and an existing, newly written PDF are required for success.
- Keep the full log on disk but summarize only actionable errors in chat.
- Respect an existing `.latexmkrc`; do not replace it merely to enforce the default.
- For a project using XeLaTeX or LuaLaTeX, preserve its existing engine configuration.
