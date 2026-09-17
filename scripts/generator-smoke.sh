#!/usr/bin/env bash
set -euo pipefail

repo_root="$(pwd)"
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

validate_project() {
  local project="$1"
  local ai_extra="$2"

  pushd "$project" >/dev/null
  uv sync --extra dev ${ai_extra}
  uv run ruff check .
  uv run mypy src
  uv run pytest

  # Exercise the generated migration environment against its default local SQLite DB.
  uv run alembic upgrade head
  uv run alembic downgrade base
  uv run alembic upgrade head
  popd >/dev/null
}

cd "$repo_root"
echo "Generating and validating default project"
uv run fastapi-backbone new generated-default --output "$workdir"
validate_project "$workdir/generated-default" ""

cd "$repo_root"
echo "Generating and validating AI-enabled project"
uv run fastapi-backbone new generated-ai --output "$workdir" --ai
validate_project "$workdir/generated-ai" "--extra ai"

echo "Generated-project smoke gate passed"
