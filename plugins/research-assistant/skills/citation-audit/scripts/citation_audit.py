#!/usr/bin/env python3
"""Audit LaTeX citation keys against project BibTeX files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


CITE_RE = re.compile(
    r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|autocite|parencite|textcite|footcite|nocite)"
    r"(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]*)\}",
    re.IGNORECASE,
)
ENTRY_START_RE = re.compile(r"@(?!comment\b|string\b|preamble\b)[A-Za-z]+\s*[({]\s*([^,\s]+)\s*,", re.IGNORECASE)
DOI_RE = re.compile(r"\bdoi\s*=\s*[\{\"]([^}\"]+)", re.IGNORECASE)
IGNORED_PARTS = {".git", ".research-assistant", ".venv", "node_modules", ".test-dist"}


def project_files(root: Path, suffix: str) -> list[Path]:
    return sorted(
        path
        for path in root.rglob(f"*{suffix}")
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
    )


def bib_entries(text: str) -> list[tuple[str, str]]:
    starts = list(ENTRY_START_RE.finditer(text))
    entries: list[tuple[str, str]] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        entries.append((match.group(1).strip(), text[match.start() : end]))
    return entries


def audit(project_root: Path) -> dict[str, object]:
    tex_files = project_files(project_root, ".tex")
    bib_files = project_files(project_root, ".bib")
    citations: dict[str, list[str]] = defaultdict(list)
    entries: dict[str, list[str]] = defaultdict(list)
    dois: dict[str, list[str]] = defaultdict(list)
    errors: list[dict[str, str]] = []

    for path in tex_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            errors.append({"path": str(path), "error": str(error)})
            continue
        relative = path.relative_to(project_root).as_posix()
        for match in CITE_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            for key in match.group(1).split(","):
                clean = key.strip()
                if clean and clean != "*":
                    citations[clean].append(f"{relative}:{line}")

    for path in bib_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            errors.append({"path": str(path), "error": str(error)})
            continue
        relative = path.relative_to(project_root).as_posix()
        for key, entry in bib_entries(text):
            entries[key].append(relative)
            doi_match = DOI_RE.search(entry)
            if doi_match:
                doi = doi_match.group(1).strip().lower().removeprefix("https://doi.org/")
                dois[doi].append(key)

    cited_keys = set(citations)
    bibliography_keys = set(entries)
    return {
        "project_root": str(project_root),
        "tex_files": [path.relative_to(project_root).as_posix() for path in tex_files],
        "bib_files": [path.relative_to(project_root).as_posix() for path in bib_files],
        "citation_occurrences": sum(len(locations) for locations in citations.values()),
        "cited_keys": sorted(cited_keys),
        "missing_keys": {key: citations[key] for key in sorted(cited_keys - bibliography_keys)},
        "unused_keys": sorted(bibliography_keys - cited_keys),
        "duplicate_keys": {key: locations for key, locations in sorted(entries.items()) if len(locations) > 1},
        "duplicate_dois": {doi: keys for doi, keys in sorted(dois.items()) if len(set(keys)) > 1},
        "errors": errors,
        "ok": not errors and cited_keys <= bibliography_keys and all(len(v) == 1 for v in entries.values())
        and all(len(set(v)) == 1 for v in dois.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    arguments = parser.parse_args()
    root = Path(arguments.project_root).expanduser().resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Project root is not a directory: {root}"}, indent=2))
        return 1
    result = audit(root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
