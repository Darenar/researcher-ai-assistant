#!/usr/bin/env python3
"""Project-local hybrid semantic and lexical retrieval for research literature."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
import zipfile
from array import array
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence
from xml.etree import ElementTree

SUPPORTED_TEXT = {".bib", ".md", ".rst", ".tex", ".txt"}
SUPPORTED = SUPPORTED_TEXT | {".docx", ".pdf"}
DEFAULT_ROOTS = ("literature/pdfs", "literature/notes", "literature")
INDEX_RELATIVE_PATH = Path(".research-assistant/literature-index.sqlite3")
WORD_RE = re.compile(r"[\w'-]+", re.UNICODE)
DEFAULT_EMBEDDING_PROVIDER = "local"
DEFAULT_LOCAL_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_OPENAI_MODEL = "text-embedding-3-small"
DEFAULT_VOYAGE_MODEL = "voyage-4-lite"
DEFAULT_DIMENSIONS = {"local": 384, "openai": 1536, "voyage": 1024}


@dataclass(frozen=True)
class SourceChunk:
    path: str
    page: int | None
    chunk: int
    text: str


@dataclass(frozen=True)
class EmbeddingConfig:
    provider: str
    model: str
    dimensions: int


def resolve_project_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")
    return root


def project_config(project_root: Path) -> dict[str, object]:
    config_path = project_root / "config/research-assistant.json"
    if not config_path.is_file():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid project configuration: {config_path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"Project configuration must be a JSON object: {config_path}")
    return payload


def configured_roots(project_root: Path) -> list[Path]:
    payload = project_config(project_root)
    literature = payload.get("literature", {})
    configured = literature.get("roots", []) if isinstance(literature, dict) else []
    candidates = configured if isinstance(configured, list) and configured else list(DEFAULT_ROOTS)
    roots: list[Path] = []
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        resolved = (project_root / candidate).resolve()
        try:
            resolved.relative_to(project_root)
        except ValueError as error:
            raise ValueError(f"Literature root escapes the project: {candidate}") from error
        if resolved.is_dir() and not any(resolved == root or resolved.is_relative_to(root) for root in roots):
            roots.append(resolved)
    return roots


def embedding_config(project_root: Path) -> EmbeddingConfig:
    payload = project_config(project_root)
    raw = payload.get("embeddings", {})
    settings = raw if isinstance(raw, dict) else {}
    provider = str(settings.get("provider", DEFAULT_EMBEDDING_PROVIDER)).casefold()
    if provider in {"anthropic", "claude"}:
        raise ValueError(
            "Claude has no first-party embeddings endpoint. Use provider 'local', "
            "'openai', or 'voyage' for a Claude-oriented workflow."
        )
    if provider not in {"local", "openai", "voyage"}:
        raise ValueError(f"Unsupported embedding provider: {provider}")
    default_model = {
        "local": DEFAULT_LOCAL_MODEL,
        "openai": DEFAULT_OPENAI_MODEL,
        "voyage": DEFAULT_VOYAGE_MODEL,
    }[provider]
    model = str(settings.get("model", default_model))
    raw_dimensions = settings.get("dimensions", DEFAULT_DIMENSIONS[provider])
    try:
        dimensions = int(raw_dimensions)
    except (TypeError, ValueError) as error:
        raise ValueError("Embedding dimensions must be an integer") from error
    if dimensions < 1:
        raise ValueError("Embedding dimensions must be positive")
    return EmbeddingConfig(provider=provider, model=model, dimensions=dimensions)


def source_files(project_root: Path) -> list[Path]:
    files: set[Path] = set()
    for root in configured_roots(project_root):
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED and not path.name.startswith("."):
                files.add(path)
    return sorted(files)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_pdf(path: Path) -> list[tuple[int | None, str]]:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return [(number, page.extract_text() or "") for number, page in enumerate(reader.pages, 1)]
    except ImportError:
        executable = shutil.which("pdftotext")
        if not executable:
            raise RuntimeError(
                f"Cannot extract {path.name}: install pypdf or the pdftotext command"
            )
        result = subprocess.run(
            [executable, "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
        return [(number, text) for number, text in enumerate(result.stdout.split("\f"), 1)]


def extract_docx(path: Path) -> list[tuple[int | None, str]]:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    text = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
    return [(None, text)]


def extract_source(path: Path) -> list[tuple[int | None, str]]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path)
    if suffix == ".docx":
        return extract_docx(path)
    return [(None, path.read_text(encoding="utf-8", errors="replace"))]


def chunk_text(text: str, *, size: int = 360, overlap: int = 60) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(start + 1, end - overlap)
    return chunks


def connect(project_root: Path) -> sqlite3.Connection:
    index_path = project_root / INDEX_RELATIVE_PATH
    index_path.parent.mkdir(parents=True, exist_ok=True)
    database = sqlite3.connect(index_path)
    database.execute("PRAGMA foreign_keys = ON")
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS documents (
            path TEXT PRIMARY KEY,
            sha256 TEXT NOT NULL,
            size INTEGER NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
            path UNINDEXED,
            page UNINDEXED,
            chunk UNINDEXED,
            text,
            tokenize = 'unicode61 remove_diacritics 2'
        );
        CREATE TABLE IF NOT EXISTS chunk_embeddings (
            chunk_rowid INTEGER PRIMARY KEY,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            dimensions INTEGER NOT NULL,
            vector BLOB NOT NULL
        );
        """
    )
    return database


