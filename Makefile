db:
	docker compose up -d --wait db adminer
	uv run aerodoc health

db-down:
	docker compose down

test:
	uv run ruff check .
	uv run pytest

lint:
	uv run ruff check . --fix
	uv run ruff format .

data:
	uv run aerodoc data

.PHONY: db db-down data test lint
