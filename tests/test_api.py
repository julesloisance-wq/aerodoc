from fastapi.testclient import TestClient

from aerodoc.api import app

client = TestClient(app)


def test_ask_rejects_empty_question():
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_openapi_lists_the_endpoints():
    paths = client.get("/openapi.json").json()["paths"]
    assert {"/ask", "/search", "/health", "/stats"} <= set(paths)
