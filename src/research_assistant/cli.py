"""Command-line interface for the research assistant."""

import argparse
import asyncio
from pathlib import Path
from typing import Sequence

from research_assistant.agent import run_chat_agent, run_format_agent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-assistant",
        description="Create a clear, maintainable research project structure.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    format_parser = subparsers.add_parser(
        "format",
        help="Format a folder as a research project.",
    )
    format_parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Project folder (default: current directory).",
    )
    format_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without creating files.",
    )

    chat_parser = subparsers.add_parser(
        "chat",
        help="Send a message about a research project.",
    )
    chat_parser.add_argument("message", help="Message for the research assistant.")
    chat_parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project folder (default: current directory).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "format":
            output = asyncio.run(run_format_agent(args.path, dry_run=args.dry_run))
        else:
            output = asyncio.run(run_chat_agent(args.path, args.message))
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception as error:
        raise SystemExit(f"Error: {error}") from error
    print(output)


if __name__ == "__main__":
    main()

