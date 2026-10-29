import math


class TFIDF:
    def __init__(self):
        self.document_vectors = {}

    def calculate_tf(self, frequency: int) -> float:
        if frequency <= 0:
            return 0.0

        return 1.0 + math.log(frequency)

    def calculate_idf(
        self,
        total_documents: int,
        document_frequency: int,
    ) -> float:

        if total_documents <= 0 or document_frequency <= 0:
            return 0.0

        return math.log(
            total_documents / document_frequency
        ) + 1.0

    def build_document_vector(
        self,
        document_id: int,
        term_frequencies: dict[str, int],
        document_frequencies: dict[str, int],
        total_documents: int,
    ) -> dict[str, float]:

        vector = {}

        for term, frequency in term_frequencies.items():
            tf = self.calculate_tf(frequency)

            df = document_frequencies[term]

            idf = self.calculate_idf(
                total_documents,
                df,
            )

            vector[term] = tf * idf

        self.document_vectors[document_id] = vector

        return vector