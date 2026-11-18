"""HTTP API: `POST /ask`, `POST /search`, `GET /health`, `GET /stats`.

Run with: uvicorn aerodoc.api:app --port 8000
Models are loaded once at startup, so each question only pays for retrieval and the LLM.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from aerodoc import db
from aerodoc.answer import answer_question
from aerodoc.pipeline_config import load_config
from aerodoc.search import Hit, retrieve

CONFIG = load_config(Path(os.environ.get("AERODOC_CONFIG", "configs/default.yaml")))


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Warm-up: load the embedding model, the reranker and the BM25 index once.
    try:
        with db.connect() as conn:
            retrieve(conn, "landing gear inspection", CONFIG)
    except Exception as exc:  # the API still starts; /health reports the problem
        print(f"Warm-up skipped: {exc}")
    yield


app = FastAPI(
    title="AeroDoc API",
    description="Cited answers over FAA airworthiness directives and the AMT handbook.",
    version="0.1.0",
    lifespan=lifespan,
)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class Passage(BaseModel):
    number: int
    citation: str
    document_id: str
    doc_type: str
    ad_number: str | None
    section: str | None
    page: int | None
    page_label: str | None
    source_url: str
    text: str
    score: float
    found_by: dict[str, int]
    cited: bool = False


class AskResponse(BaseModel):
    question: str
    answer: str
    abstained: bool
    cited: list[int]
    passages: list[Passage]
    model: str
    timings_ms: dict[str, float]
    tokens: int


def _passage(n: int, hit: Hit, cited: set[int]) -> Passage:
    return Passage(
        number=n,
        citation=hit.citation,
        document_id=hit.document_id,
        doc_type=hit.doc_type,
        ad_number=hit.ad_number,
        section=hit.section,
        page=hit.page,
        page_label=hit.page_label,
        source_url=hit.source_url,
        text=hit.text,
        score=hit.score,
        found_by=hit.ranks,
        cited=n in cited,
    )


@app.get("/health")
def health() -> dict:
    try:
        with db.connect() as conn:
            chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"database not ready: {exc}") from exc
    return {"status": "ok", "chunks": chunks}


@app.get("/stats")
def stats() -> dict:
    with db.connect() as conn:
        docs = dict(conn.execute("SELECT doc_type, count(*) FROM documents GROUP BY 1").fetchall())
        families = dict(
            conn.execute(
                "SELECT f, count(*) FROM documents, unnest(families) f GROUP BY 1 ORDER BY 1"
            ).fetchall()
        )
        chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    return {"documents": docs, "families": families, "chunks": chunks}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        with db.connect() as conn:
            ans = answer_question(conn, request.question, CONFIG)
    except RuntimeError as exc:  # LLM unavailable (rate limit, outage)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    cited = set(ans.cited)
    return AskResponse(
        question=ans.question,
        answer=ans.text,
        abstained=ans.abstained,
        cited=ans.cited,
        passages=[_passage(i, h, cited) for i, h in enumerate(ans.passages, 1)],
        model=ans.model,
        timings_ms=ans.timings_ms,
        tokens=ans.prompt_tokens + ans.completion_tokens,
    )


@app.post("/search", response_model=list[Passage])
def search(request: AskRequest) -> list[Passage]:
    """Retrieval only (no LLM): the passages that /ask would give to the model."""
    with db.connect() as conn:
        result = retrieve(conn, request.question, CONFIG)
    return [_passage(i, h, set()) for i, h in enumerate(result.hits, 1)]
