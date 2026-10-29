from collections import defaultdict


class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(dict)

    def add_document(
        self,
        document_id: int,
        tokens: list[str],
    ) -> None:

        term_frequency = defaultdict(int)

        for token in tokens:
            term_frequency[token] += 1

        for term, frequency in term_frequency.items():
            self.index[term][document_id] = frequency

    def remove_document(self, document_id: int) -> None:
        empty_terms = []

        for term, postings in self.index.items():
            if document_id in postings:
                del postings[document_id]

            if not postings:
                empty_terms.append(term)

        for term in empty_terms:
            del self.index[term]

    def get_postings(self, term: str) -> dict[int, int]:
        return self.index.get(term, {})

    def get_document_frequency(self, term: str) -> int:
        return len(self.get_postings(term))

    def get_candidates(
        self,
        query_terms: list[str],
    ) -> dict[int, int]:

        candidates = defaultdict(int)

        for term in set(query_terms):
            for document_id in self.get_postings(term):
                candidates[document_id] += 1

        return dict(candidates)