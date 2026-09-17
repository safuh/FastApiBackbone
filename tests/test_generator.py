import sys
from importlib import import_module
from pathlib import Path

import pytest

from fastapi_backbone.generator import GenerationError, ProjectGenerator
from fastapi_backbone.template_registry import TEMPLATE_PROFILES, get_template_profile


def test_template_registry_has_default_and_ai_profiles() -> None:
    assert {profile.name for profile in TEMPLATE_PROFILES} == {"default", "ai"}
    assert get_template_profile("default").ai_enabled is False
    assert get_template_profile("ai").ai_enabled is True
    assert get_template_profile("default").version == get_template_profile("ai").version


def test_template_registry_rejects_unknown_profile() -> None:
    with pytest.raises(ValueError, match="unknown template profile"):
        get_template_profile("unknown")


def test_generator_creates_production_project(tmp_path: Path) -> None:
    target = ProjectGenerator("billing-api", tmp_path).generate()

    assert target == (tmp_path / "billing-api").resolve()
    assert (target / "src/billing_api/app.py").exists()
    assert (target / "src/billing_api/core/database.py").exists()
    assert (target / "src/billing_api/auth/application.py").exists()
    assert (target / "src/billing_api/identity/models.py").exists()
    assert (target / "alembic/env.py").exists()
    assert (target / "alembic/versions/0001_initial.py").exists()
    assert (target / "Dockerfile").exists()
    assert (target / ".github/workflows/ci.yml").exists()
    assert (target / "tests/test_app.py").exists()
    assert not (target / "src/billing_api/ai").exists()


def test_generated_default_project_imports_without_ai_dependency(tmp_path: Path) -> None:
    target = ProjectGenerator("generated-api", tmp_path).generate()
    sys.path.insert(0, str(target / "src"))
    try:
        app_module = import_module("generated_api.app")
        assert app_module.create_app is not None
    finally:
        sys.path.remove(str(target / "src"))
        for module_name in tuple(sys.modules):
            if module_name == "generated_api" or module_name.startswith("generated_api."):
                del sys.modules[module_name]


def test_generator_ai_profile_is_optional(tmp_path: Path) -> None:
    target = ProjectGenerator("ai-api", tmp_path, include_ai=True).generate()

    ai_root = target / "src/ai_api/ai"
    expected_ai_files = (
        "__init__.py",
        "configuration.py",
        "contracts.py",
        "errors.py",
        "model_router.py",
        "providers.py",
        "pydantic_ai_adapter.py",
    )

    assert all((ai_root / path).exists() for path in expected_ai_files)
    assert "pydantic-ai" in (target / "pyproject.toml").read_text(encoding="utf-8")


def test_generator_ai_profile_renders_canonical_sources(tmp_path: Path) -> None:
    target = ProjectGenerator("ai-api", tmp_path, include_ai=True).generate()
    canonical_root = Path(__file__).parents[1] / "src" / "fastapi_backbone" / "ai"
    generated_root = target / "src" / "ai_api" / "ai"

    for source in canonical_root.glob("*.py"):
        generated = generated_root / source.name
        assert generated.exists()
        expected = source.read_text(encoding="utf-8").replace("fastapi_backbone", "ai_api")
        assert generated.read_text(encoding="utf-8") == expected


def test_generator_rejects_non_empty_target(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    (target / "important.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(GenerationError, match="not empty"):
        ProjectGenerator("existing", tmp_path).generate()


def test_generator_rejects_path_escape(tmp_path: Path) -> None:
    with pytest.raises(GenerationError, match="escapes output directory"):
        ProjectGenerator("../escaped", tmp_path).generate()

    assert not (tmp_path.parent / "escaped").exists()


def test_generator_allows_existing_empty_target(tmp_path: Path) -> None:
    target = tmp_path / "empty"
    target.mkdir()

    ProjectGenerator("empty", tmp_path, force=True).generate()
    assert (target / "README.md").exists()
