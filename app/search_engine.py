from collections import Counter

from app.text_processor import TextProcessor
from app.inv_idx import InvertedIndex
from app.tf_idf import TFIDF
from app.ranker import Ranker
from app.database import Database


class SearchEngine:
    def __init__(self, database: Database | None = None):
        self.database = database

        self.text_processor = TextProcessor()
        self.inverted_index = InvertedIndex()
        self.tf_idf = TFIDF()
        self.ranker = Ranker()
        self.documents = {}
        self.document_terms = {}

        if self.database is not None:
            self.load_documents()

    def load_documents(self) -> None:
        """Load all documents from the database into the in-memory index."""
        if self.database is None:
            return

        documents = self.database.get_all_documents()

        for document in documents:
            self.add_document(
                document_id=document["id"],
                title=document["title"],
                content=document["content"],
            )

    def add_document(self, document_id: int, title: str, content: str) -> None:
        if self.database is not None:
            self.database.add_document(document_id, title, content)
        if document_id in self.documents:
            self.inverted_index.remove_document(document_id)
            self.tf_idf.document_vectors.pop(document_id, None)

        tokens = self.text_processor.process(content)
        term_frequencies = Counter(tokens)

        self.documents[document_id] = {
            "title": title,
            "content": content,
        }

        self.document_terms[document_id] = dict(term_frequencies)

        self.inverted_index.add_document(document_id, tokens)

        self._rebuild_tfidf()

    def _rebuild_tfidf(self) -> None:
        document_frequencies = {
            term: self.inverted_index.get_document_frequency(term)
            for term in self.inverted_index.index
        }

        total_documents = len(self.documents)
        self.tf_idf.document_vectors.clear()

        for document_id, term_frequencies in self.document_terms.items():
            self.tf_idf.build_document_vector(
                document_id,
                term_frequencies,
                document_frequencies,
                total_documents,
            )

    def search(self, query: str, k: int = 10) -> list[tuple[int, float]]:
        query_terms = self.text_processor.process(query)

        if not query_terms:
            return []

        candidates = self.inverted_index.get_candidates(query_terms)

        if not candidates:
            return []

        query_term_frequencies = Counter(query_terms)

        document_frequencies = {
            term: self.inverted_index.get_document_frequency(term)
            for term in query_term_frequencies
        }

        query_vector = {}

        for term, frequency in query_term_frequencies.items():
            tf = self.tf_idf.calculate_tf(frequency)
            idf = self.tf_idf.calculate_idf(
                len(self.documents),
                document_frequencies[term],
            )
            query_vector[term] = tf * idf

        candidate_vectors = {
            document_id: self.tf_idf.document_vectors[document_id]
            for document_id in candidates
        }

        return self.ranker.top_k(query_vector, candidate_vectors, k)

    def delete_document(self, document_id: int) -> bool:
        if document_id not in self.documents:
            return False

        if self.database is not None:
            self.database.delete_document(document_id)

        self.inverted_index.remove_document(document_id)
        self.tf_idf.document_vectors.pop(document_id, None)

        self.documents.pop(document_id, None)
        self.document_terms.pop(document_id, None)

        self._rebuild_tfidf()

        return True
