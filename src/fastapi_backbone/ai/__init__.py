"""Provider-agnostic AI architecture contracts and infrastructure.

This package intentionally contains no concrete model-provider SDK dependency.
Generated applications can use Pydantic AI behind these application-facing
contracts without coupling domain code to a vendor.
"""

from .configuration import AISettings
from .contracts import AIModel, AIProvider, AIRequest, AIResponse
from .model_router import AIModelRouter, ModelRoute
from .profiles import (
    AIProviderProfile,
    GEMINI_PROFILE,
    OLLAMA_PROFILE,
    OPENAI_COMPATIBLE_PROFILE,
    OPENAI_PROFILE,
    get_provider_profile,
)
from .providers import AIProviderRegistry
from .structured import create_structured_agent

__all__ = [
    "AIModel",
    "AIModelRouter",
    "AIProvider",
    "AIProviderRegistry",
    "AIRequest",
    "AIResponse",
    "AISettings",
    "AIProviderProfile",
    "GEMINI_PROFILE",
    "OLLAMA_PROFILE",
    "OPENAI_COMPATIBLE_PROFILE",
    "OPENAI_PROFILE",
    "ModelRoute",
    "create_structured_agent",
    "get_provider_profile",
]
