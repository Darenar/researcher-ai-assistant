# Research AI Assistant

Research AI Assistant helps you create a clear, maintainable academic research
project directly from VS Code.

Ask it to organize the open workspace and it creates missing folders for raw,
intermediate, and final data; tables and figures; literature; reusable code;
tests; configuration; and a LaTeX paper. It never replaces an existing file.

## Features

- Natural-language messages from the VS Code Command Palette.
- One focused action: format the open workspace as a research project.
- Safe, additive file creation with a preview option.
- A ready-to-edit LaTeX manuscript and BibTeX bibliography.
- API keys stored in VS Code Secret Storage, not workspace settings.
- OpenAI and OpenAI-compatible hosted or local model endpoints.
- No separate Python installation and no extension telemetry.

## Get started

1. Open the folder containing your research project.
2. Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`).
3. Run **Research Assistant: Configure API Key**.
4. Run **Research Assistant: Ask About This Project**.
5. Enter a message such as:

   `Organize this workspace as a research project.`

Replies appear in the **Research Assistant** output panel. The extension asks
for confirmation before sending a message because formatting requests can
create files in the workspace.

## Generated project structure

```text
project/
├── data/{raw,intermediate,final}/
├── artifacts/{tables,figures}/
├── literature/{pdfs,notes}/
├── literature/references.bib
├── src/
├── scripts/
├── tests/
├── config/
└── paper/
    ├── main.tex
    └── sections/
```

## Model settings

The default model is `gpt-4.1-mini`. Change **Research Assistant: Model** in
VS Code Settings to use another model available to your account.

To use an OpenAI-compatible server such as Ollama, LM Studio, vLLM, or another
provider:

1. Set **Research Assistant: Base URL** to its API URL, such as
   `http://localhost:11434/v1`.
2. Set **Research Assistant: Model** to the server's model name.
3. Configure an API key only if that server requires one.

The selected model must support Chat Completions tool calling.

## Privacy and safety

- The API key is stored using VS Code Secret Storage.
- Messages are sent only to the configured model provider.
- OpenAI Agents SDK tracing is disabled by this extension.
- Formatting is limited to the selected open workspace.
- Existing files are skipped and never overwritten.

## Development

```bash
npm install
npm run check
npm test
npm run build
```

Press `F5` in this folder to start an Extension Development Host.

To build an installable package:

```bash
npm run package
```

See [PUBLISHING.md](PUBLISHING.md) for the one-time Marketplace setup and
release steps.

## License

MIT
