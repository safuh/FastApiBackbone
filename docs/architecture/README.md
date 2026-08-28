# Architecture

This directory records architectural boundaries and decisions that should remain stable across feature work.

## Reference layers

```text
Transport/API
     ↓
Application services
     ↓
Domain contracts / policies
     ↑
Infrastructure adapters
```

The dependency arrow is intentionally inward. Infrastructure implements contracts; business logic does not need to know whether persistence uses SQLAlchemy, whether the transport is FastAPI, or which client consumes OpenAPI.

## Decision records

Architectural Decision Records (ADRs) are added when a change has durable consequences for public APIs, dependency direction, persistence, security, deployment, or generated-project compatibility.
