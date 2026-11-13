---
name: latex-paper-preview
description: Edit, compile, diagnose, and preview the project's LaTeX paper. Use after changing paper text, citations, tables, figures, or LaTeX configuration, and whenever the user asks to build or view the manuscript in VS Code.
---

# LaTeX paper and preview

Treat a successful PDF build as the verification step for paper changes.

1. Resolve the main file from `config/research-assistant.json`, falling back to `paper/main.tex`.
2. Make the requested source changes. Keep generated tables and static figure exports outside hand-written section files and include them with `\input` or `\includegraphics`.
3. Resolve `<skill-dir>` as the directory containing this `SKILL.md`, then compile with:

   ```bash
   python3 "<skill-dir>/scripts/compile_latex.py" --project-root .
   ```

4. On failure, report the first actionable LaTeX error with its file and line, then fix and rebuild when the requested task includes implementation.
5. On success, give the PDF path. In VS Code, prefer the LaTeX Workshop PDF viewer when installed; otherwise open the generated PDF as a normal editor file.

Do not commit auxiliary files or `paper/main.pdf` unless the project explicitly tracks release artifacts. If a paper change is ready but not reflected in Overleaf, invoke or recommend `$research-checkpoint`.

Read [references/build-contract.md](references/build-contract.md) when changing build configuration or diagnosing a nonstandard project.
