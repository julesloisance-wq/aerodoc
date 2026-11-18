db:
	./scripts/ensure-docker.sh
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

data:
	uv run aerodoc data

index:
	uv run aerodoc index

eval:
	uv run aerodoc eval --config $(or $(CONFIG),configs/default.yaml) --questions $(or $(QUESTIONS),eval/questions/dev.jsonl)

up:
	./scripts/ensure-docker.sh
	docker compose up --build

api:
	uv run uvicorn aerodoc.api:app --port 8000

ui:
	uv run streamlit run src/aerodoc/ui.py --server.port 8501

.PHONY: db db-down data index eval test lint up api ui
