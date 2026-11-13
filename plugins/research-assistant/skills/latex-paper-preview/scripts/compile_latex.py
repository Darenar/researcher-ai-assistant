#!/usr/bin/env python3
"""Compile a research project's main LaTeX document and report JSON."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--main")
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    configured_main = None
    config = root / "config/research-assistant.json"
    if config.is_file():
        try:
            configured_main = json.loads(config.read_text(encoding="utf-8")).get("paper", {}).get("main")
        except (OSError, json.JSONDecodeError, TypeError):
            configured_main = None
    main_file = (root / (args.main or configured_main or "paper/main.tex")).resolve()
    try:
        main_file.relative_to(root)
    except ValueError:
        print(json.dumps({"error": "Main document must be inside the project"}, indent=2))
        return 1
    if not main_file.is_file():
        print(json.dumps({"error": f"Main document not found: {main_file}"}, indent=2))
        return 1
    latexmk = shutil.which("latexmk")
    if not latexmk:
        print(json.dumps({"error": "latexmk is not installed or not on PATH"}, indent=2))
        return 1

    command = [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", main_file.name]
    result = subprocess.run(command, cwd=main_file.parent, capture_output=True, text=True)
    pdf = main_file.with_suffix(".pdf")
    output = (result.stdout + "\n" + result.stderr).strip()
    payload = {
        "success": result.returncode == 0 and pdf.is_file(),
        "main": str(main_file.relative_to(root)),
        "pdf": str(pdf.relative_to(root)) if pdf.is_file() else None,
        "exit_code": result.returncode,
        "log_tail": output.splitlines()[-40:],
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