def relative(project_root: Path, path: Path) -> str:
    return path.relative_to(project_root).as_posix()


def status(project_root: Path) -> dict[str, object]:
    files = source_files(project_root)
    index_path = project_root / INDEX_RELATIVE_PATH
    indexed: dict[str, str] = {}
    if index_path.is_file():
        with connect(project_root) as database:
            indexed = dict(database.execute("SELECT path, sha256 FROM documents"))
    current = {relative(project_root, path): file_hash(path) for path in files}
    return {
        "project_root": str(project_root),
        "index": str(index_path),
        "sources": len(current),
        "indexed": len(indexed),
        "new": sorted(set(current) - set(indexed)),
        "changed": sorted(path for path in current.keys() & indexed.keys() if current[path] != indexed[path]),
        "removed": sorted(set(indexed) - set(current)),
        "stale": current != indexed,
    }


def delete_path(database: sqlite3.Connection, path: str) -> None:
    database.execute(
        "DELETE FROM chunk_embeddings WHERE chunk_rowid IN (SELECT rowid FROM chunks WHERE path = ?)",
        (path,),
    )
    database.execute("DELETE FROM chunks WHERE path = ?", (path,))
    database.execute("DELETE FROM documents WHERE path = ?", (path,))


def index(project_root: Path) -> dict[str, object]:
    files = source_files(project_root)
    current_paths = {relative(project_root, path): path for path in files}
    errors: list[dict[str, str]] = []
    updated: list[str] = []

    with connect(project_root) as database:
        indexed = dict(database.execute("SELECT path, sha256 FROM documents"))
        for removed in sorted(set(indexed) - set(current_paths)):
            delete_path(database, removed)

        for relative_path, path in current_paths.items():
            digest = file_hash(path)
            if indexed.get(relative_path) == digest:
                continue
            try:
                pages = extract_source(path)
                source_chunks = [
                    SourceChunk(relative_path, page, number, chunk)
                    for page, text in pages
                    for number, chunk in enumerate(chunk_text(text))
                ]
                if not source_chunks:
                    raise RuntimeError("no extractable text")
            except Exception as error:  # keep the previous healthy index on extraction failure
                errors.append({"path": relative_path, "error": str(error)})
                continue

            delete_path(database, relative_path)
            database.execute(
                "INSERT OR REPLACE INTO documents(path, sha256, size) VALUES (?, ?, ?)",
                (relative_path, digest, path.stat().st_size),
            )
            database.executemany(
                "INSERT INTO chunks(path, page, chunk, text) VALUES (?, ?, ?, ?)",
                [(item.path, item.page, item.chunk, item.text) for item in source_chunks],
            )
            updated.append(relative_path)
        database.commit()
        chunk_count = database.execute("SELECT count(*) FROM chunks").fetchone()[0]
        document_count = database.execute("SELECT count(*) FROM documents").fetchone()[0]

    return {
        "project_root": str(project_root),
        "documents": document_count,
        "chunks": chunk_count,
        "updated": updated,
        "errors": errors,
    }


