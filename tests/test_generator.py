from pathlib import Path

import pytest

from fastapi_backbone.generator import GenerationError, ProjectGenerator


def test_generator_creates_basic_project(tmp_path: Path) -> None:
    target = ProjectGenerator("billing-api", tmp_path).generate()

    assert target == (tmp_path / "billing-api").resolve()
    assert (target / "src/billing_api/app.py").exists()
    assert (target / "tests/test_app.py").exists()
    assert not (target / "src/billing_api/ai").exists()


def test_generator_ai_profile_is_optional(tmp_path: Path) -> None:
    target = ProjectGenerator("ai-api", tmp_path, include_ai=True).generate()

    assert (target / "src/ai_api/ai/agent.py").exists()
    assert "pydantic-ai" in (target / "pyproject.toml").read_text()


def test_generator_rejects_non_empty_target(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    (target / "important.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(GenerationError, match="not empty"):
        ProjectGenerator("existing", tmp_path).generate()


def test_generator_allows_existing_empty_target(tmp_path: Path) -> None:
    target = tmp_path / "empty"
    target.mkdir()

    ProjectGenerator("empty", tmp_path, force=True).generate()
    assert (target / "README.md").exists()
