import math

from app.ranker import Ranker


def test_cosine_similarity():
    ranker = Ranker()

    identical = ranker.cosine_similarity(
        {"a": 1.0, "b": 2.0},
        {"a": 1.0, "b": 2.0},
    )

    orthogonal = ranker.cosine_similarity(
        {"a": 1.0},
        {"b": 1.0},
    )

    assert math.isclose(identical, 1.0)
    assert orthogonal == 0.0

def test_top_k():
    ranker = Ranker()

    query_vector = {"a": 1.0, "b": 1.0}

    document_vectors = {
        1: {"a": 1.0, "b": 1.0},
        2: {"a": 1.0},
        3: {"b": 1.0},
        4: {"c": 1.0},
    }

    results = ranker.top_k(query_vector, document_vectors, k=2)

    assert len(results) == 2
    assert results[0][1] == 1
    assert results[0][0] > results[1][0]