def provider_ready(config: EmbeddingConfig) -> tuple[bool, str]:
    if config.provider == "local":
        ready = importlib.util.find_spec("fastembed") is not None
        return ready, "ready" if ready else "Install fastembed to use the local embedding model"
    if config.provider == "openai":
        ready = importlib.util.find_spec("openai") is not None and bool(os.getenv("OPENAI_API_KEY"))
        return ready, "ready" if ready else "Install openai and set OPENAI_API_KEY"
    ready = bool(os.getenv("VOYAGE_API_KEY"))
    return ready, "ready" if ready else "Set VOYAGE_API_KEY"


def embedding_status(project_root: Path) -> dict[str, object]:
    config = embedding_config(project_root)
    index_result = status(project_root)
    index_path = project_root / INDEX_RELATIVE_PATH
    total = matching = incompatible = 0
    if index_path.is_file():
        with connect(project_root) as database:
            total = int(database.execute("SELECT count(*) FROM chunks").fetchone()[0])
            matching = int(
                database.execute(
                    """
                    SELECT count(*) FROM chunk_embeddings
                    WHERE provider = ? AND model = ? AND dimensions = ?
                    """,
                    (config.provider, config.model, config.dimensions),
                ).fetchone()[0]
            )
            incompatible = int(
                database.execute(
                    """
                    SELECT count(*) FROM chunk_embeddings
                    WHERE provider != ? OR model != ? OR dimensions != ?
                    """,
                    (config.provider, config.model, config.dimensions),
                ).fetchone()[0]
            )
    ready, readiness = provider_ready(config)
    pending = max(0, total - matching)
    return {
        "project_root": str(project_root),
        "config": asdict(config),
        "provider_ready": ready,
        "provider_message": readiness,
        "chunks": total,
        "embedded": matching,
        "pending": pending,
        "incompatible": incompatible,
        "requires_rebuild": incompatible > 0,
        "literature_stale": bool(index_result["stale"]),
        "ready": ready and pending == 0 and incompatible == 0 and not index_result["stale"],
    }


def normalize_vector(values: Sequence[float]) -> list[float]:
    vector = [float(value) for value in values]
    norm = math.sqrt(sum(value * value for value in vector))
    if not vector or norm == 0:
        raise ValueError("Embedding provider returned an empty or zero vector")
    return [value / norm for value in vector]


def vector_blob(values: Sequence[float]) -> bytes:
    return array("f", normalize_vector(values)).tobytes()


def blob_vector(value: bytes) -> array:
    result = array("f")
    result.frombytes(value)
    return result


