# Core Module

The core module owns cross-cutting infrastructure and the application lifecycle.

## Responsibilities

- Typed environment configuration with Pydantic Settings.
- Async SQLAlchemy engine/session construction.
- FastAPI application lifespan and resource cleanup.
- Structured logging configuration.

## Boundaries

Core must remain domain-neutral. It must not contain user, billing, order, AI, or other business entities.

Application code may consume core abstractions. Core should not import consuming application modules.

## Production requirements

Before v1.0, this module must add correlation IDs, a formal exception taxonomy, integration fixtures, safe CORS configuration, and complete type-checking coverage. See [`../../MILESTONES.md`](../../MILESTONES.md).
