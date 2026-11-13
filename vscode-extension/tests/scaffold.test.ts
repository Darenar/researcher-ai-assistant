import assert from "node:assert/strict";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { formatProject } from "../src/scaffold";

async function withTemporaryProject(
  callback: (projectPath: string) => Promise<void>,
): Promise<void> {
  const temporaryDirectory = await mkdtemp(
    path.join(os.tmpdir(), "research-assistant-test-"),
  );
  try {
    await callback(path.join(temporaryDirectory, "project"));
  } finally {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
}

test("creates the expected research structure", async () => {
  await withTemporaryProject(async (projectPath) => {
    const result = await formatProject(projectPath, false);

    assert.ok(result.created.includes("data/raw/"));
    assert.ok(result.created.includes("artifacts/figures/"));
    assert.match(
      await readFile(path.join(projectPath, "paper/main.tex"), "utf8"),
      /Research Paper Title/,
    );
  });
});

test("never overwrites an existing file", async () => {
  await withTemporaryProject(async (projectPath) => {
    await formatProject(projectPath, false);
    const readme = path.join(projectPath, "README.md");
    await writeFile(readme, "My existing research notes", "utf8");

    const result = await formatProject(projectPath, false);

    assert.equal(await readFile(readme, "utf8"), "My existing research notes");
    assert.ok(result.skipped.includes("README.md"));
  });
});

test("dry run does not create files", async () => {
  await withTemporaryProject(async (projectPath) => {
    const result = await formatProject(projectPath, true);

    assert.ok(result.created.includes("paper/main.tex"));
    await assert.rejects(readFile(path.join(projectPath, "paper/main.tex")));
  });
});
