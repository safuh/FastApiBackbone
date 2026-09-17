"""Provider-agnostic AI architecture contracts.

This module intentionally contains no concrete model-provider SDK dependency.
Generated applications can use Pydantic AI behind these application-facing
contracts without coupling domain code to a vendor.
"""

from .contracts import AIModel, AIProvider, AIRequest, AIResponse

__all__ = ["AIModel", "AIProvider", "AIRequest", "AIResponse"]
