"""Typed configuration for the optional AI application profile."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class AISettings(BaseModel):
    """Application-level AI settings.

    Provider credentials and SDK-specific options belong in adapter-specific
    configuration, not in this provider-neutral contract.
    """

    enabled: bool = False
    model: str = ""
    timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=2, ge=0)

    @model_validator(mode="after")
    def validate_enabled_model(self) -> AISettings:
        if self.enabled and not self.model.strip():
            raise ValueError("AI model must be configured when AI is enabled")
        return self
