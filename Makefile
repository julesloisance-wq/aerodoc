db:
	docker compose up -d --wait db
	uv run aerodoc health

db-down:
	docker compose down

test:
	uv run ruff check .
	uv run pytest

lint:
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: db db-down test lint
