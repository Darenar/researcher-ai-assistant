import csv
import importlib.util
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]


def load_script(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


citation_audit = load_script(
    "citation_audit",
    "plugins/research-assistant/skills/citation-audit/scripts/citation_audit.py",
)
evidence_matrix = load_script(
    "evidence_matrix",
    "plugins/research-assistant/skills/evidence-matrix/scripts/evidence_matrix.py",
)
git_compare = load_script(
    "git_compare",
    "plugins/research-assistant/skills/git-version-compare/scripts/git_compare.py",
)
paper_ingest = load_script(
    "paper_ingest",
    "plugins/research-assistant/skills/paper-ingest/scripts/paper_ingest.py",
)


def test_rai_routes_to_existing_specialist_skills() -> None:
    skills = ROOT / "plugins/research-assistant/skills"
    instructions = (skills / "rai/SKILL.md").read_text(encoding="utf-8")
    routes = re.findall(r"`([^`]+/SKILL\.md)`", instructions)

    assert routes
    assert all((skills / route).is_file() for route in routes)


def test_citation_audit_reports_missing_and_duplicate_dois(tmp_path: Path) -> None:
    (tmp_path / "paper").mkdir()
    (tmp_path / "literature").mkdir()
    (tmp_path / "paper/main.tex").write_text(
        r"Evidence supports this claim \cite{known,missing}.", encoding="utf-8"
    )
    (tmp_path / "literature/references.bib").write_text(
        """@article{known,
  title = {Known},
  doi = {10.1000/example}
}
@article{duplicate,
  title = {Duplicate},
  doi = {10.1000/example}
}
""",
        encoding="utf-8",
    )

    result = citation_audit.audit(tmp_path)

    assert result["missing_keys"] == {"missing": ["paper/main.tex:1"]}
    assert result["duplicate_dois"] == {"10.1000/example": ["known", "duplicate"]}
    assert result["ok"] is False


def test_evidence_matrix_initializes_and_validates_provenance(tmp_path: Path) -> None:
    source = tmp_path / "literature/paper.md"
    source.parent.mkdir()
    source.write_text("Evidence", encoding="utf-8")
    matrix = tmp_path / "research/evidence-matrix.csv"
    assert evidence_matrix.initialize(matrix)["created"] is True
    with matrix.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=evidence_matrix.FIELDS)
        writer.writerow(
            {
                "study_id": "smith2026",
                "outcome": "retention",
                "finding": "Delayed testing improved retention.",
                "source": "literature/paper.md",
                "page": "1",
            }
        )

    result = evidence_matrix.validate(matrix, tmp_path)

    assert result["rows"] == 1
    assert result["ok"] is True


def test_git_compare_reports_changes_between_commits(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    paper = tmp_path / "paper.tex"
    paper.write_text("First version\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "paper.tex"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "first"], check=True)
    base = subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True).strip()
    paper.write_text("Second version\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qam", "second"], check=True)
    target = subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True).strip()

    result = git_compare.compare(tmp_path, base, target, [])

    assert result["file_count"] == 1
    assert result["files"][0]["path"] == "paper.tex"
    assert result["working_tree_dirty"] is False


def test_paper_ingest_plans_and_applies_verified_metadata(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "download.pdf"
    source.write_bytes(b"fake pdf")
    monkeypatch.setattr(paper_ingest, "pdf_text", lambda path: "doi:10.1000/example")
    monkeypatch.setattr(
        paper_ingest,
        "crossref_metadata",
        lambda doi, email: {
            "title": ["Testing Memory Over Time"],
            "author": [{"family": "Smith", "given": "A."}],
            "issued": {"date-parts": [[2026]]},
            "container-title": ["Journal of Tests"],
        },
    )

    plan = paper_ingest.plan_file(source, tmp_path, "", None)
    bibliography = tmp_path / "literature/references.bib"
    paper_ingest.apply_plans([plan], bibliography)

    assert plan["ready"] is True
    assert Path(plan["destination"]).is_file()
    assert not source.exists()
    assert "10.1000/example" in bibliography.read_text(encoding="utf-8")
