"""Files placed in every newly formatted research project."""

PROJECT_DIRECTORIES = (
    "data/raw",
    "data/intermediate",
    "data/final",
    "artifacts/tables",
    "artifacts/figures",
    "literature/pdfs",
    "literature/notes",
    "src",
    "scripts",
    "tests",
    "config",
    "paper/sections",
)

PROJECT_README = """# Research project

## Folder guide

- `data/raw/`: original source data. Treat these files as immutable.
- `data/intermediate/`: cleaned or partially transformed data.
- `data/final/`: analysis-ready datasets.
- `artifacts/tables/`: final generated tables.
- `artifacts/figures/`: final generated figures.
- `literature/pdfs/`: papers and source documents.
- `literature/notes/`: reading notes, named to match their source.
- `literature/references.bib`: the single BibTeX bibliography.
- `src/`: reusable analysis functions and modules.
- `scripts/`: small entry points that run analyses.
- `tests/`: tests for code in `src/`.
- `config/`: non-secret settings needed to reproduce the work.
- `paper/`: the LaTeX manuscript.

## Working rules

1. Never edit raw data. Create a derived file in `data/intermediate/`.
2. Keep reusable logic in `src/`; keep scripts short.
3. Generate tables and figures with code whenever possible.
4. Add every cited work to `literature/references.bib`.
5. Do not commit secrets, raw data, or generated LaTeX build files.

## Build the paper

From this project directory, run:

```bash
cd paper
latexmk -pdf main.tex
```
"""

PROJECT_GITIGNORE = """# Secrets and local environment
.env
.venv/
__pycache__/
*.py[cod]

# Data is normally stored outside Git. Keep the folder placeholders.
data/raw/*
!data/raw/.gitkeep

# LaTeX build files
paper/*.aux
paper/*.bbl
paper/*.bcf
paper/*.blg
paper/*.fdb_latexmk
paper/*.fls
paper/*.log
paper/*.out
paper/*.run.xml
paper/*.synctex.gz
paper/*.toc
paper/main.pdf
"""

REFERENCES_BIB = """% Keep all project references in this file.
% Example:
% @article{author2026shortname,
%   author  = {Family Name, Given Name},
%   title   = {Article title},
%   journal = {Journal Name},
%   year    = {2026}
% }
"""

MAIN_TEX = r"""\documentclass[11pt]{article}

\usepackage[margin=1in]{geometry}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage[hidelinks]{hyperref}
\usepackage{natbib}

\title{Research Paper Title}
\author{Author Name}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
Write a concise summary of the question, method, results, and conclusion.
\end{abstract}

\input{sections/introduction}
\input{sections/methods}
\input{sections/results}
\input{sections/discussion}

\bibliographystyle{plainnat}
\bibliography{../literature/references}

\end{document}
"""

SECTION_FILES = {
    "paper/sections/introduction.tex": "\\section{Introduction}\n\nState the research question and its importance.\n",
    "paper/sections/methods.tex": "\\section{Methods}\n\nDescribe the data and analysis so the work can be reproduced.\n",
    "paper/sections/results.tex": "\\section{Results}\n\nReport the findings and refer to generated tables and figures.\n",
    "paper/sections/discussion.tex": "\\section{Discussion}\n\nInterpret the results, limitations, and implications.\n",
}

PROJECT_FILES = {
    "README.md": PROJECT_README,
    ".gitignore": PROJECT_GITIGNORE,
    "data/raw/.gitkeep": "",
    "data/intermediate/.gitkeep": "",
    "data/final/.gitkeep": "",
    "artifacts/tables/.gitkeep": "",
    "artifacts/figures/.gitkeep": "",
    "literature/pdfs/.gitkeep": "",
    "literature/notes/.gitkeep": "",
    "literature/references.bib": REFERENCES_BIB,
    "src/.gitkeep": "",
    "scripts/.gitkeep": "",
    "tests/.gitkeep": "",
    "config/.gitkeep": "",
    "paper/main.tex": MAIN_TEX,
    **SECTION_FILES,
}

