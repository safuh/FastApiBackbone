from collections.abc import Mapping

import pytest

from fastapi_backbone.ai import AITool, AIToolRegistry, AIToolRuntime
from fastapi_backbone.ai.errors import AIConfigurationError, AIError


async def test_tool_runtime_executes_only_allowlisted_tools() -> None:
    calls: list[Mapping[str, object]] = []
    registry = AIToolRegistry()

    async def echo(arguments: Mapping[str, object]) -> dict[str, object]:
        calls.append(arguments)
        return {"echo": arguments["value"]}

    registry.register(AITool(name="echo", handler=echo))
    registry.register(AITool(name="delete", handler=lambda _: "deleted"))

    runtime = AIToolRuntime(registry, allowlist={"echo"})

    result = await runtime.execute("ECHO", {"value": "hello"})

    assert result == {"echo": "hello"}
    assert calls == [{"value": "hello"}]
    assert runtime.allowed_tools() == ("echo",)


async def test_tool_runtime_rejects_unallowlisted_tool() -> None:
    registry = AIToolRegistry()
    registry.register(AITool(name="echo", handler=lambda _: "ok"))
    runtime = AIToolRuntime(registry, allowlist=set())

    with pytest.raises(AIError, match="not allowed"):
        await runtime.execute("echo", {})


async def test_tool_runtime_applies_application_authorization() -> None:
    registry = AIToolRegistry()
    registry.register(AITool(name="echo", handler=lambda _: "ok"))
    runtime = AIToolRuntime(
        registry,
        allowlist={"echo"},
        authorizer=lambda subject, name: subject == "allowed-user",
    )

    assert await runtime.execute("echo", {}, subject="allowed-user") == "ok"

    with pytest.raises(AIError, match="not authorized"):
        await runtime.execute("echo", {}, subject="denied-user")


def test_tool_runtime_rejects_unknown_allowlist_entry() -> None:
    registry = AIToolRegistry()
    registry.register(AITool(name="echo", handler=lambda _: "ok"))

    with pytest.raises(
        AIConfigurationError,
        match="allowlist contains unregistered tools",
    ):
        AIToolRuntime(registry, allowlist={"missing"})
