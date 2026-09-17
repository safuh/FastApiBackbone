"""Deterministic project generation primitives used by the CLI."""

from __future__ import annotations

import re
from pathlib import Path

from .templates import TemplateFile, render_default_template


class GenerationError(ValueError):
    """Raised when a project cannot be generated safely."""


class ProjectGenerator:
    """Generate a testable FastAPI project from versioned templates."""

    def __init__(
        self,
        name: str,
        output: Path,
        include_ai: bool = False,
        force: bool = False,
    ):
        self.name = name
        self.output = output
        self.include_ai = include_ai
        self.force = force
        self.package = self._package_name(name)

    @staticmethod
    def _package_name(name: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-").lower()
        package = normalized.replace("-", "_")
        if not package or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", package):
            raise GenerationError(f"invalid project name: {name!r}")
        return package

    def generate(self) -> Path:
        target = (self.output / self.name).resolve()
        if target.exists():
            if not target.is_dir():
                raise GenerationError(f"target exists and is not a directory: {target}")
            if any(target.iterdir()) and not self.force:
                raise GenerationError(f"target directory is not empty: {target}")
        else:
            target.mkdir(parents=True, exist_ok=True)

        for template in self._files():
            destination = target / template.path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(template.content, encoding="utf-8")
        return target

    def _files(self) -> tuple[TemplateFile, ...]:
        files = list(
            render_default_template(
                self.package,
                self.name,
                include_ai=self.include_ai,
            )
        )
        if self.include_ai:
            ai_test = (
                "import pytest\n\n"
                "\n"
                "def test_ai_profile_is_optional() -> None:\n"
                "    pytest.importorskip(\"pydantic_ai\")\n"
                f"    from {self.package}.ai.configuration import AISettings\n\n"
                "    settings = AISettings(enabled=False)\n"
                "    assert settings.enabled is False\n"
            )
            files.append(TemplateFile("tests/test_ai.py", ai_test))
        return tuple(files)
