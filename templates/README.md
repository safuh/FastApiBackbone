# Project Templates

Templates are the source material for the future project generator.

Templates must remain deterministic and independently smoke-testable. A generated project is treated as a release artifact and must pass the same quality gates as the foundation.

Planned template families:

- `backend/` — FastAPI + SQLAlchemy + Alembic + identity.
- `flutter/` — optional Flutter client generated from OpenAPI.
- `kubernetes/` — deployment assets with safe secret placeholders.

Template versions will be coupled to generator releases so that generated applications can be traced back to the exact foundation version that created them.
