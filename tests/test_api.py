
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path / "test.db")

    with TestClient(app) as test_client:
        yield test_client


# ── Existing tests (preserved) ────────────────────────────────────────────────

def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_document(client):
    payload = {
        "id": 1,
        "title": "Python Basics",
        "content": "Python programming is useful",
    }

    create_response = client.post("/documents", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["id"] == 1

    get_response = client.get("/documents/1")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Python Basics"


def test_search_document(client):
    client.post(
        "/documents",
        json={
            "id": 1,
            "title": "Python Basics",
            "content": "Python programming is useful",
        },
    )

    response = client.get("/search", params={"q": "Python"})

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["id"] == 1


def test_delete_document(client):
    client.post(
        "/documents",
        json={
            "id": 1,
            "title": "Python Basics",
            "content": "Python programming is useful",
        },
    )

    response = client.delete("/documents/1")
    assert response.status_code == 200

    assert client.get("/documents/1").status_code == 404
    assert client.get("/search", params={"q": "Python"}).json()["count"] == 0


def test_missing_document_returns_404(client):
    response = client.get("/documents/999")

    assert response.status_code == 404


def test_invalid_document_returns_422(client):
    response = client.post(
        "/documents",
        json={"id": 1, "title": "", "content": "Some content"},
    )

    assert response.status_code == 422


def test_search_requires_query(client):
    response = client.get("/search")

    assert response.status_code == 422


# ── New tests ─────────────────────────────────────────────────────────────────

def test_list_documents_empty(client):
    """GET /documents returns an empty list when no documents exist."""
    response = client.get("/documents")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["documents"] == []


def test_list_documents_returns_all(client):
    """GET /documents returns every added document."""
    client.post("/documents", json={"id": 1, "title": "Alpha", "content": "First document content"})
    client.post("/documents", json={"id": 2, "title": "Beta", "content": "Second document content"})

    response = client.get("/documents")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    ids = [doc["id"] for doc in data["documents"]]
    assert sorted(ids) == [1, 2]


def test_list_documents_contains_expected_fields(client):
    """Each document entry must include id, title, content, and created_at."""
    client.post("/documents", json={"id": 5, "title": "My Doc", "content": "Hello world"})

    response = client.get("/documents")
    doc = response.json()["documents"][0]

    assert doc["id"] == 5
    assert doc["title"] == "My Doc"
    assert doc["content"] == "Hello world"
    assert "created_at" in doc


def test_search_result_includes_snippet(client):
    """Search results must include a 'snippet' field (no score visible to callers who ignore it)."""
    client.post(
        "/documents",
        json={"id": 1, "title": "Snippet Test", "content": "A " * 300},
    )

    response = client.get("/search", params={"q": "snippet"})
    # 'snippet' field is present regardless of match
    # Use a doc that is guaranteed to match
    client.post(
        "/documents",
        json={"id": 2, "title": "Snippet Doc", "content": "snippet content here"},
    )
    response2 = client.get("/search", params={"q": "snippet"})
    results = response2.json()["results"]
    assert len(results) > 0
    for result in results:
        assert "snippet" in result
        assert "score" in result   # score is present in API but not shown in UI


def test_snippet_is_truncated_for_long_content(client):
    """Snippets must not exceed 200 characters for long content."""
    long_content = "word " * 200
    client.post("/documents", json={"id": 10, "title": "Long Doc", "content": long_content})

    response = client.get("/search", params={"q": "word"})
    snippet = response.json()["results"][0]["snippet"]

    assert len(snippet) <= 202  # 200 chars + possible ellipsis char


def test_deleted_document_absent_from_list(client):
    """After deletion, document must not appear in GET /documents."""
    client.post("/documents", json={"id": 3, "title": "Temp", "content": "Temporary content"})
    client.delete("/documents/3")

    response = client.get("/documents")
    ids = [doc["id"] for doc in response.json()["documents"]]
    assert 3 not in ids


def test_deleted_document_absent_from_search(client):
    """After deletion, document must not appear in search results."""
    client.post(
        "/documents",
        json={"id": 7, "title": "Gone", "content": "unique xyzzy content for testing"},
    )
    client.delete("/documents/7")

    response = client.get("/search", params={"q": "xyzzy"})
    assert response.json()["count"] == 0


def test_delete_nonexistent_document_returns_404(client):
    """Deleting a document that doesn't exist must return 404."""
    response = client.delete("/documents/9999")
    assert response.status_code == 404


def test_update_document_via_post(client):
    """Posting a document with an existing ID replaces it."""
    client.post("/documents", json={"id": 1, "title": "Old Title", "content": "Old content"})
    client.post("/documents", json={"id": 1, "title": "New Title", "content": "New content"})

    doc = client.get("/documents/1").json()
    assert doc["title"] == "New Title"
    assert doc["content"] == "New content"

    # Old terms must no longer match
    assert client.get("/search", params={"q": "Old"}).json()["count"] == 0
