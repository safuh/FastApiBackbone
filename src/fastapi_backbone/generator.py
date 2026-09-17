"""Deterministic project generation primitives used by the CLI."""

from __future__ import annotations

import re
from pathlib import Path

from .templates import TemplateFile, render_default_template


class GenerationError(ValueError):
    """Raised when a project cannot be generated safely."""


class ProjectGenerator:
    """Generate a testable FastAPI project from versioned templates."""

    def __init__(self, name: str, output: Path, include_ai: bool = False, force: bool = False):
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
        files = list(render_default_template(self.package, self.name))
        if self.include_ai:
            files.extend(
                (
                    TemplateFile(f"src/{self.package}/ai/__init__.py", AI_INIT_TEMPLATE),
                    TemplateFile(f"src/{self.package}/ai/agent.py", AI_AGENT_TEMPLATE),
                    TemplateFile(f"src/{self.package}/ai/config.py", AI_CONFIG_TEMPLATE),
                    TemplateFile("tests/test_ai.py", AI_TEST_TEMPLATE.format(package=self.package)),
                )
            )
        return tuple(files)


AI_INIT_TEMPLATE = '''"""Optional AI application architecture."""\n\nfrom .agent import create_agent\n\n__all__ = ["create_agent"]\n'''

AI_CONFIG_TEMPLATE = '''"""AI configuration kept separate from business logic."""\n\nfrom pydantic_settings import BaseSettings, SettingsConfigDict\n\n\nclass AISettings(BaseSettings):\n    model_config = SettingsConfigDict(env_prefix="AI_", extra="ignore")\n\n    enabled: bool = False\n    model: str = ""\n    timeout_seconds: float = 30.0\n    max_retries: int = 2\n'''

AI_AGENT_TEMPLATE = '''"""Pydantic AI boundary for the generated application."""\n\nfrom pydantic_ai import Agent\n\n\ndef create_agent(model: str) -> Agent:\n    """Create an agent from a runtime model identifier."""\n    return Agent(model=model)\n'''

AI_TEST_TEMPLATE = '''import pytest\n\n\ndef test_ai_profile_is_optional() -> None:\n    pytest.importorskip("pydantic_ai")\n    from {package}.ai.agent import create_agent\n\n    assert create_agent is not None\n'''
