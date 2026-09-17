import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from fastapi_backbone.cli import (
    ClientGenerationError,
    DatabaseCommandError,
    _doctor,
    _generate_client,
    _run_alembic,
    build_parser,
)


def test_db_parser_defaults_upgrade_to_head() -> None:
    args = build_parser().parse_args(["db", "upgrade"])
    assert args.command == "db"
    assert args.db_command == "upgrade"
    assert args.revision == "head"


def test_db_parser_defaults_downgrade_to_one_revision() -> None:
    args = build_parser().parse_args(["db", "downgrade"])
    assert args.revision == "-1"


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["db", "upgrade", "2026_revision"], ["upgrade", "2026_revision"]),
        (["db", "downgrade", "base"], ["downgrade", "base"]),
        (["db", "current"], ["current"]),
        (["db", "history"], ["history"]),
    ],
)
def test_db_parser_preserves_alembic_arguments(
    argv: list[str], expected: list[str]
) -> None:
    args = build_parser().parse_args(argv)
    arguments = [args.db_command]
    if args.db_command in {"upgrade", "downgrade"}:
        arguments.append(args.revision)
    assert arguments == expected


def test_run_alembic_sets_generated_src_on_pythonpath(tmp_path: Path) -> None:
    (tmp_path / "alembic.ini").write_text("[alembic]\n", encoding="utf-8")
    (tmp_path / "src").mkdir()

    with patch("fastapi_backbone.cli.subprocess.run") as run:
        run.return_value.returncode = 0
        result = _run_alembic(["current"], tmp_path)

    assert result == 0
    call = run.call_args
    assert call.args[0] == [sys.executable, "-m", "alembic", "current"]
    assert call.kwargs["cwd"] == tmp_path.resolve()
    assert str(tmp_path / "src") in call.kwargs["env"]["PYTHONPATH"]


def test_run_alembic_requires_project_config(tmp_path: Path) -> None:
    with pytest.raises(DatabaseCommandError, match="alembic.ini not found"):
        _run_alembic(["current"], tmp_path)


def test_doctor_accepts_a_healthy_generated_project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    (tmp_path / "alembic.ini").write_text("[alembic]\n", encoding="utf-8")
    (tmp_path / "alembic").mkdir()
    (tmp_path / "alembic" / "env.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "demo").mkdir(parents=True)
    (tmp_path / "src" / "demo" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    assert _doctor(tmp_path) == 0
    assert "Doctor found no structural issues" in capsys.readouterr().out


def test_doctor_returns_failure_for_missing_foundation_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")

    assert _doctor(tmp_path) == 1
    output = capsys.readouterr().out
    assert "[FAIL] alembic.ini" in output
    assert "Doctor found" in output


def test_doctor_parser_defaults_to_current_directory() -> None:
    args = build_parser().parse_args(["doctor"])
    assert args.command == "doctor"
    assert args.path == Path(".")


def test_client_parser_accepts_spec_and_output() -> None:
    args = build_parser().parse_args(
        [
            "client",
            "generate",
            "--spec",
            "openapi.json",
            "--output",
            "generated-client",
        ]
    )
    assert args.client_command == "generate"
    assert args.spec == Path("openapi.json")
    assert args.output == Path("generated-client")


def test_generate_client_uses_openapi_python_client(tmp_path: Path) -> None:
    spec = tmp_path / "openapi.json"
    spec.write_text("{}", encoding="utf-8")
    output = tmp_path / "client"

    with patch(
        "fastapi_backbone.cli.shutil.which",
        return_value="/usr/bin/openapi-python-client",
    ):
        with patch("fastapi_backbone.cli.subprocess.run") as run:
            run.return_value.returncode = 0
            assert _generate_client(spec=spec, url=None, output=output) == 0

    assert run.call_args.args[0] == [
        "/usr/bin/openapi-python-client",
        "generate",
        "--meta",
        "uv",
        "--config",
        str(output.parent / ".openapi-python-client.yml"),
        "--output-path",
        str(output.resolve()),
        "--path",
        str(spec.resolve()),
    ]
    assert run.call_args.kwargs["check"] is False
    assert (output.parent / ".openapi-python-client.yml").read_text(encoding="utf-8") == (
        "post_hooks:\n  - ruff check . --fix\n  - ruff format .\n"
    )


def test_generate_client_requires_external_tool(tmp_path: Path) -> None:
    with patch("fastapi_backbone.cli.shutil.which", return_value=None):
        with pytest.raises(ClientGenerationError, match="openapi-python-client is required"):
            _generate_client(
                spec=None,
                url="https://example.test/openapi.json",
                output=tmp_path / "client",
            )
