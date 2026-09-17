"""Command-line entry point for the FastAPI Backbone project generator."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .generator import GenerationError, ProjectGenerator


class DatabaseCommandError(RuntimeError):
    """Raised when a database helper command cannot be executed."""


class ClientGenerationError(RuntimeError):
    """Raised when an OpenAPI client cannot be generated."""


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

    doctor = subparsers.add_parser(
        "doctor",
        help="Check a generated project for required foundation files.",
    )
    doctor.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Project directory to diagnose (default: current directory).",
    )

    client = subparsers.add_parser(
        "client", help="Generate a client from an OpenAPI document."
    )
    client_subparsers = client.add_subparsers(dest="client_command", required=True)
    generate = client_subparsers.add_parser(
        "generate", help="Generate a Python client with openapi-python-client."
    )
    source = generate.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--spec", type=Path, help="Path to an OpenAPI JSON or YAML document."
    )
    source.add_argument("--url", help="URL serving an OpenAPI JSON or YAML document.")
    generate.add_argument(
        "--output",
        type=Path,
        default=Path("client"),
        help="Output directory for the generated client (default: ./client).",
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


def _generate_client(
    *,
    spec: Path | None,
    url: str | None,
    output: Path,
) -> int:
    """Generate a Python client using the external openapi-python-client tool."""
    executable = shutil.which("openapi-python-client")
    if executable is None:
        raise ClientGenerationError(
            "openapi-python-client is required; install it before generating a client"
        )

    output_path = output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Generated services use uv, so keep the generated client metadata compatible
    # with the same workflow rather than relying on the generator default metadata
    # backend.
    config_path = output_path.parent / ".openapi-python-client.yml"
    config_path.write_text(
        "post_hooks:\n  - ruff check . --fix\n  - ruff format .\n",
        encoding="utf-8",
    )

    arguments = [
        executable,
        "generate",
        "--meta",
        "uv",
        "--config",
        str(config_path),
        "--output-path",
        str(output_path),
    ]
    if spec is not None:
        arguments.extend(["--path", str(spec.resolve())])
    elif url is not None:
        arguments.extend(["--url", url])
    else:  # pragma: no cover - argparse enforces this
        raise ClientGenerationError("exactly one of --spec or --url is required")

    return subprocess.run(arguments, check=False).returncode


def _doctor(project_root: Path) -> int:
    """Diagnose the structural health of a generated project without mutating it."""
    root = project_root.resolve()
    checks = {
        "project directory": root.is_dir(),
        "pyproject.toml": (root / "pyproject.toml").is_file(),
        "alembic.ini": (root / "alembic.ini").is_file(),
        "alembic environment": (root / "alembic" / "env.py").is_file(),
        "source package": any(
            path.is_dir() and (path / "__init__.py").is_file()
            for path in (root / "src").glob("*")
        ) if (root / "src").is_dir() else False,
        "tests": (root / "tests").is_dir(),
    }
    failed = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        status = "OK" if passed else "FAIL"
        print(f"[{status}] {name}")
    if failed:
        print(f"Doctor found {len(failed)} issue(s) in {root}")
        return 1
    print(f"Doctor found no structural issues in {root}")
    return 0


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

    if args.command == "doctor":
        return _doctor(args.path)

    if args.command == "client" and args.client_command == "generate":
        try:
            return _generate_client(
                spec=args.spec,
                url=args.url,
                output=args.output,
            )
        except ClientGenerationError as exc:
            parser.error(str(exc))

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
