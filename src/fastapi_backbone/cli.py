"""Command-line entry point for the FastAPI Backbone project generator."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from .generator import GenerationError, ProjectGenerator


class DatabaseCommandError(RuntimeError):
    """Raised when a database helper command cannot be executed."""


def _run_alembic(arguments: list[str], project_root: Path = Path(".")) -> int:
    """Run Alembic from a generated project's root without invoking a shell."""
    root = project_root.resolve()
    config = root / "alembic.ini"
    if not config.is_file():
        raise DatabaseCommandError(f"alembic.ini not found in project directory: {root}")

    env = os.environ.copy()
    src = root / "src"
    if src.is_dir():
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(src), existing) if part
        )

    completed = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=root,
        env=env,
        check=False,
    )
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fastapi-backbone",
        description="Generate production-oriented FastAPI application foundations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    new = subparsers.add_parser("new", help="Create a new FastAPI application.")
    new.add_argument("name", help="Project/package name, for example myapp.")
    new.add_argument(
        "--output",
        type=Path,
        default=Path("."),
        help="Parent directory for the generated project (default: current directory).",
    )
    new.add_argument(
        "--ai",
        action="store_true",
        help="Include the optional provider-agnostic Pydantic AI architecture.",
    )
    new.add_argument(
        "--force",
        action="store_true",
        help="Allow generation into an existing empty project directory.",
    )

    db = subparsers.add_parser("db", help="Run an explicit Alembic migration command.")
    db_subparsers = db.add_subparsers(dest="db_command", required=True)

    upgrade = db_subparsers.add_parser("upgrade", help="Upgrade the database.")
    upgrade.add_argument("revision", nargs="?", default="head")

    downgrade = db_subparsers.add_parser("downgrade", help="Downgrade the database.")
    downgrade.add_argument("revision", nargs="?", default="-1")

    db_subparsers.add_parser("current", help="Show the current database revision.")
    db_subparsers.add_parser("history", help="Show migration history.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "new":
        try:
            path = ProjectGenerator(
                name=args.name,
                output=args.output,
                include_ai=args.ai,
                force=args.force,
            ).generate()
        except GenerationError as exc:
            parser.error(str(exc))
        print(f"Generated {args.name} at {path}")
        if args.ai:
            print("AI profile: Pydantic AI architecture included (provider configured at runtime).")
        return 0

    if args.command == "db":
        arguments = [args.db_command]
        if args.db_command in {"upgrade", "downgrade"}:
            arguments.append(args.revision)
        try:
            return _run_alembic(arguments)
        except DatabaseCommandError as exc:
            parser.error(str(exc))

    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
