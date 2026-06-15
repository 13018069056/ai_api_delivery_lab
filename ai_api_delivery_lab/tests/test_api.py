import os

from fastapi.testclient import TestClient

from app import app


os.environ["COURSE_API_TOKEN"] = "test-token"
client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_without_token_returns_401():
    response = client.post("/api/ask", json={"question": "RAG 是什么？"})

    assert response.status_code == 401


def test_ask_with_token_returns_answer():
    response = client.post(
        "/api/ask",
        json={"question": "RAG 是什么？"},
        headers={"Authorization": "Bearer test-token"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["ok"] is True
    assert body["sources"] == ["course_notes:rag"]
    assert body["request_id"]


def test_empty_question_returns_422():
    response = client.post(
        "/api/ask",
        json={"question": ""},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 422