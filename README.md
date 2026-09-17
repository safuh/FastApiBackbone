# FastAPI Backbone

> **A production-grade foundation and project generator for FastAPI services, with an optional provider-agnostic AI application architecture.**
>
> FastAPI + SQLAlchemy 2.x + Alembic + JWT authentication + PostgreSQL + Docker + optional Pydantic AI.

[![CI](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml/badge.svg)](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml)

FastAPI Backbone is an open-source, domain-neutral foundation for teams that want to start serious Python APIs without rebuilding the same infrastructure every time. The generator is deliberately layered: the normal application remains free of AI dependencies, while an explicit `--ai` profile adds an AI boundary based on Pydantic AI.

## Current implementation

The repository currently contains a verified production foundation plus the first generator slice:

- explicit application factory and environment profiles;
- async SQLAlchemy 2.x and transaction-scoped Unit of Work;
- Alembic migration discipline;
- health/readiness, structured logging, correlation IDs and security controls;
- `fastapi-backbone new` CLI foundation;
- deterministic project generation with safe non-empty-directory protection;
- optional `--ai` generation profile;
- optional Pydantic AI dependency rather than a core dependency; and
- generator and AI-infrastructure tests.

The authoritative acceptance tracker is [`docs/MILESTONES.md`](docs/MILESTONES.md).

## Generator

The intended developer experience is:

```bash
uv tool install fastapi-backbone
fastapi-backbone new myapp
fastapi-backbone new myapp --ai
```

The generator is being developed as a versioned template system rather than a copy of the Backbone repository. This keeps generated applications independent from the generator source tree and lets future releases define explicit template compatibility contracts.

### AI profile

`--ai` is opt-in. A generated AI application gets an `ai/` boundary containing configuration and an agent factory. The model identifier is supplied by the application at runtime; business logic does not hard-code a provider SDK.

The current architecture separates three concerns:

```text
Application service
      ↓
Backbone AI contracts
(AIRequest / AIResponse / AIProvider)
      ↓
Provider registry + model router
      ↓
Optional Pydantic AI adapter
      ↓
OpenAI / Gemini / Ollama / other Pydantic AI provider
```

The core package does not import Pydantic AI. The optional adapter imports it only when the AI extra is installed. See the [Pydantic AI model provider documentation](https://ai.pydantic.dev/models/) and [Ollama provider documentation](https://ai.pydantic.dev/models/ollama/) for the supported provider model interfaces.

The important boundary is that **the LLM is not the authorization layer**. Tool permissions, domain policies, persistence, audit logging and consequential-action approval belong in deterministic application code.

Planned AI capabilities include structured outputs, tool execution, dependency injection, streaming, retries/timeouts, provider/model routing, fallback policies, token/cost telemetry, prompt versioning, evaluations, guardrails, RAG and human-in-the-loop workflows.

## Canonical local workflow

Use **uv** for development. This avoids mixing virtual-environment managers and dependency resolvers.

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src
make check
```

The reference application is run with the same factory in every environment:

```bash
make run
make prod
```

The factory is `fastapi_backbone.app:create_app`; the `--factory` flag is intentional.

## Configuration profiles

Configuration is environment-driven through `pydantic-settings`. Supported profiles are `development`, `test`, and `production`.

The optional AI settings are part of the canonical settings object:

```text
AI_ENABLED=false
AI_PROVIDER=ollama
AI_MODEL=ollama:qwen3
AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=2
```

When AI is enabled, `AI_MODEL` must use the `provider:model` format. Provider credentials, base URLs and SDK-specific options remain adapter/provider concerns rather than application-domain concerns.

Production configuration rejects debug mode and non-PostgreSQL database URLs. Never commit production secrets.

## Database and migrations

PostgreSQL is the production database. SQLite is supported for lightweight local development and unit tests.

The application owns one shared async engine and session factory. Application services can use `UnitOfWork` when they need an explicit transaction boundary; repositories should use the UoW session and must not create independent transactions.

Schema changes are made only through Alembic revisions. Application processes do not run migrations on startup.

## Health contract

```text
GET /api/health       -> process health
GET /api/health/live  -> liveness; no database dependency
GET /api/health/ready -> readiness; startup complete + database reachable
```

## Docker smoke test

```bash
make docker-test
```

The smoke test builds the image, starts PostgreSQL and the API, verifies liveness/readiness, and exercises the migration path.

## Project vision

FastAPI Backbone remains domain-neutral. Its long-term workflow is:

```bash
fastapi-backbone new myapp --frontend flutter --deployment kubernetes
fastapi-backbone new my-ai-app --ai
```

Flutter, Kubernetes assets, richer generator options and the complete AI runtime remain milestone work rather than being presented as finished features.

## Architecture

```text
Client(s)
  ↓
FastAPI HTTP boundary
  ↓
Application services
  ├── Domain contracts / policies
  ├── AI application layer (optional)
  │     ├── Agents
  │     ├── Structured outputs
  │     ├── Tools
  │     ├── Guardrails
  │     └── Evaluations
  └── Repository interfaces
          ↓
   Infrastructure adapters
          ↓
      PostgreSQL

Optional AI path:
Application → AI service → Pydantic AI → provider/model
```

See [`docs/architecture/`](docs/architecture/) and its ADRs for durable boundary decisions.

## Current status

**Version: 0.1.0-alpha**

M1 Core Foundation is complete and verified. Phase 4 Generator/CLI is in progress with the CLI, optional AI generation foundation, canonical AI configuration, provider registry, model routing boundary and optional Pydantic AI runtime adapter implemented on `feat/project-generator-ai-foundation`.

## Production-grade definition

For this project, **production-grade does not mean “it starts successfully.”** A milestone can only be called production-ready when it has documented public behavior, automated tests, deterministic dependency/build configuration, static analysis, safe defaults, operational health behavior, migration considerations, container validation where applicable, upgrade/release documentation, and a reproducible CI gate.

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Architecture changes should include an ADR or documentation update when they materially affect public behavior or generated-project compatibility.

## Security

Please do not disclose security vulnerabilities in public issues. Follow [`SECURITY.md`](SECURITY.md).

## License

FastAPI Backbone is released under the MIT License. See [`LICENSE`](LICENSE).
