import * as vscode from "vscode";

import { askResearchAgent } from "./agent";

const API_KEY_SECRET = "researchAssistant.apiKey";

async function configureApiKey(context: vscode.ExtensionContext): Promise<string | undefined> {
  const apiKey = await vscode.window.showInputBox({
    title: "Configure Research Assistant API Key",
    prompt: "The key is stored securely in VS Code Secret Storage.",
    placeHolder: "sk-…",
    password: true,
    ignoreFocusOut: true,
  });
  if (!apiKey?.trim()) {
    return undefined;
  }

  await context.secrets.store(API_KEY_SECRET, apiKey.trim());
  vscode.window.showInformationMessage("Research Assistant API key saved securely.");
  return apiKey.trim();
}

async function chooseWorkspace(): Promise<vscode.WorkspaceFolder | undefined> {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders?.length) {
    vscode.window.showErrorMessage("Open a research project folder first.");
    return undefined;
  }
  if (folders.length === 1) {
    return folders[0];
  }

  const selected = await vscode.window.showQuickPick(
    folders.map((folder) => ({ label: folder.name, folder })),
    { title: "Choose the research project workspace" },
  );
  return selected?.folder;
}

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel("Research Assistant");

  const configure = vscode.commands.registerCommand(
    "researchAssistant.configureApiKey",
    () => configureApiKey(context),
  );
  const clear = vscode.commands.registerCommand(
    "researchAssistant.clearApiKey",
    async () => {
      await context.secrets.delete(API_KEY_SECRET);
      vscode.window.showInformationMessage("Research Assistant API key removed.");
    },
  );
  const ask = vscode.commands.registerCommand("researchAssistant.ask", async () => {
    const workspace = await chooseWorkspace();
    if (!workspace) {
      return;
    }

    const message = await vscode.window.showInputBox({
      title: "Ask Research Assistant",
      prompt: "Ask a question or request a research project structure.",
      placeHolder: "Organize this workspace as a research project",
      ignoreFocusOut: true,
    });
    if (!message?.trim()) {
      return;
    }

    const choice = await vscode.window.showWarningMessage(
      "The agent may create missing files in this workspace if requested.",
      { modal: true },
      "Send Message",
    );
    if (choice !== "Send Message") {
      return;
    }

    const configuration = vscode.workspace.getConfiguration("researchAssistant");
    const baseUrl = configuration.get<string>("baseUrl", "").trim();
    let apiKey = await context.secrets.get(API_KEY_SECRET);
    if (!apiKey && !baseUrl) {
      apiKey = await configureApiKey(context);
    }
    if (!apiKey && !baseUrl) {
      return;
    }

    output.appendLine(`You: ${message.trim()}`);
    output.show(true);

    try {
      const reply = await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Research Assistant is working…",
          cancellable: false,
        },
        () =>
          askResearchAgent(message.trim(), {
            apiKey: apiKey || "not-needed",
            baseUrl: baseUrl || undefined,
            model: configuration.get<string>("model", "gpt-4.1-mini"),
            projectPath: workspace.uri.fsPath,
          }),
      );
      output.appendLine(`Assistant: ${reply}\n`);
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      output.appendLine(`Error: ${detail}\n`);
      vscode.window.showErrorMessage(`Research Assistant: ${detail}`);
    }
  });

  context.subscriptions.push(output, configure, clear, ask);
}

export function deactivate(): void {}
