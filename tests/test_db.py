
from app.database import Database


def test_initialize_creates_documents_table(tmp_path):
    db_path = tmp_path / "test.db"
    database = Database(str(db_path))

    database.initialize()

    assert db_path.exists()

def test_add_document(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    database.initialize()

    database.add_document(1, "MiniSearch", "Information retrieval")

    import sqlite3

    with sqlite3.connect(database.db_path) as connection:
        row = connection.execute(
            "SELECT id, title, content FROM documents WHERE id = ?",
            (1,),
        ).fetchone()

    assert row == (1, "MiniSearch", "Information retrieval")


def test_add_document_replaces_existing_id(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    database.initialize()

    database.add_document(1, "Old title", "Old content")
    database.add_document(1, "New title", "New content")

    import sqlite3

    with sqlite3.connect(database.db_path) as connection:
        rows = connection.execute(
            "SELECT id, title, content FROM documents"
        ).fetchall()

    assert rows == [(1, "New title", "New content")]

def test_get_document(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    database.initialize()
    database.add_document(1, "MiniSearch", "Search engine")

    document = database.get_document(1)

    assert document is not None
    assert document["id"] == 1
    assert document["title"] == "MiniSearch"
    assert document["content"] == "Search engine"
    assert "created_at" in document


def test_get_missing_document(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    database.initialize()

    assert database.get_document(999) is None


def test_get_all_documents(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    database.initialize()
    database.add_document(2, "Second", "Content B")
    database.add_document(1, "First", "Content A")

    documents = database.get_all_documents()

    assert [document["id"] for document in documents] == [1, 2]

def test_delete_existing_document(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    database.initialize()
    database.add_document(1, "MiniSearch", "Search engine")

    deleted = database.delete_document(1)

    assert deleted is True
    assert database.get_document(1) is None


def test_delete_missing_document(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    database.initialize()

    deleted = database.delete_document(999)

    assert deleted is False
