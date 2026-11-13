#!/usr/bin/env python3
"""Initialize and validate an auditable research evidence matrix."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


FIELDS = [
    "study_id",
    "citation",
    "research_question",
    "design",
    "sample",
    "exposure_or_intervention",
    "comparator",
    "outcome",
    "effect",
    "finding",
    "limitations",
    "source",
    "page",
    "notes",
]
PAGE_RE = re.compile(r"^(?:\d+|\d+\s*[-–]\s*\d+|not available)$", re.IGNORECASE)


def initialize(path: Path) -> dict[str, object]:
    if path.exists():
        return {"path": str(path), "created": False, "message": "Matrix already exists"}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=FIELDS).writeheader()
    return {"path": str(path), "created": True, "fields": FIELDS}


def validate(path: Path, project_root: Path) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    if not path.is_file():
        return {"path": str(path), "rows": 0, "errors": [{"error": "Matrix does not exist"}], "warnings": [], "ok": False}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        actual = reader.fieldnames or []
        missing_fields = [field for field in FIELDS if field not in actual]
        if missing_fields:
            errors.append({"error": "Missing required columns", "fields": missing_fields})
        rows = list(reader)

    identities: Counter[tuple[str, str]] = Counter()
    for number, row in enumerate(rows, 2):
        study_id = (row.get("study_id") or "").strip()
        outcome = (row.get("outcome") or "").strip()
        finding = (row.get("finding") or "").strip()
        source = (row.get("source") or "").strip()
        page = (row.get("page") or "").strip()
        if not study_id:
            errors.append({"row": number, "field": "study_id", "error": "Required value is empty"})
        if not outcome:
            errors.append({"row": number, "field": "outcome", "error": "Required value is empty"})
        if finding and not source:
            errors.append({"row": number, "field": "source", "error": "A finding requires a source"})
        if source:
            source_path = (project_root / source).resolve()
            try:
                source_path.relative_to(project_root)
            except ValueError:
                errors.append({"row": number, "field": "source", "error": "Source escapes project root"})
            else:
                if not source_path.is_file():
                    errors.append({"row": number, "field": "source", "error": "Source file does not exist"})
        if page and not PAGE_RE.match(page):
            warnings.append({"row": number, "field": "page", "warning": "Use a page number, range, or 'not available'"})
        if study_id and outcome:
            identities[(study_id.casefold(), outcome.casefold())] += 1

    for (study_id, outcome), count in identities.items():
        if count > 1:
            warnings.append({"study_id": study_id, "outcome": outcome, "warning": f"{count} rows share this study/outcome"})
    return {"path": str(path), "rows": len(rows), "errors": errors, "warnings": warnings, "ok": not errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init_parser = commands.add_parser("init")
    init_parser.add_argument("--path", default="research/evidence-matrix.csv")
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("--path", default="research/evidence-matrix.csv")
    validate_parser.add_argument("--project-root", default=".")
    arguments = parser.parse_args()
    root = Path(getattr(arguments, "project_root", ".")).expanduser().resolve()
    path = Path(arguments.path).expanduser()
    if not path.is_absolute():
        path = root / path
    result = initialize(path) if arguments.command == "init" else validate(path, root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
