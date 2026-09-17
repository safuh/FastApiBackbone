"""Optional Pydantic AI runtime adapter.

This module is the only Backbone AI module that imports Pydantic AI. The core
contracts and application services remain independent of the runtime.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi_backbone.ai.contracts import AIRequest, AIResponse


class PydanticAIProvider:
    """Adapt Pydantic AI's Agent runtime to the Backbone AIProvider port."""

    def __init__(self, *, timeout_seconds: float = 30.0, max_retries: int = 2) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        try:
            from pydantic_ai import Agent
        except ImportError as exc:  # pragma: no cover - exercised in optional envs
            raise RuntimeError(
                "Pydantic AI is not installed; install fastapi-backbone[ai]"
            ) from exc

        self._agent_type = Agent
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._agents: dict[str, Any] = {}

    def _agent_for(self, model_identifier: str) -> Any:
        agent = self._agents.get(model_identifier)
        if agent is None:
            agent = self._agent_type(model_identifier, retries=self._max_retries)
            self._agents[model_identifier] = agent
        return agent

    async def generate(self, request: AIRequest) -> AIResponse:
        """Run the configured Pydantic AI model and normalize its text output."""
        identifier = f"{request.model.provider}:{request.model.model}"
        result = await asyncio.wait_for(
            self._agent_for(identifier).run(request.prompt, metadata=request.metadata),
            timeout=self._timeout_seconds,
        )
        return AIResponse(
            content=str(result.output),
            model=request.model,
            metadata={"runtime": "pydantic-ai"},
        )
