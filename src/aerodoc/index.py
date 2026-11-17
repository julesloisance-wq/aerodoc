"""Build the search index: chunks + embeddings + full-text vectors in PostgreSQL."""

from __future__ import annotations

import json
import time
from pathlib import Path

import psycopg

from aerodoc import db
from aerodoc.chunking import Chunk, chunk_document
from aerodoc.corpus import load_manifest
from aerodoc.embeddings import embed_passages
from aerodoc.pipeline_config import PipelineConfig


def chunks_schema(dimension: int) -> str:
    return f"""
    DROP TABLE IF EXISTS chunks;
    CREATE TABLE chunks (
        id          bigserial PRIMARY KEY,
        document_id text NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        chunk_index int  NOT NULL,
        header      text NOT NULL,   -- document / AD number / section, embedded with the text
        text        text NOT NULL,
        page        int,             -- Federal Register page, or PDF page for the handbook
        page_label  text,            -- printed page number, e.g. '5-51' in the handbook
        section     text,
        embedding   vector({dimension}) NOT NULL,
        -- Full-text search vector (used by keyword search at step 4).
        tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', header || ' ' || text)) STORED
    );
    -- HNSW: approximate nearest-neighbour index, fast cosine search over thousands of vectors.
    CREATE INDEX chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
    CREATE INDEX chunks_tsv_idx ON chunks USING gin (tsv);
    CREATE TABLE IF NOT EXISTS index_meta (key text PRIMARY KEY, value jsonb NOT NULL);
    """


def build_index(conn: psycopg.Connection, cfg: PipelineConfig, data_dir: Path) -> int:
    records = load_manifest(data_dir)
    db.upsert_documents(conn, records)

    t0 = time.time()
    chunks: list[Chunk] = []
    for rec in records:
        chunks.extend(chunk_document(rec, data_dir, cfg.chunking))
    print(f"{len(chunks)} chunks from {len(records)} documents ({time.time() - t0:.0f}s)")

    t0 = time.time()
    vectors = embed_passages([c.embedding_text for c in chunks], cfg.embedding, True)
    print(f"Embedded {len(chunks)} chunks in {time.time() - t0:.0f}s")

    conn.execute(chunks_schema(cfg.embedding.dimension))
    with conn.cursor() as cur:
        cur.executemany(
            """INSERT INTO chunks (document_id, chunk_index, header, text, page,
                   page_label, section, embedding) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            [
                (c.document_id, c.chunk_index, c.header, c.text, c.page, c.page_label, c.section, v)
                for c, v in zip(chunks, vectors, strict=True)
            ],
        )
        cur.execute(
            "INSERT INTO index_meta VALUES ('config', %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            (json.dumps(cfg.model_dump()),),
        )
    return len(chunks)
