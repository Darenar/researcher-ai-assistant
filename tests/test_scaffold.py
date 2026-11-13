from pathlib import Path

import pytest

from research_assistant.scaffold import format_project


def test_format_project_creates_expected_structure(tmp_path: Path) -> None:
    project = tmp_path / "study"

    result = format_project(project)

    assert result.root == project
    assert (project / "data/raw/.gitkeep").is_file()
    assert (project / "data/intermediate").is_dir()
    assert (project / "data/final").is_dir()
    assert (project / "artifacts/tables").is_dir()
    assert (project / "artifacts/figures").is_dir()
    assert (project / "literature/references.bib").is_file()
    assert (project / "config/research-assistant.json").is_file()
    assert (project / "paper/main.tex").is_file()
    assert (project / "paper/sections/methods.tex").is_file()


def test_format_project_does_not_overwrite_existing_files(tmp_path: Path) -> None:
    project = tmp_path / "study"
    project.mkdir()
    readme = project / "README.md"
    readme.write_text("My existing notes", encoding="utf-8")

    result = format_project(project)

    assert readme.read_text(encoding="utf-8") == "My existing notes"
    assert "README.md" in result.skipped


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    project = tmp_path / "study"

    result = format_project(project, dry_run=True)

    assert result.created
    assert not project.exists()


def test_rejects_a_file_as_the_project_path(tmp_path: Path) -> None:
    project = tmp_path / "not-a-folder"
    project.write_text("content", encoding="utf-8")

    with pytest.raises(ValueError, match="not a directory"):
        format_project(project)

