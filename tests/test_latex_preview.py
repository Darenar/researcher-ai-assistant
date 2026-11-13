import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from research_assistant.scaffold import format_project


SCRIPT = (
    Path(__file__).parents[1]
    / "plugins/research-assistant/skills/latex-paper-preview/scripts/compile_latex.py"
)


@pytest.mark.skipif(
    not shutil.which("latexmk") or not shutil.which("pdflatex"),
    reason="LaTeX toolchain is not installed",
)
def test_compiles_scaffolded_paper(tmp_path: Path) -> None:
    project = tmp_path / "study"
    format_project(project)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(project)],
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 0, payload.get("log_tail")
    assert payload["success"] is True
    assert (project / "paper/main.pdf").is_file()
