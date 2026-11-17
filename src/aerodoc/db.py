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
