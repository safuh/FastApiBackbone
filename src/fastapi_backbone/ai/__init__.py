"""Provider-agnostic AI architecture contracts and infrastructure.

This package intentionally contains no concrete model-provider SDK dependency.
Generated applications can use Pydantic AI behind these application-facing
contracts without coupling domain code to a vendor.
"""

from .configuration import AISettings
from .contracts import AIModel, AIProvider, AIRequest, AIResponse
from .model_router import AIModelRouter, ModelRoute
from .providers import AIProviderRegistry
from .profiles import (
    GEMINI_PROFILE,
    OLLAMA_PROFILE,
    OPENAI_COMPATIBLE_PROFILE,
    OPENAI_PROFILE,
    AIProviderProfile,
    get_provider_profile,
)

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
    "get_provider_profile",
]
