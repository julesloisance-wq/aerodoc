import psycopg
import pytest

from aerodoc import db


@pytest.fixture
def conn():
    try:
        connection = db.connect()
    except psycopg.OperationalError:
        pytest.skip("database not running (start it with `make db`)")
    yield connection
    connection.close()


@pytest.mark.integration
def test_pgvector_is_installed(conn):
    info = db.server_info(conn)
    assert info["pgvector"]


@pytest.mark.integration
def test_vector_similarity_search(conn):
    """The core operation of the project: find the nearest vector."""
    conn.execute("CREATE TEMP TABLE t (name text, embedding vector(3))")
    conn.execute("INSERT INTO t VALUES ('landing gear', '[1,0,0]'), ('fuel pump', '[0,1,0]')")
    nearest = conn.execute(
        "SELECT name FROM t ORDER BY embedding <=> '[0.9,0.1,0]' LIMIT 1"
    ).fetchone()[0]
    assert nearest == "landing gear"
