#!/usr/bin/env bash
set -euo pipefail

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

validate_project() {
  local project="$1"
  local ai_extra="$2"

  cd "$project"
  uv sync --extra dev ${ai_extra}
  uv run ruff check .
  uv run mypy src
  uv run pytest

  # Exercise the generated migration environment against its default local SQLite DB.
  uv run alembic upgrade head
  uv run alembic downgrade base
  uv run alembic upgrade head
}

echo "Generating and validating default project"
uv run fastapi-backbone new generated-default --output "$workdir"
validate_project "$workdir/generated-default" ""

echo "Generating and validating AI-enabled project"
uv run fastapi-backbone new generated-ai --output "$workdir" --ai
validate_project "$workdir/generated-ai" "--extra ai"

echo "Generated-project smoke gate passed"
