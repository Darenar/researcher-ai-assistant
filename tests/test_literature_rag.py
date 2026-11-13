import importlib.util
import json
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "plugins/research-assistant/skills/literature-rag/scripts/literature_rag.py"
)
SPEC = importlib.util.spec_from_file_location("literature_rag", SCRIPT)
assert SPEC and SPEC.loader
literature_rag = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = literature_rag
SPEC.loader.exec_module(literature_rag)


def test_indexes_and_searches_only_the_active_project(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    (first / "literature/notes").mkdir(parents=True)
    (second / "literature/notes").mkdir(parents=True)
    (first / "literature/notes/alpha.md").write_text(
        "Delayed testing improved retention in the intervention group.",
        encoding="utf-8",
    )
    (second / "literature/notes/beta.md").write_text(
        "This unrelated project discusses marine sediment.",
        encoding="utf-8",
    )

    result = literature_rag.index(first)
    search = literature_rag.search(first, "delayed retention", 5, mode="lexical")

    assert result["documents"] == 1
    assert search["count"] == 1
    assert search["results"][0]["path"] == "literature/notes/alpha.md"
    assert "beta.md" not in str(search)


def test_index_status_detects_changed_and_removed_sources(tmp_path: Path) -> None:
    project = tmp_path / "study"
    notes = project / "literature/notes"
    notes.mkdir(parents=True)
    source = notes / "paper.md"
    source.write_text("Initial evidence about treatment effects.", encoding="utf-8")
    literature_rag.index(project)

    assert literature_rag.status(project)["stale"] is False

    source.write_text("Revised evidence about treatment effects.", encoding="utf-8")
    changed = literature_rag.status(project)
    assert changed["changed"] == ["literature/notes/paper.md"]

    source.unlink()
    removed = literature_rag.status(project)
    assert removed["removed"] == ["literature/notes/paper.md"]


def write_embedding_config(project: Path, model: str) -> None:
    config = project / "config/research-assistant.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        json.dumps(
            {
                "embeddings": {
                    "provider": "local",
                    "model": model,
                    "dimensions": 2,
                }
            }
        ),
        encoding="utf-8",
    )


def fake_embed(config, texts, *, input_type):
    if input_type == "query":
        return [[1.0, 0.0] for _ in texts]
    return [
        [1.0, 0.0] if "retention" in text.casefold() else [0.0, 1.0]
        for text in texts
    ]


def test_builds_embeddings_once_and_searches_semantically(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "semantic-study"
    notes = project / "literature/notes"
    notes.mkdir(parents=True)
    (notes / "memory.md").write_text(
        "Delayed testing produced stronger long-term retention.", encoding="utf-8"
    )
    (notes / "ocean.md").write_text(
        "Marine sediment accumulated near the continental shelf.", encoding="utf-8"
    )
    write_embedding_config(project, "fake-small")
    monkeypatch.setattr(literature_rag, "provider_ready", lambda config: (True, "ready"))
    monkeypatch.setattr(literature_rag, "embed_texts", fake_embed)

    first = literature_rag.build_embeddings(project)
    second = literature_rag.build_embeddings(project)
    result = literature_rag.search(project, "memory performance", 2, mode="semantic")

    assert first["created"] == 2
    assert first["ready"] is True
    assert second["created"] == 0
    assert result["results"][0]["path"] == "literature/notes/memory.md"


def test_model_change_requires_explicit_rebuild(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "model-change"
    notes = project / "literature/notes"
    notes.mkdir(parents=True)
    (notes / "paper.md").write_text("Evidence about retention.", encoding="utf-8")
    write_embedding_config(project, "fake-a")
    monkeypatch.setattr(literature_rag, "provider_ready", lambda config: (True, "ready"))
    monkeypatch.setattr(literature_rag, "embed_texts", fake_embed)
    literature_rag.build_embeddings(project)

    write_embedding_config(project, "fake-b")

    assert literature_rag.embedding_status(project)["requires_rebuild"] is True
    try:
        literature_rag.build_embeddings(project)
    except RuntimeError as error:
        assert "cannot be converted or mixed" in str(error)
    else:
        raise AssertionError("Changing an embedding model must require --rebuild")

    rebuilt = literature_rag.build_embeddings(project, rebuild=True)
    assert rebuilt["created"] == 1
    assert rebuilt["ready"] is True
