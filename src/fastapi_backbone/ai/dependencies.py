"""Dependency-injection contracts for AI application services.

The contract keeps request-scoped infrastructure explicit while leaving concrete
repositories, authentication, and HTTP framework details in the composition root.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from .contracts import AIProvider

RepositoryT = TypeVar("RepositoryT")


class RepositoryFactory(Protocol):
    """Create a repository bound to the current request transaction."""

    def __call__(
        self,
        repository_type: type[RepositoryT],
        session: AsyncSession,
    ) -> RepositoryT:
        """Return a repository using the supplied transaction session."""
        ...


@dataclass(frozen=True, slots=True)
class AIRequestContext:
    """Request-scoped dependencies available to AI application services."""

    request_id: str
    session: AsyncSession
    provider: AIProvider
    repository_factory: RepositoryFactory | None = None
    subject: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def repository(self, repository_type: type[RepositoryT]) -> RepositoryT:
        """Resolve a repository against this context's transaction."""
        if self.repository_factory is None:
            raise RuntimeError("repository factory is not configured")
        return self.repository_factory(repository_type, self.session)


@dataclass(frozen=True, slots=True)
class AIServiceDependencies:
    """Stable constructor dependencies for an AI application service."""

    provider: AIProvider
    repository_factory: RepositoryFactory | None = None

    def for_request(
        self,
        *,
        request_id: str,
        session: AsyncSession,
        subject: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AIRequestContext:
        """Create explicit request-scoped context from application dependencies."""
        return AIRequestContext(
            request_id=request_id,
            session=session,
            provider=self.provider,
            repository_factory=self.repository_factory,
            subject=subject,
            metadata={} if metadata is None else dict(metadata),
        )
