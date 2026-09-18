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

  # Isolate the external generator from its default post-generation Ruff hooks first.
  # This distinguishes OpenAPI parsing/model generation failures from hook failures.
  cat > "$workdir/client-config.yml" <<'EOF'
post_hooks:
  - "true"
EOF
  uv run --project "$repo_root" --with openapi-python-client openapi-python-client --version

  # Run the external process from a Python subprocess so stdout/stderr and the exact
  # exit status survive even when the generator terminates abruptly.
  uv run --project "$repo_root" --with openapi-python-client python - "$project/openapi.json" "$project/client-no-hooks" "$workdir/client-config.yml" <<'PY'
import subprocess
import sys

spec, output, config = sys.argv[1:]
command = [
    "openapi-python-client",
    "generate",
    "--meta",
    "uv",
    "--config",
    config,
    "--path",
    spec,
    "--output-path",
    output,
]
result = subprocess.run(command, capture_output=True, text=True)
print("external generator exit:", result.returncode)
print("external generator stdout:")
print(result.stdout, end="")
print("external generator stderr:")
print(result.stderr, end="")
raise SystemExit(0)
PY

  test -f "$project/client-no-hooks/pyproject.toml"
  client_package="$(find "$project/client-no-hooks" -mindepth 1 -maxdepth 1 -type d -name "*_client" -print -quit)"
  test -n "$client_package"
  test -f "$client_package/__init__.py"

  rm -rf "$project/client-no-hooks"
  if ! uv run --project "$repo_root" --with openapi-python-client fastapi-backbone client generate \
    --spec "$project/openapi.json" \
    --output "$project/client"
  then
    echo "Client generation failed with default post-hooks; inspecting generated output"
    find "$project/client" -maxdepth 3 -type f -print 2>/dev/null || true
    uv run --project "$repo_root" --with ruff ruff check "$project/client" || true
    exit 1
  fi
  test -f "$project/client/pyproject.toml"
  client_package="$(find "$project/client" -mindepth 1 -maxdepth 1 -type d -name "*_client" -print -quit)"
  test -n "$client_package"
  test -f "$client_package/__init__.py"
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