def embed_texts(config: EmbeddingConfig, texts: list[str], *, input_type: str) -> list[list[float]]:
    if not texts:
        return []
    if config.provider == "local":
        try:
            from fastembed import TextEmbedding  # type: ignore
        except ImportError as error:
            raise RuntimeError("Install fastembed to use provider 'local'") from error
        model = TextEmbedding(model_name=config.model)
        generator: Iterable[Sequence[float]]
        if input_type == "query":
            generator = model.query_embed(texts)
        else:
            generator = model.passage_embed(texts)
        return [normalize_vector(vector) for vector in generator]

    if config.provider == "openai":
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as error:
            raise RuntimeError("Install openai to use provider 'openai'") from error
        parameters: dict[str, object] = {"model": config.model, "input": texts}
        if config.dimensions:
            parameters["dimensions"] = config.dimensions
        response = OpenAI().embeddings.create(**parameters)
        ordered = sorted(response.data, key=lambda item: item.index)
        return [normalize_vector(item.embedding) for item in ordered]

    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise RuntimeError("Set VOYAGE_API_KEY to use provider 'voyage'")
    body = {
        "input": texts,
        "model": config.model,
        "input_type": input_type,
        "output_dimension": config.dimensions,
    }
    request = urllib.request.Request(
        "https://api.voyageai.com/v1/embeddings",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:  # nosec B310 - fixed HTTPS endpoint
        payload = json.load(response)
    ordered = sorted(payload["data"], key=lambda item: item["index"])
    return [normalize_vector(item["embedding"]) for item in ordered]


def build_embeddings(project_root: Path, *, rebuild: bool = False, batch_size: int = 64) -> dict[str, object]:
    config = embedding_config(project_root)
    ready, readiness = provider_ready(config)
    if not ready:
        raise RuntimeError(readiness)
    index_result = index(project_root)
    with connect(project_root) as database:
        incompatible = int(
            database.execute(
                """
                SELECT count(*) FROM chunk_embeddings
                WHERE provider != ? OR model != ? OR dimensions != ?
                """,
                (config.provider, config.model, config.dimensions),
            ).fetchone()[0]
        )
        if incompatible and not rebuild:
            raise RuntimeError(
                "Embedding provider, model, or dimensions changed. Run embeddings build --rebuild; "
                "vectors from different model spaces cannot be converted or mixed."
            )
        if rebuild:
            database.execute("DELETE FROM chunk_embeddings")
            database.commit()
        pending = database.execute(
            """
            SELECT rowid, text FROM chunks
            WHERE rowid NOT IN (SELECT chunk_rowid FROM chunk_embeddings)
            ORDER BY rowid
            """
        ).fetchall()

        embedded = 0
        for start in range(0, len(pending), max(1, batch_size)):
            batch = pending[start : start + max(1, batch_size)]
            vectors = embed_texts(config, [row[1] for row in batch], input_type="document")
            if len(vectors) != len(batch):
                raise RuntimeError("Embedding provider returned the wrong number of vectors")
            records = []
            for (rowid, _), vector in zip(batch, vectors):
                if len(vector) != config.dimensions:
                    raise RuntimeError(
                        f"Model returned {len(vector)} dimensions; configuration expects {config.dimensions}"
                    )
                records.append(
                    (int(rowid), config.provider, config.model, config.dimensions, vector_blob(vector))
                )
            database.executemany(
                """
                INSERT OR REPLACE INTO chunk_embeddings
                    (chunk_rowid, provider, model, dimensions, vector)
                VALUES (?, ?, ?, ?, ?)
                """,
                records,
            )
            database.commit()
            embedded += len(records)

    result = embedding_status(project_root)
    result.update({"created": embedded, "literature_index": index_result})
    return result


def fts_query(value: str) -> str:
    terms = []
    seen = set()
    for term in WORD_RE.findall(value.casefold()):
        if len(term) < 2 or term in seen:
            continue
        seen.add(term)
        terms.append('"' + term.replace('"', '""') + '"')
    if not terms:
        raise ValueError("Search query contains no searchable terms")
    return " OR ".join(terms[:24])


def lexical_search(database: sqlite3.Connection, query: str, limit: int) -> list[dict[str, object]]:
    rows = database.execute(
        """
        SELECT rowid, path, page, chunk, text, -bm25(chunks) AS score
        FROM chunks
        WHERE chunks MATCH ?
        ORDER BY bm25(chunks)
        LIMIT ?
        """,
        (fts_query(query), limit),
    ).fetchall()
    return [
        {
            "rowid": int(rowid),
            "path": path,
            "page": page,
            "chunk": int(chunk_number),
            "text": text,
            "lexical_score": float(score),
        }
        for rowid, path, page, chunk_number, text, score in rows
    ]


def semantic_search(
    database: sqlite3.Connection,
    config: EmbeddingConfig,
    query: str,
    limit: int,
) -> list[dict[str, object]]:
    query_vector = embed_texts(config, [query], input_type="query")[0]
    if len(query_vector) != config.dimensions:
        raise RuntimeError(
            f"Model returned {len(query_vector)} query dimensions; "
            f"configuration expects {config.dimensions}"
        )
    rows = database.execute(
        """
        SELECT c.rowid, c.path, c.page, c.chunk, c.text, e.vector
        FROM chunks AS c
        JOIN chunk_embeddings AS e ON e.chunk_rowid = c.rowid
        WHERE e.provider = ? AND e.model = ? AND e.dimensions = ?
        """,
        (config.provider, config.model, config.dimensions),
    ).fetchall()
    scored: list[dict[str, object]] = []
    for rowid, path, page, chunk_number, text, raw_vector in rows:
        vector = blob_vector(raw_vector)
        score = sum(left * right for left, right in zip(query_vector, vector))
        scored.append(
            {
                "rowid": int(rowid),
                "path": path,
                "page": page,
                "chunk": int(chunk_number),
                "text": text,
                "semantic_score": float(score),
            }
        )
    scored.sort(key=lambda item: float(item["semantic_score"]), reverse=True)
    return scored[:limit]


def add_citation(item: dict[str, object]) -> dict[str, object]:
    page = item.get("page")
    path = str(item["path"])
    item["citation"] = f"{path}, p. {page}" if page else path
    item.pop("rowid", None)
    for key in ("score", "lexical_score", "semantic_score"):
        if key in item:
            item[key] = round(float(item[key]), 6)
    return item


def search(project_root: Path, query: str, limit: int, mode: str = "hybrid") -> dict[str, object]:
    index_path = project_root / INDEX_RELATIVE_PATH
    if not index_path.is_file():
        raise RuntimeError("Literature index does not exist; run the index and embeddings build commands")
    config = embedding_config(project_root)
    with connect(project_root) as database:
        if mode == "lexical":
            results = lexical_search(database, query, limit)
        else:
            health = embedding_status(project_root)
            if not health["ready"]:
                raise RuntimeError(
                    "Semantic embeddings are missing or stale; run embeddings status and embeddings build"
                )
            semantic = semantic_search(database, config, query, limit * 4)
            if mode == "semantic":
                results = semantic[:limit]
            else:
                lexical = lexical_search(database, query, limit * 4)
                combined: dict[int, dict[str, object]] = {}
                for rank, item in enumerate(semantic, 1):
                    rowid = int(item["rowid"])
                    combined[rowid] = dict(item)
                    combined[rowid]["score"] = 1.0 / (60 + rank)
                for rank, item in enumerate(lexical, 1):
                    rowid = int(item["rowid"])
                    if rowid not in combined:
                        combined[rowid] = dict(item)
                        combined[rowid]["score"] = 0.0
                    else:
                        combined[rowid]["lexical_score"] = item["lexical_score"]
                    combined[rowid]["score"] = float(combined[rowid]["score"]) + 1.0 / (60 + rank)
                results = sorted(combined.values(), key=lambda item: float(item["score"]), reverse=True)[:limit]
    return {
        "query": query,
        "mode": mode,
        "embedding_config": asdict(config) if mode != "lexical" else None,
        "results": [add_citation(item) for item in results],
        "count": len(results),
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    for command in ("status", "index"):
        child = subparsers.add_parser(command)
        child.add_argument("--project-root", default=".")
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--project-root", default=".")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=8)
    search_parser.add_argument("--mode", choices=("hybrid", "semantic", "lexical"), default="hybrid")

    embeddings_parser = subparsers.add_parser("embeddings")
    embeddings_commands = embeddings_parser.add_subparsers(dest="embeddings_command", required=True)
    embeddings_status_parser = embeddings_commands.add_parser("status")
    embeddings_status_parser.add_argument("--project-root", default=".")
    embeddings_build_parser = embeddings_commands.add_parser("build")
    embeddings_build_parser.add_argument("--project-root", default=".")
    embeddings_build_parser.add_argument("--rebuild", action="store_true")
    embeddings_build_parser.add_argument("--batch-size", type=int, default=64)
    return root


def main() -> int:
    arguments = parser().parse_args()
    try:
        project_root = resolve_project_root(arguments.project_root)
        if arguments.command == "status":
            payload = status(project_root)
        elif arguments.command == "index":
            payload = index(project_root)
        elif arguments.command == "search":
            payload = search(
                project_root,
                arguments.query,
                max(1, min(arguments.limit, 50)),
                arguments.mode,
            )
        elif arguments.embeddings_command == "status":
            payload = embedding_status(project_root)
        else:
            payload = build_embeddings(
                project_root,
                rebuild=arguments.rebuild,
                batch_size=max(1, min(arguments.batch_size, 1000)),
            )
    except Exception as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
