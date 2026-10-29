import math

from app.tf_idf import TFIDF


def test_calculate_tf():
    tf_idf = TFIDF()

    assert tf_idf.calculate_tf(0) == 0.0
    assert tf_idf.calculate_tf(1) == 1.0
    assert math.isclose(tf_idf.calculate_tf(4), 1.0 + math.log(4))


def test_calculate_idf():
    tf_idf = TFIDF()

    assert tf_idf.calculate_idf(10, 0) == 0.0
    assert math.isclose(
        tf_idf.calculate_idf(10, 2),
        math.log(10 / 2) + 1.0,
    )


def test_build_document_vector():
    tf_idf = TFIDF()

    vector = tf_idf.build_document_vector(
        document_id=1,
        term_frequencies={"machine": 2, "learn": 1},
        document_frequencies={"machine": 2, "learn": 3},
        total_documents=5,
    )

    expected_machine = (1.0 + math.log(2)) * (math.log(5 / 2) + 1.0)
    expected_learn = 1.0 * (math.log(5 / 3) + 1.0)

    assert math.isclose(vector["machine"], expected_machine)
    assert math.isclose(vector["learn"], expected_learn)
    assert tf_idf.document_vectors[1] == vector