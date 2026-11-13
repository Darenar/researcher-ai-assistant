# Research AI Assistant

A small, installable AI agent with one job: prepare a folder as a clear,
maintainable research project.

It uses the OpenAI Agents SDK and creates this structure without deleting or
overwriting anything already present:

```text
project/
├── data/
│   ├── raw/              # Original, immutable input data
│   ├── intermediate/     # Temporary and cleaned data
│   └── final/            # Analysis-ready datasets
├── artifacts/
│   ├── tables/           # Final tables used in reports or papers
│   └── figures/          # Final figures used in reports or papers
├── literature/
│   ├── pdfs/             # Papers and other source documents
│   ├── notes/            # Reading notes
│   └── references.bib    # BibTeX references
├── src/                  # Reusable analysis code
├── scripts/              # Small runnable workflows
├── tests/                # Tests for analysis code
├── paper/
│   ├── sections/         # LaTeX sections
│   └── main.tex          # Main paper document
├── config/               # Non-secret configuration
└── README.md             # Project-specific guide
```

## Install

Python 3.10 or newer is required. Install once with
[uv](https://docs.astral.sh/uv/):

```bash
uv tool install /path/to/researcher-ai-assistant
```

During development, run it without installing globally:

```bash
uv run research-assistant --help
```

## Configure a model

For OpenAI, set an API key. The model is optional and can be changed:

```bash
export OPENAI_API_KEY="your-api-key"
export RESEARCH_ASSISTANT_MODEL="gpt-4.1-mini"
```

For an OpenAI-compatible local or hosted model, also set its base URL. For
example, an Ollama server exposing its OpenAI-compatible endpoint can use:

```bash
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="not-needed"
export RESEARCH_ASSISTANT_MODEL="your-local-model"
```

The exact URL and model name come from the server or provider you use.

## Use

Format the current folder:

```bash
cd /path/to/my-research
research-assistant format .
```

Or provide another folder, including one that does not exist yet:

```bash
research-assistant format /path/to/new-research-project
```

Preview the files without creating them:

```bash
research-assistant format /path/to/project --dry-run
```

You can also send a natural-language message:

```bash
research-assistant chat "Explain where my final figures should go" --path .
research-assistant chat "Organize this workspace as a research project" --path .
```

The formatter is additive: existing files are reported as skipped and are
never replaced. Raw data is also excluded by the generated `.gitignore` so it
is not accidentally committed.

## Use from VS Code

A self-contained extension is included in `vscode-extension/`. It bundles the
TypeScript OpenAI Agents SDK implementation, so Marketplace users do not need
Python or `uv`. It adds **Research Assistant: Ask About This Project** to the
Command Palette and stores API keys using VS Code Secret Storage.

To try it during development:

1. Run `npm install` inside `vscode-extension/`.
2. Open the `vscode-extension/` folder in VS Code.
3. Press `F5` to open an Extension Development Host.
4. In that window, open a research folder.
5. Configure an API key, then run **Research Assistant: Ask About This
   Project**.

The extension asks for confirmation before sending each message because the
agent may create missing project files when requested. See
`vscode-extension/PUBLISHING.md` for the Marketplace release checklist.

## Use as a Codex plugin

The portable plugin in `plugins/research-assistant/` keeps Codex as the chat
and agent while adding focused research workflows:

- project-local hybrid semantic and full-text literature retrieval with file and page citations;
- verified paper ingest, conventional filenames, BibTeX records, and incremental re-indexing;
- structured evidence matrices, systematic-review records, and literature-review drafting;
- mechanical citation audits and source-to-claim verification;
- Git-version comparison and data-to-result reproducibility audits;
- independent critical review across code, results, citations, and manuscript text;
- a durable research decision and progress log;
- repository and paper naming conventions;
- raw-data pointers, DVC, Google Drive, and Dropbox synchronization guidance;
- LaTeX compilation and preview;
- safe Overleaf Git synchronization;
- LaTeX tables and Plotly figures; and
- evidence-based synchronization reminders.

Invoke `$rai` in Codex as the single explicit entry point. It routes the request
to the relevant specialist skill, so commands such as `$rai search my
literature`, `$rai compile my paper`, and `$rai check synchronization` all use
the same chat interface.

Additional direct entry points include `$paper-ingest`, `$evidence-matrix`,
`$citation-audit`, `$systematic-review`, `$literature-review`,
`$git-version-compare`, `$reproducibility-audit`, `$manuscript-review`,
`$research-reviewer`, and `$research-log`. These remain available individually
while `$rai` provides the simpler default interface.

The literature index is local to each project under `.research-assistant/` and
is never committed. The default semantic provider is the small local
`BAAI/bge-small-en-v1.5` model through FastEmbed, so it does not need an API
key; the model is downloaded once on first use. OpenAI (`text-embedding-3-small`)
and Voyage (`voyage-4-lite`) can be selected in
`config/research-assistant.json`. Changing models requires rebuilding the
vectors because different embedding spaces cannot be converted or mixed. PDF
indexing requires either the Python `pypdf` package or the `pdftotext` command.
For the default local setup, install `fastembed` in the Python environment that
Codex uses to run the skill; the embeddings skill checks this before building.

The `plugins/` directory is a local marketplace. Register and install it with:

```bash
codex plugin marketplace add ./plugins
codex plugin add research-assistant@research-assistant-local
```

Restart the ChatGPT desktop app after local plugin changes when testing there.

## Develop and test

```bash
uv sync --extra dev
uv run pytest
```

The code is deliberately small. `agent.py` defines the single agent skill,
`scaffold.py` performs safe filesystem changes, `provider.py` selects the
model connection, and `cli.py` provides the command.

