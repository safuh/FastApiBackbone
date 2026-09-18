"""Structured-output agent template for the optional Pydantic AI profile.

The Pydantic AI dependency remains optional and is imported only when an
application explicitly creates a structured-output agent.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

OutputT = TypeVar("OutputT", bound=BaseModel)


def create_structured_agent(
    model: str,
    output_type: type[OutputT],
) -> Any:
    """Create a Pydantic AI agent that validates responses into output_type.

    Provider/model selection remains runtime-configured through the existing
    provider:model identifier. Domain code supplies the output schema rather
    than embedding provider-specific response parsing.
    """
    if not model.strip():
        raise ValueError("AI model identifier cannot be empty")

    try:
        from pydantic_ai import Agent
    except ImportError as exc:
        raise RuntimeError(
            "structured AI agents require the optional ai dependency"
        ) from exc

    return Agent(model=model, output_type=output_type)
