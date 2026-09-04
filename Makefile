.PHONY: install test lint typecheck check run prod migrate docker-up docker-down docker-test

install:
	uv sync --extra dev

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

check: lint typecheck test

run:
	uv run uvicorn fastapi_backbone.app:create_app --factory --reload --host 127.0.0.1 --port 8000

prod:
	uv run uvicorn fastapi_backbone.app:create_app --factory --host 0.0.0.0 --port 8000

migrate:
	uv run alembic upgrade head

docker-up:
	docker compose -f docker/compose.yml up --build -d

docker-down:
	docker compose -f docker/compose.yml down

docker-test:
	bash scripts/docker-smoke.sh
