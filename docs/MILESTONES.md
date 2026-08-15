# FastAPI Backbone Completion Tracker

## Foundation

- [x] Project packaging with `pyproject.toml`
- [x] Pydantic settings
- [x] Async SQLAlchemy engine/session factory
- [x] PostgreSQL + SQLite driver support
- [x] Application lifespan
- [x] Structured logging
- [x] API composition root
- [x] Health endpoint
- [x] Alembic configuration
- [x] Async Alembic environment
- [x] Safe `.env.example`
- [x] Python `.gitignore`

## Next hardening milestones

- [ ] Shared exception hierarchy
- [ ] Request correlation IDs
- [ ] Centralized exception handlers
- [ ] Authentication/authorization optional module
- [ ] Generic repository/service contracts
- [ ] Database transaction boundary helpers
- [ ] Test database fixtures
- [ ] CI workflow
- [ ] Docker development environment
- [ ] PostgreSQL integration tests
- [ ] Observability hooks
- [ ] Production deployment examples
- [ ] Security baseline checklist
- [ ] Load-test example

## Design rule

FastApiBackbone should remain domain-neutral. Features that belong to a particular product—AI providers, conversations, billing, documents, tool execution, etc.—should live in the consuming application's bounded contexts rather than being added to the backbone.
