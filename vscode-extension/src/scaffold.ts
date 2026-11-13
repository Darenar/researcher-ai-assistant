import { constants } from "node:fs";
import { access, mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

import { PROJECT_DIRECTORIES, PROJECT_FILES } from "./templates";

export type ScaffoldResult = {
  root: string;
  created: string[];
  skipped: string[];
  dryRun: boolean;
};

async function exists(filePath: string): Promise<boolean> {
  try {
    await access(filePath, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

export async function formatProject(
  root: string,
  dryRun: boolean,
): Promise<ScaffoldResult> {
  const result: ScaffoldResult = { root, created: [], skipped: [], dryRun };

  for (const relativePath of PROJECT_DIRECTORIES) {
    const destination = path.join(root, relativePath);
    if (await exists(destination)) {
      result.skipped.push(`${relativePath}/`);
    } else {
      result.created.push(`${relativePath}/`);
      if (!dryRun) {
        await mkdir(destination, { recursive: true });
      }
    }
  }

  for (const [relativePath, content] of Object.entries(PROJECT_FILES)) {
    const destination = path.join(root, relativePath);
    if (await exists(destination)) {
      result.skipped.push(relativePath);
      continue;
    }

    result.created.push(relativePath);
    if (!dryRun) {
      await mkdir(path.dirname(destination), { recursive: true });
      await writeFile(destination, content, { encoding: "utf8", flag: "wx" });
    }
  }

  return result;
}

export function describeResult(result: ScaffoldResult): string {
  const action = result.dryRun ? "Would create" : "Created";
  return [
    `Research project: ${result.root}`,
    `${action}: ${result.created.length}`,
    ...result.created.map((item) => `  + ${item}`),
    `Skipped existing: ${result.skipped.length}`,
    ...result.skipped.map((item) => `  = ${item}`),
  ].join("\n");
}
