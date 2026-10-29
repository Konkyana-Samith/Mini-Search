from app.search_engine import SearchEngine
from app.database import Database

def test_add_and_search():
    engine = SearchEngine()

    engine.add_document(1, "ML Basics", "Machine learning is useful")
    engine.add_document(2, "Algorithms", "Machine learning algorithms are powerful")
    engine.add_document(3, "Cooking", "Cooking requires fresh ingredients")

    results = engine.search("machine learning", k=2)

    assert len(results) == 2
    assert {document_id for _, document_id in results} == {1, 2}


def test_unknown_query_term():
    engine = SearchEngine()

    engine.add_document(1, "ML Basics", "Machine learning is useful")
    engine.add_document(2, "Algorithms", "Machine learning algorithms are powerful")

    results = engine.search("machine xyzabc", k=2)

    assert len(results) == 2
    assert {document_id for _, document_id in results} == {1, 2}


def test_empty_query():
    engine = SearchEngine()

    engine.add_document(1, "ML Basics", "Machine learning is useful")

    assert engine.search("") == []
    assert engine.search("the is a") == []

def test_load_documents_from_database(tmp_path):
    db_path = tmp_path / "test.db"
    database = Database(db_path)
    database.initialize()

    database.add_document(
        1,
        "ML Basics",
        "Machine learning is useful",
    )
    database.add_document(
        2,
        "Cooking",
        "Cooking requires fresh ingredients",
    )

    engine = SearchEngine(database)

    results = engine.search("machine learning")

    assert len(results) == 1
    assert results[0][1] == 1
def test_added_document_persists_after_reinitialization(tmp_path):
    db_path = tmp_path / "test.db"
    database = Database(db_path)
    database.initialize()

    engine1 = SearchEngine(database)
    engine1.add_document(
        1,
        "Python Basics",
        "Python is useful for software engineering",
    )

    engine2 = SearchEngine(database)

    results = engine2.search("python software")

    assert len(results) == 1
    assert results[0][1] == 1

    stored_document = database.get_document(1)
    assert stored_document is not None
    assert stored_document["title"] == "Python Basics"
def test_update_existing_document():
    engine = SearchEngine()

    engine.add_document(
        1,
        "Python Basics",
        "Python programming is useful",
    )

    engine.add_document(
        1,
        "Java Basics",
        "Java programming is powerful",
    )

    python_results = engine.search("Python")
    java_results = engine.search("Java")

    assert python_results == []
    assert len(java_results) == 1
    assert java_results[0][1] == 1
    assert engine.documents[1]["title"] == "Java Basics"

def test_update_document_with_database(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    engine = SearchEngine(database)

    engine.add_document(
        1,
        "Python Basics",
        "Python programming is useful",
    )

    engine.add_document(
        1,
        "Java Basics",
        "Java programming is powerful",
    )
    assert engine.search("Python") == []
    
    results = engine.search("Java")
    assert len(results) == 1
    assert results[0][1] == 1

    stored = database.get_document(1)
    assert stored["title"] == "Java Basics"
    assert stored["content"] == "Java programming is powerful"

def test_delete_document_with_database(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    engine = SearchEngine(database)

    engine.add_document(
        1,
        "Python Basics",
        "Python programming is useful",
    )

    deleted = engine.delete_document(1)

    assert deleted is True
    assert engine.search("Python") == []
    assert database.get_document(1) is None
    assert 1 not in engine.documents
    assert 1 not in engine.document_terms
    assert 1 not in engine.tf_idf.document_vectors

def test_delete_nonexistent_document():
    engine = SearchEngine()

    deleted = engine.delete_document(999)

    assert deleted is False
    assert engine.search("Python") == []