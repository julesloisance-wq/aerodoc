"""PostgreSQL connection helpers."""

import psycopg
from pgvector.psycopg import register_vector

from aerodoc.config import get_settings


def connect(url: str | None = None) -> psycopg.Connection:
    """Open a connection with the pgvector extension enabled and registered."""
    conn = psycopg.connect(url or get_settings().database_url, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def server_info(conn: psycopg.Connection) -> dict[str, str]:
    """Return the PostgreSQL and pgvector versions, as a quick health check."""
    pg = conn.execute("SHOW server_version").fetchone()[0]
    vec = conn.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'").fetchone()[0]
    return {"postgres": pg, "pgvector": vec}


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id               text PRIMARY KEY,
    doc_type         text NOT NULL,          -- 'directive' or 'handbook'
    title            text NOT NULL,
    ad_number        text,                   -- e.g. '2026-18-03'
    families         text[] NOT NULL DEFAULT '{}',
    publication_date date,
    effective_date   date,
    source_url       text NOT NULL,
    download_url     text NOT NULL,
    local_path       text NOT NULL,
    sha256           text,
    abstract         text
);
"""


def init_schema(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA)


def upsert_documents(conn: psycopg.Connection, records: list) -> int:
    """Insert or update document metadata (one row per manifest entry)."""
    init_schema(conn)
    with conn.cursor() as cur:
        for r in records:
            cur.execute(
                """
                INSERT INTO documents (id, doc_type, title, ad_number, families,
                    publication_date, effective_date, source_url, download_url,
                    local_path, sha256, abstract)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    doc_type = EXCLUDED.doc_type, title = EXCLUDED.title,
                    ad_number = EXCLUDED.ad_number, families = EXCLUDED.families,
                    publication_date = EXCLUDED.publication_date,
                    effective_date = EXCLUDED.effective_date,
                    source_url = EXCLUDED.source_url, download_url = EXCLUDED.download_url,
                    local_path = EXCLUDED.local_path, sha256 = EXCLUDED.sha256,
                    abstract = EXCLUDED.abstract
                """,
                (
                    r.id,
                    r.doc_type,
                    r.title,
                    r.ad_number,
                    r.families,
                    r.publication_date,
                    r.effective_date,
                    r.source_url,
                    r.download_url,
                    r.local_path,
                    r.sha256,
                    r.abstract,
                ),
            )
    return len(records)
