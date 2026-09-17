"""Provider-agnostic AI architecture contracts and infrastructure.

This package intentionally contains no concrete model-provider SDK dependency.
Generated applications can use Pydantic AI behind these application-facing
contracts without coupling domain code to a vendor.
"""

from .configuration import AISettings
from .contracts import AIModel, AIProvider, AIRequest, AIResponse
from .model_router import AIModelRouter, ModelRoute
from .providers import AIProviderRegistry

__all__ = [
    "AIModel",
    "AIModelRouter",
    "AIProvider",
    "AIProviderRegistry",
    "AIRequest",
    "AIResponse",
    "AISettings",
    "ModelRoute",
]
