from app.inv_idx import InvertedIndex


def test_add_document():
    index = InvertedIndex()

    index.add_document(1, ["machine", "learn", "machine"])

    assert index.get_postings("machine") == {1: 2}
    assert index.get_postings("learn") == {1: 1}


def test_remove_document():
    index = InvertedIndex()

    index.add_document(1, ["machine", "learn"])
    index.add_document(2, ["machine", "algorithm"])

    index.remove_document(1)

    assert index.get_postings("machine") == {2: 1}
    assert index.get_postings("learn") == {}


def test_get_candidates():
    index = InvertedIndex()

    index.add_document(1, ["machine", "learn"])
    index.add_document(2, ["machine", "algorithm"])
    index.add_document(3, ["database"])

    candidates = index.get_candidates(["machine", "learn"])

    assert candidates == {1: 2, 2: 1}