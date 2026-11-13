"""Safe, deterministic creation of a research project structure."""

from dataclasses import dataclass, field
from pathlib import Path

from research_assistant.templates import PROJECT_DIRECTORIES, PROJECT_FILES


@dataclass
class ScaffoldResult:
    """Summary of a formatting operation."""

    root: Path
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    dry_run: bool = False

    def as_text(self) -> str:
        action = "Would create" if self.dry_run else "Created"
        lines = [f"Research project: {self.root}", f"{action}: {len(self.created)}"]
        lines.extend(f"  + {path}" for path in self.created)
        lines.append(f"Skipped existing: {len(self.skipped)}")
        lines.extend(f"  = {path}" for path in self.skipped)
        return "\n".join(lines)


def format_project(path: str | Path, *, dry_run: bool = False) -> ScaffoldResult:
    """Create missing research folders and starter files without overwriting.

    Args:
        path: Project directory to format. It may not exist yet.
        dry_run: Report what would be created without writing anything.
    """

    root = Path(path).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")

    result = ScaffoldResult(root=root, dry_run=dry_run)

    if not root.exists():
        result.created.append("./")
        if not dry_run:
            root.mkdir(parents=True)

    for relative_path in PROJECT_DIRECTORIES:
        destination = root / relative_path
        if destination.exists():
            if not destination.is_dir():
                raise ValueError(f"Expected a directory but found a file: {destination}")
            result.skipped.append(f"{relative_path}/")
        else:
            result.created.append(f"{relative_path}/")
            if not dry_run:
                destination.mkdir(parents=True)

    for relative_path, content in PROJECT_FILES.items():
        destination = root / relative_path
        if destination.exists():
            result.skipped.append(relative_path)
            continue

        result.created.append(relative_path)
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

    return result

