#!/usr/bin/env python3
"""Plan or apply DOI-verified PDF imports into a research project."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
STOPWORDS = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with"}


def pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages[:5])
    except ImportError:
        executable = shutil.which("pdftotext")
        if not executable:
            raise RuntimeError("Install pypdf or pdftotext to inspect PDF files")
        result = subprocess.run(
            [executable, "-f", "1", "-l", "5", str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "pdftotext failed")
        return result.stdout


def detect_doi(text: str) -> str:
    matches = []
    for match in DOI_RE.findall(text):
        clean = match.rstrip(".,;:)]}").lower()
        if clean not in matches:
            matches.append(clean)
    if not matches:
        raise RuntimeError("No DOI found in the first five PDF pages")
    if len(matches) > 1:
        raise RuntimeError(f"Multiple DOI candidates found: {', '.join(matches)}")
    return matches[0]


def crossref_metadata(doi: str, email: str | None) -> dict[str, object]:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    if email:
        url += "?" + urllib.parse.urlencode({"mailto": email})
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "research-ai-assistant/0.4 (paper metadata lookup)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310 - fixed HTTPS host
        payload = json.load(response)
    message = payload.get("message", {})
    if not isinstance(message, dict):
        raise RuntimeError("Crossref returned invalid metadata")
    return message


def first(value: object) -> str:
    if isinstance(value, list) and value:
        return str(value[0]).strip()
    return ""


def publication_year(metadata: dict[str, object]) -> str:
    for field in ("published-print", "published-online", "issued", "created"):
        value = metadata.get(field)
        if not isinstance(value, dict):
            continue
        parts = value.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
            return str(parts[0][0])
    return ""


def authors(metadata: dict[str, object]) -> list[dict[str, str]]:
    result = []
    raw = metadata.get("author", [])
    if not isinstance(raw, list):
        return result
    for author in raw:
        if isinstance(author, dict):
            family = str(author.get("family", "")).strip()
            given = str(author.get("given", "")).strip()
            if family or given:
                result.append({"family": family, "given": given})
    return result


def slug(value: str, *, words: int = 0) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    tokens = re.findall(r"[A-Za-z0-9]+", normalized.lower())
    if words:
        tokens = tokens[:words]
    return "-".join(tokens)


def citation_key(family: str, year: str, title: str) -> str:
    title_words = [word for word in re.findall(r"[A-Za-z0-9]+", slug(title).replace("-", " ")) if word not in STOPWORDS]
    short = "".join(word.capitalize() for word in title_words[:3]) or "Work"
    return f"{slug(family).replace('-', '')}{year}{short}".replace("-", "")


def bib_value(value: str) -> str:
    return value.replace("{", "").replace("}", "").replace("&", r"\&").strip()


def bibtex(key: str, metadata: dict[str, object], doi: str) -> str:
    title = first(metadata.get("title"))
    people = authors(metadata)
    author_value = " and ".join(
        f"{person['family']}, {person['given']}".strip(", ") for person in people
    )
    year = publication_year(metadata)
    journal = first(metadata.get("container-title"))
    fields = [
        ("title", title),
        ("author", author_value),
        ("year", year),
        ("journal", journal),
        ("doi", doi),
        ("url", f"https://doi.org/{doi}"),
    ]
    lines = [f"@article{{{key},"]
    for name, value in fields:
        if value:
            lines.append(f"  {name} = {{{bib_value(value)}}},")
    lines.append("}")
    return "\n".join(lines)


def plan_file(source: Path, project_root: Path, bibliography: str, email: str | None) -> dict[str, object]:
    if not source.is_file() or source.suffix.casefold() != ".pdf":
        raise RuntimeError(f"Not a PDF file: {source}")
    doi = detect_doi(pdf_text(source))
    metadata = crossref_metadata(doi, email)
    title = first(metadata.get("title"))
    people = authors(metadata)
    year = publication_year(metadata)
    if not title or not people or not people[0]["family"] or not year:
        raise RuntimeError("Crossref metadata lacks title, first author, or publication year")
    family = people[0]["family"]
    filename = f"{slug(family)}-{year}-{slug(title, words=6)}.pdf"
    destination = project_root / "literature/pdfs" / filename
    key = citation_key(family, year, title)
    bib_text = bibliography.casefold()
    duplicate_doi = doi.casefold() in bib_text
    key_pattern = re.compile(
        r"@[A-Za-z]+\s*[({]\s*" + re.escape(key) + r"\s*,",
        re.IGNORECASE,
    )
    duplicate_key = bool(key_pattern.search(bibliography))
    destination_exists = destination.exists() and source.resolve() != destination.resolve()
    ready = not duplicate_doi and not duplicate_key and not destination_exists
    return {
        "source": str(source.resolve()),
        "doi": doi,
        "title": title,
        "authors": people,
        "year": year,
        "citation_key": key,
        "destination": str(destination.resolve()),
        "duplicate_doi": duplicate_doi,
        "duplicate_key": duplicate_key,
        "destination_exists": destination_exists,
        "ready": ready,
        "bibtex": bibtex(key, metadata, doi),
    }


def apply_plans(plans: list[dict[str, object]], bibliography_path: Path) -> None:
    if not all(plan["ready"] for plan in plans):
        raise RuntimeError("At least one import is not safe to apply; resolve duplicates or metadata first")
    destinations = [str(plan["destination"]) for plan in plans]
    if len(destinations) != len(set(destinations)):
        raise RuntimeError("Two imports resolve to the same destination filename")
    original_bibliography = bibliography_path.read_text(encoding="utf-8") if bibliography_path.exists() else ""
    moved: list[tuple[Path, Path]] = []
    try:
        for plan in plans:
            source = Path(str(plan["source"]))
            destination = Path(str(plan["destination"]))
            if source != destination:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                moved.append((source, destination))
            plan["applied"] = True
        bibliography_path.parent.mkdir(parents=True, exist_ok=True)
        additions = "\n\n".join(str(plan["bibtex"]) for plan in plans)
        separator = "\n\n" if original_bibliography.strip() else ""
        bibliography_path.write_text(original_bibliography.rstrip() + separator + additions + "\n", encoding="utf-8")
    except Exception:
        for source, destination in reversed(moved):
            if destination.exists() and not source.exists():
                shutil.move(str(destination), str(source))
        if original_bibliography:
            bibliography_path.write_text(original_bibliography, encoding="utf-8")
        elif bibliography_path.exists():
            bibliography_path.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--bibliography", default="literature/references.bib")
    parser.add_argument("--email", default=os.getenv("CROSSREF_MAILTO"))
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()
    project_root = Path(arguments.project_root).expanduser().resolve()
    bibliography_path = (project_root / arguments.bibliography).resolve()
    try:
        bibliography_path.relative_to(project_root)
        bibliography = bibliography_path.read_text(encoding="utf-8", errors="replace") if bibliography_path.exists() else ""
        plans = [
            plan_file(Path(value).expanduser().resolve(), project_root, bibliography, arguments.email)
            for value in arguments.files
        ]
        if arguments.apply:
            apply_plans(plans, bibliography_path)
        result = {
            "project_root": str(project_root),
            "bibliography": str(bibliography_path),
            "mode": "apply" if arguments.apply else "plan",
            "plans": plans,
            "ready": all(plan["ready"] for plan in plans),
        }
    except Exception as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
