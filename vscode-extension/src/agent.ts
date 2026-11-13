import { Agent, OpenAIProvider, Runner, tool } from "@openai/agents";
import { z } from "zod";

import { describeResult, formatProject } from "./scaffold";

type AgentOptions = {
  apiKey: string;
  baseUrl?: string;
  model: string;
  projectPath: string;
};

export async function askResearchAgent(
  message: string,
  options: AgentOptions,
): Promise<string> {
  const formatResearchProject = tool({
    name: "format_research_project",
    description:
      "Create the standard maintainable research structure in the current workspace without overwriting existing files.",
    parameters: z.object({
      dryRun: z
        .boolean()
        .default(false)
        .describe("Preview changes without creating files."),
    }),
    execute: async ({ dryRun }) =>
      describeResult(await formatProject(options.projectPath, dryRun)),
  });

  const provider = new OpenAIProvider({
    apiKey: options.apiKey,
    baseURL: options.baseUrl,
    useResponses: !options.baseUrl,
  });
  const runner = new Runner({
    modelProvider: provider,
    tracingDisabled: true,
  });
  const agent = new Agent({
    name: "Research project formatter",
    model: options.model,
    instructions: `You are a concise research project assistant.

You may answer questions about the standard research project structure. You
have exactly one action skill: format_research_project. Call it only when the
user asks to create, organize, initialize, or preview the workspace structure.
The tool is bound to the current VS Code workspace, is additive, and never
overwrites existing files. After using it, summarize the result and remind the
user that existing files were preserved. Never claim to operate elsewhere.`,
    tools: [formatResearchProject],
  });

  const result = await runner.run(agent, message);
  return String(result.finalOutput);
}
