"""Provider-agnostic AI architecture contracts and infrastructure.

This package intentionally contains no concrete model-provider SDK dependency.
Generated applications can use Pydantic AI behind these application-facing
contracts without coupling domain code to a vendor.
"""

from .configuration import AISettings
from .contracts import (
    AIModel,
    AIProvider,
    AIRequest,
    AIResponse,
    AIStreamChunk,
    AIStreamingProvider,
)
from .dependencies import AIRequestContext, AIServiceDependencies, RepositoryFactory
from .model_router import AIModelRouter, ModelRoute
from .profiles import (
    GEMINI_PROFILE,
    OLLAMA_PROFILE,
    OPENAI_COMPATIBLE_PROFILE,
    OPENAI_PROFILE,
    AIProviderProfile,
    get_provider_profile,
)
from .providers import AIProviderRegistry
from .resilience import (
    AICircuitBreaker,
    AICircuitOpenError,
    AIResilienceError,
    AIResiliencePolicy,
    ResilientAIProvider,
)
from .routing_policy import AIModelRoutePolicy
from .structured import create_structured_agent
from .telemetry import AIModelPricing, AIUsage, AIUsageTelemetry
from .tools import AITool, AIToolRegistry, AIToolRuntime

__all__ = [
    "AIModel",
    "AIModelRouter",
    "AIModelRoutePolicy",
    "AIProvider",
    "AIProviderRegistry",
    "AIRequest",
    "AIRequestContext",
    "AIResponse",
    "AIServiceDependencies",
    "AISettings",
    "AIStreamChunk",
    "AIStreamingProvider",
    "AIModelPricing",
    "AIUsage",
    "AIUsageTelemetry",
    "AITool",
    "AIToolRegistry",
    "AIToolRuntime",
    "AIProviderProfile",
    "AICircuitBreaker",
    "AICircuitOpenError",
    "AIResilienceError",
    "AIResiliencePolicy",
    "GEMINI_PROFILE",
    "OLLAMA_PROFILE",
    "OPENAI_COMPATIBLE_PROFILE",
    "ModelRoute",
    "RepositoryFactory",
    "OPENAI_PROFILE",
    "ResilientAIProvider",
    "create_structured_agent",
    "get_provider_profile",
]
