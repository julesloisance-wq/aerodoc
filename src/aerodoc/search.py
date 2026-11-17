"""Retrieve the chunks most relevant to a question."""

from __future__ import annotations

from dataclasses import dataclass

import psycopg

from aerodoc.embeddings import embed_query
from aerodoc.pipeline_config import PipelineConfig


@dataclass
class Hit:
    chunk_id: int
    document_id: str
    title: str
    doc_type: str
    ad_number: str | None
    source_url: str
    header: str
    text: str
    page: int | None
    page_label: str | None
    section: str | None
    score: float

    @property
    def citation(self) -> str:
        """Human-readable reference, e.g. 'AD 2026-18-03, (c) Applicability, FR page 56578'."""
        if self.doc_type == "directive":
            name = f"AD {self.ad_number}" if self.ad_number else self.document_id
            page = f"FR page {self.page}" if self.page else None
        else:
            name = self.document_id
            page = f"page {self.page_label}" if self.page_label else None
        return ", ".join(p for p in (name, self.section, page) if p)


SELECT_HIT = """
    SELECT c.id, c.document_id, d.title, d.doc_type, d.ad_number, d.source_url,
           c.header, c.text, c.page, c.page_label, c.section, {score} AS score
    FROM chunks c JOIN documents d ON d.id = c.document_id
"""


def dense_search(
    conn: psycopg.Connection, query: str, cfg: PipelineConfig, k: int | None = None
) -> list[Hit]:
    """Semantic search: nearest chunks by cosine similarity of embeddings."""
    vector = embed_query(query, cfg.embedding)
    rows = conn.execute(
        SELECT_HIT.format(score="1 - (c.embedding <=> %(v)s)")
        + " ORDER BY c.embedding <=> %(v)s LIMIT %(k)s",
        {"v": vector, "k": k or cfg.retrieval.top_k},
    ).fetchall()
    return [Hit(*row) for row in rows]
