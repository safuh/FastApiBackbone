"""Provider-neutral AI usage and cost telemetry.

Telemetry records usage facts at the application boundary. Pricing is supplied
explicitly by the application so provider-specific prices do not leak into the
AI contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from .contracts import AIRequest, AIResponse
from .errors import AIConfigurationError


@dataclass(frozen=True, slots=True)
class AIModelPricing:
    """Per-token pricing used only for estimated-cost calculation."""

    input_cost_per_token: float = 0.0
    output_cost_per_token: float = 0.0

    def __post_init__(self) -> None:
        if self.input_cost_per_token < 0 or self.output_cost_per_token < 0:
            raise AIConfigurationError("AI token pricing cannot be negative")


@dataclass(frozen=True, slots=True)
class AIUsage:
    """Normalized usage facts for one completed AI generation."""

    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    latency_seconds: float
    estimated_cost: float | None

    @property
    def total_tokens(self) -> int | None:
        if self.input_tokens is None or self.output_tokens is None:
            return None
        return self.input_tokens + self.output_tokens


class AIUsageTelemetry:
    """Collect immutable usage records for application-level telemetry."""

    def __init__(self, pricing: dict[str, AIModelPricing] | None = None) -> None:
        self._pricing = {
            self._normalize_model(key): value for key, value in (pricing or {}).items()
        }
        self._records: list[AIUsage] = []

    @staticmethod
    def _normalize_model(model: str) -> str:
        normalized = model.strip().lower()
        if not normalized:
            raise AIConfigurationError("AI model name cannot be empty")
        return normalized

    def observe(
        self,
        request: AIRequest,
        response: AIResponse,
        latency_seconds: float,
    ) -> AIUsage:
        """Record one response and return its normalized usage facts."""
        if latency_seconds < 0:
            raise AIConfigurationError("AI latency cannot be negative")
        if response.input_tokens is not None and response.input_tokens < 0:
            raise AIConfigurationError("AI input token count cannot be negative")
        if response.output_tokens is not None and response.output_tokens < 0:
            raise AIConfigurationError("AI output token count cannot be negative")

        key = self._normalize_model(response.model.model)
        pricing = self._pricing.get(key)
        estimated_cost = None
        if (
            pricing is not None
            and response.input_tokens is not None
            and response.output_tokens is not None
        ):
            estimated_cost = (
                response.input_tokens * pricing.input_cost_per_token
                + response.output_tokens * pricing.output_cost_per_token
            )

        usage = AIUsage(
            provider=response.model.provider,
            model=response.model.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_seconds=latency_seconds,
            estimated_cost=estimated_cost,
        )
        self._records.append(usage)
        return usage

    def records(self) -> tuple[AIUsage, ...]:
        """Return an immutable snapshot of observed usage."""
        return tuple(self._records)

    def timed(self) -> AITelemetryTimer:
        """Create a monotonic timer for a generation boundary."""
        return AITelemetryTimer()


@dataclass(slots=True)
class AITelemetryTimer:
    """Monotonic timer used to measure provider-independent latency."""

    started_at: float = 0.0

    def __post_init__(self) -> None:
        if self.started_at == 0.0:
            self.started_at = monotonic()

    def elapsed_seconds(self) -> float:
        """Return elapsed monotonic time in seconds."""
        return max(0.0, monotonic() - self.started_at)
