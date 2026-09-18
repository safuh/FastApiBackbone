"""Concrete provider configuration profiles for the optional AI layer.

The profiles describe how a generated application resolves provider configuration
without importing provider SDKs into the core AI contracts. Runtime adapters may
consume these profiles when they are composed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class AIProviderProfile:
    """Provider-specific configuration metadata owned by the application."""

    name: str
    api_key_environment: str | None
    base_url_environment: str | None
    default_base_url: str | None = None

    def __post_init__(self) -> None:
        normalized = self.name.strip().lower()
        if not normalized:
            raise ValueError("AI provider name cannot be empty")
        object.__setattr__(self, "name", normalized)


OPENAI_PROFILE: Final[AIProviderProfile] = AIProviderProfile(
    name="openai",
    api_key_environment="OPENAI_API_KEY",
    base_url_environment="OPENAI_BASE_URL",
)

GEMINI_PROFILE: Final[AIProviderProfile] = AIProviderProfile(
    name="gemini",
    api_key_environment="GEMINI_API_KEY",
    base_url_environment=None,
)

OLLAMA_PROFILE: Final[AIProviderProfile] = AIProviderProfile(
    name="ollama",
    api_key_environment=None,
    base_url_environment="OLLAMA_BASE_URL",
    default_base_url="http://localhost:11434",
)

OPENAI_COMPATIBLE_PROFILE: Final[AIProviderProfile] = AIProviderProfile(
    name="openai-compatible",
    api_key_environment="OPENAI_COMPATIBLE_API_KEY",
    base_url_environment="OPENAI_COMPATIBLE_BASE_URL",
)

PROVIDER_PROFILES: Final[dict[str, AIProviderProfile]] = {
    profile.name: profile
    for profile in (
        OPENAI_PROFILE,
        GEMINI_PROFILE,
        OLLAMA_PROFILE,
        OPENAI_COMPATIBLE_PROFILE,
    )
}


def get_provider_profile(name: str) -> AIProviderProfile:
    """Return a normalized provider profile or raise a configuration error."""
    normalized = name.strip().lower()
    try:
        return PROVIDER_PROFILES[normalized]
    except KeyError as exc:
        raise ValueError(f"unknown AI provider profile: {normalized!r}") from exc
