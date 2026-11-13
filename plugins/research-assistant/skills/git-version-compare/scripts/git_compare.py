#!/usr/bin/env python3
"""Produce a read-only JSON overview of differences between Git versions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def git(root: Path, *arguments: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Git command failed")
    return result.stdout


def resolve(root: Path, revision: str) -> str:
    return git(root, "rev-parse", "--verify", f"{revision}^{{commit}}").strip()


def commit_info(root: Path, revision: str) -> dict[str, str]:
    output = git(root, "show", "-s", "--format=%H%n%aI%n%an%n%s", revision).splitlines()
    return {
        "commit": output[0],
        "authored_at": output[1],
        "author": output[2],
        "subject": output[3] if len(output) > 3 else "",
    }


def compare(root: Path, base: str, target: str | None, paths: list[str]) -> dict[str, object]:
    repository = Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve()
    base_commit = resolve(repository, base)
    target_commit = resolve(repository, target) if target else None
    diff_arguments = [base_commit]
    if target_commit:
        diff_arguments.append(target_commit)
    if paths:
        diff_arguments.extend(["--", *paths])

    name_status = git(repository, "diff", "--name-status", *diff_arguments)
    numstat = git(repository, "diff", "--numstat", *diff_arguments)
    files: list[dict[str, object]] = []
    numbers: dict[str, tuple[str, str]] = {}
    for line in numstat.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            numbers[parts[2]] = (parts[0], parts[1])
    for line in name_status.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        path = parts[-1]
        added, deleted = numbers.get(path, ("unknown", "unknown"))
        files.append(
            {
                "status": status,
                "path": path,
                "previous_path": parts[1] if status.startswith(("R", "C")) and len(parts) > 2 else None,
                "lines_added": int(added) if added.isdigit() else added,
                "lines_deleted": int(deleted) if deleted.isdigit() else deleted,
            }
        )
    dirty = git(repository, "status", "--porcelain=v1")
    result: dict[str, object] = {
        "repository": str(repository),
        "base": commit_info(repository, base_commit),
        "target": commit_info(repository, target_commit) if target_commit else {"working_tree": True},
        "working_tree_dirty": bool(dirty.strip()),
        "paths": paths,
        "files": files,
        "file_count": len(files),
        "stat": git(repository, "diff", "--stat", *diff_arguments).strip(),
    }
    if not target_commit:
        result["untracked"] = [
            line[3:] for line in dirty.splitlines() if line.startswith("?? ")
        ]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--base", required=True)
    parser.add_argument("--target")
    parser.add_argument("--path", action="append", default=[])
    arguments = parser.parse_args()
    try:
        result = compare(
            Path(arguments.project_root).expanduser().resolve(),
            arguments.base,
            arguments.target,
            arguments.path,
        )
    except Exception as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
