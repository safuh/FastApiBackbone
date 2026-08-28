# ADR 0001: Foundation Architecture

- Status: Accepted
- Date: 2026-08-28

## Context

FastAPI applications commonly repeat the same configuration, persistence, migration, authentication, testing, and deployment setup. A reusable foundation should reduce this repetition without becoming a domain-specific framework.

## Decision

FastAPI Backbone uses a src-layout Python package with these primary concerns:

1. FastAPI for the HTTP boundary.
2. Pydantic v2 for validation/configuration.
3. SQLAlchemy 2.x async APIs for persistence.
4. Alembic for schema migrations.
5. JWT/OAuth2 security primitives behind an explicit authentication boundary.
6. OpenAPI as the contract for generated clients, including Flutter.
7. Docker for reproducible application artifacts.
8. Kubernetes/Kustomize as an optional deployment target.
9. A generator/CLI as the long-term distribution mechanism.

The foundation remains domain-neutral. Product applications own business models, bounded contexts, and product-specific policies.

## Consequences

- The reference package is reusable without forcing Flutter or Kubernetes dependencies.
- Generated projects can own their source tree and evolve independently.
- Authentication can be hardened without coupling it to the database or transport layer.
- OpenAPI remains the client contract.
- Production readiness is verified by tests and deployment gates rather than by the presence of templates alone.
