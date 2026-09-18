"""Provider-neutral AI resilience policy.

This module owns application-level retry, timeout, circuit-breaker, and fallback
semantics. Provider SDKs remain behind the AIProvider port.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from dataclasses import dataclass

from .contracts import AIProvider, AIRequest, AIResponse
from .errors import AIError


class AICircuitOpenError(AIError):
    """Raised when a circuit is open and execution is rejected."""


class AIResilienceError(AIError):
    """Raised when all resilience attempts and fallbacks fail."""


@dataclass(frozen=True, slots=True)
class AIResiliencePolicy:
    """Bounded application-level execution policy."""

    timeout_seconds: float = 30.0
    max_retries: int = 2
    failure_threshold: int = 3
    recovery_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be at least one")
        if self.recovery_seconds <= 0:
            raise ValueError("recovery_seconds must be greater than zero")


class AICircuitBreaker:
    """Small circuit breaker with closed and open states plus timed recovery."""

    def __init__(self, *, failure_threshold: int = 3, recovery_seconds: float = 30.0) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least one")
        if recovery_seconds <= 0:
            raise ValueError("recovery_seconds must be greater than zero")
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._failures = 0
        self._opened_at: float | None = None

    @property
    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        return time.monotonic() - self._opened_at < self._recovery_seconds

    def before_call(self) -> None:
        if self.is_open:
            raise AICircuitOpenError("AI circuit is open")

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._opened_at = time.monotonic()


class ResilientAIProvider:
    """Wrap a provider with timeout, retries, circuit breaking, and fallbacks."""

    def __init__(
        self,
        provider: AIProvider,
        *,
        policy: AIResiliencePolicy | None = None,
        fallbacks: Sequence[AIProvider] = (),
        circuit: AICircuitBreaker | None = None,
    ) -> None:
        self._provider = provider
        self._policy = policy or AIResiliencePolicy()
        self._fallbacks = tuple(fallbacks)
        self._circuit = circuit or AICircuitBreaker(
            failure_threshold=self._policy.failure_threshold,
            recovery_seconds=self._policy.recovery_seconds,
        )

    @property
    def circuit(self) -> AICircuitBreaker:
        return self._circuit

    async def generate(self, request: AIRequest) -> AIResponse:
        """Execute primary attempts, then ordered fallbacks if configured."""
        try:
            self._circuit.before_call()
            response = await self._attempt(self._provider, request)
        except Exception as primary_error:
            self._circuit.record_failure()
            for fallback in self._fallbacks:
                try:
                    response = await self._attempt(fallback, request)
                    self._circuit.record_success()
                    return response
                except Exception:
                    continue
            raise AIResilienceError(
                "AI provider and all configured fallbacks failed"
            ) from primary_error
        self._circuit.record_success()
        return response

    async def _attempt(self, provider: AIProvider, request: AIRequest) -> AIResponse:
        last_error: Exception | None = None
        for attempt in range(self._policy.max_retries + 1):
            try:
                return await asyncio.wait_for(
                    provider.generate(request),
                    timeout=self._policy.timeout_seconds,
                )
            except Exception as exc:
                last_error = exc
                if attempt < self._policy.max_retries:
                    await asyncio.sleep(0)
        assert last_error is not None
        raise last_error
