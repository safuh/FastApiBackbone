#!/usr/bin/env bash
set -euo pipefail

repo_root="$(pwd)"
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

validate_project() {
  local project="$1"
  local ai_extra="$2"
  local package="$3"

  pushd "$project" >/dev/null
  uv sync --extra dev ${ai_extra}
  uv run ruff check .
  uv run mypy src
  uv run pytest

  # Exercise the generated migration environment against its default local SQLite DB.
  uv run alembic upgrade head
  uv run alembic downgrade base
  uv run alembic upgrade head

  # Produce a real OpenAPI document from the generated application, then exercise the
  # public client-generation command against the actual openapi-python-client tool.
  uv run python -c "import json; from ${package}.app import create_app; json.dump(create_app().openapi(), open('openapi.json', 'w'), indent=2)" 
  uv run --project "$repo_root" --with openapi-python-client fastapi-backbone client generate \
    --spec "$project/openapi.json" \
    --output "$project/client"
  test -f "$project/client/pyproject.toml"
  test -d "$project/client/$package"
  popd >/dev/null
}

cd "$repo_root"
echo "Generating and validating default project"
uv run fastapi-backbone new generated-default --output "$workdir"
validate_project "$workdir/generated-default" "" "generated_default"

cd "$repo_root"
echo "Generating and validating AI-enabled project"
uv run fastapi-backbone new generated-ai --output "$workdir" --ai
validate_project "$workdir/generated-ai" "--extra ai" "generated_ai"

echo "Generated-project smoke gate passed"
