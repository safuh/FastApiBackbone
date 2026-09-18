"""Deterministic project generation primitives used by the CLI."""

from __future__ import annotations

import re
from pathlib import Path

from .template_registry import get_template_profile
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
        output_root = self.output.resolve()
        target = (output_root / self.name).resolve()
        try:
            target.relative_to(output_root)
        except ValueError as exc:
            raise GenerationError(
                f"project name escapes output directory: {self.name!r}"
            ) from exc

        if target == output_root:
            raise GenerationError("project name must create a child directory")

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
        get_template_profile("ai" if self.include_ai else "default")
        files = list(
            render_default_template(
                self.package,
                self.name,
                include_ai=self.include_ai,
            )
        )
        if self.include_ai:
            ai_test = (
                f"from {self.package}.ai.configuration import AISettings\n\n"
                "\n"
                "def test_ai_profile_configuration_is_optional() -> None:\n"
                "    settings = AISettings(enabled=False)\n"
                "    assert settings.enabled is False\n"
            )
            files.append(TemplateFile("tests/test_ai.py", ai_test))
            structured_test = f'''from types import SimpleNamespace

from pydantic import BaseModel

from {self.package}.ai.structured import create_structured_agent


class Answer(BaseModel):
    value: str


def test_structured_agent_template_uses_declared_output_type(monkeypatch) -> None:
    class FakeAgent:
        def __init__(self, *, model, output_type) -> None:
            self.model = model
            self.output_type = output_type

    monkeypatch.setitem(
        __import__("sys").modules,
        "pydantic_ai",
        SimpleNamespace(Agent=FakeAgent),
    )

    agent = create_structured_agent("openai:gpt-4o-mini", Answer)

    assert agent.model == "openai:gpt-4o-mini"
    assert agent.output_type is Answer


def test_structured_agent_template_rejects_empty_model() -> None:
    try:
        create_structured_agent("", Answer)
    except ValueError as exc:
        assert str(exc) == "AI model identifier cannot be empty"
    else:
        raise AssertionError("empty AI model should fail")
'''
            files.append(TemplateFile("tests/test_ai_structured.py", structured_test))
            dependency_test = f'''from types import SimpleNamespace

from {self.package}.ai.dependencies import AIRequestContext, AIServiceDependencies


class FakeProvider:
    async def generate(self, request):  # type: ignore[no-untyped-def]
        raise NotImplementedError


class FakeRepository:
    def __init__(self, session) -> None:  # type: ignore[no-untyped-def]
        self.session = session


def test_ai_request_context_binds_provider_repository_and_request_metadata() -> None:
    session = SimpleNamespace()
    provider = FakeProvider()

    def repository_factory(repository_type, bound_session):  # type: ignore[no-untyped-def]
        return repository_type(bound_session)

    context = AIServiceDependencies(
        provider=provider,
        repository_factory=repository_factory,
    ).for_request(
        request_id="req-123",
        session=session,
        subject="user-123",
        metadata={{"source": "test"}},
    )

    assert isinstance(context, AIRequestContext)
    assert context.request_id == "req-123"
    assert context.session is session
    assert context.provider is provider
    assert context.subject == "user-123"
    assert context.metadata == {{"source": "test"}}
    assert context.repository(FakeRepository).session is session
'''
            files.append(TemplateFile("tests/test_ai_dependencies.py", dependency_test))
            tools_test = f'''from {self.package}.ai import AITool, AIToolRegistry, AIToolRuntime
from {self.package}.ai.errors import AIError


async def test_ai_tool_runtime_enforces_allowlist() -> None:
    registry = AIToolRegistry()
    registry.register(AITool(name="echo", handler=lambda arguments: arguments["value"]))
    runtime = AIToolRuntime(registry, allowlist=set(("echo",)))

    assert await runtime.execute("echo", {{"value": "hello"}}) == "hello"

    try:
        await runtime.execute("delete", {{}})
    except AIError as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("unallowlisted tool should fail")
'''
            files.append(TemplateFile("tests/test_ai_tools.py", tools_test))
            streaming_test = f'''from {self.package}.ai import (
    AIModel,
    AIRequest,
    AIStreamChunk,
    AIStreamingProvider,
)


async def test_ai_streaming_template_preserves_chunk_order() -> None:
    model = AIModel(provider="example", model="example-model")
    request = AIRequest(prompt="hello", model=model)

    class FakeProvider:
        async def _chunks(self):
            yield AIStreamChunk(content="hello ", model=model)
            yield AIStreamChunk(content="world", model=model)
            yield AIStreamChunk(content="", model=model, is_final=True)

        def stream(self, request):
            return self._chunks()

    provider: AIStreamingProvider = FakeProvider()
    chunks = [chunk async for chunk in provider.stream(request)]

    assert [chunk.content for chunk in chunks] == ["hello ", "world", ""]
    assert [chunk.is_final for chunk in chunks] == [False, False, True]
    assert all(chunk.model == model for chunk in chunks)
'''
            files.append(TemplateFile("tests/test_ai_streaming.py", streaming_test))
            routing_policy_test = f'''import pytest

from {self.package}.ai import AIModelRoutePolicy, AIModelRouter, AIProviderRegistry
from {self.package}.ai.errors import AIConfigurationError


def router() -> AIModelRouter:
    return AIModelRouter(AIProviderRegistry())


def test_generated_ai_routing_policy_resolves_logical_route() -> None:
    policy = AIModelRoutePolicy({{"default": "OPENAI:gpt-test"}})
    model = policy.resolve(" DEFAULT ", router())

    assert model.provider == "openai"
    assert model.model == "gpt-test"


def test_generated_ai_routing_policy_rejects_unknown_route() -> None:
    policy = AIModelRoutePolicy({{"default": "openai:gpt-test"}})

    with pytest.raises(AIConfigurationError, match="not configured"):
        policy.resolve("missing", router())
'''
            files.append(TemplateFile("tests/test_ai_routing_policy.py", routing_policy_test))
            telemetry_test = f'''import pytest

from {self.package}.ai import (
    AIModel,
    AIModelPricing,
    AIRequest,
    AIResponse,
    AIUsageTelemetry,
)


def test_generated_ai_telemetry_records_usage_and_cost() -> None:
    telemetry = AIUsageTelemetry(
        {{"gpt-test": AIModelPricing(input_cost_per_token=0.001, output_cost_per_token=0.002)}}
    )
    model = AIModel(provider="openai", model="gpt-test")
    usage = telemetry.observe(
        AIRequest(prompt="hello", model=model),
        AIResponse(
            content="world",
            model=model,
            input_tokens=10,
            output_tokens=5,
        ),
        latency_seconds=1.25,
    )

    assert usage.total_tokens == 15
    assert usage.latency_seconds == 1.25
    assert usage.estimated_cost == pytest.approx(0.02)
'''
            files.append(TemplateFile("tests/test_ai_telemetry.py", telemetry_test))
        return tuple(files)
