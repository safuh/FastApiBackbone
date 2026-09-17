"""Command-line entry point for the FastAPI Backbone project generator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import GenerationError, ProjectGenerator


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

    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
