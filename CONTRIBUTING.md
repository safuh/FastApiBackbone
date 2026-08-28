# Contributing to FastAPI Backbone

Thank you for contributing. FastAPI Backbone is intended to become reusable infrastructure, so compatibility, documentation, and tests are as important as implementation.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
mypy src
```

## Pull requests

Every pull request should:

1. explain the problem and proposed design;
2. include tests for changed behavior;
3. update module documentation when boundaries or public behavior change;
4. update `docs/MILESTONES.md` when milestone status changes;
5. avoid unrelated refactors; and
6. leave CI green.

Security-sensitive changes require additional tests and documentation. Do not disclose vulnerabilities through normal public issues; follow `SECURITY.md`.

## Architecture changes

If a change affects dependency direction, public API, authentication, persistence semantics, deployment behavior, or another major architectural decision, add or update an ADR under `docs/architecture/adr/`.

## Commit discipline

Use concise conventional commit-style messages such as:

```text
feat: add refresh token rotation
fix: dispose engine on shutdown
refactor: isolate repository contract
```

Do not claim a milestone complete until its acceptance criteria have been verified.
