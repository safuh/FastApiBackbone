"""Stable exceptions for the AI application boundary."""


class AIError(Exception):
    """Base class for expected AI-layer failures."""


class AIConfigurationError(AIError, ValueError):
    """Raised when AI configuration cannot be used safely."""


class AIProviderNotFoundError(AIError, LookupError):
    """Raised when a configured provider has no registered adapter."""


class AIProviderAlreadyRegisteredError(AIError, ValueError):
    """Raised when a provider name is registered more than once."""
