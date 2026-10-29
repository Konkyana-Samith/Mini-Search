import heapq
import math


class Ranker:
    def cosine_similarity(
        self,
        query_vector: dict[str, float],
        document_vector: dict[str, float],
    ) -> float:
        dot_product = sum(
            query_weight * document_vector.get(term, 0.0)
            for term, query_weight in query_vector.items()
        )

        query_magnitude = math.sqrt(
            sum(weight ** 2 for weight in query_vector.values())
        )
        document_magnitude = math.sqrt(
            sum(weight ** 2 for weight in document_vector.values())
        )

        if query_magnitude == 0 or document_magnitude == 0:
            return 0.0

        return dot_product / (query_magnitude * document_magnitude)

    def top_k(
        self,
        query_vector: dict[str, float],
        document_vectors: dict[int, dict[str, float]],
        k: int = 10,
    ) -> list[tuple[int, float]]:
        heap = []

        for document_id, document_vector in document_vectors.items():
            score = self.cosine_similarity(query_vector, document_vector)

            if len(heap) < k:
                heapq.heappush(heap, (score, document_id))
            elif score > heap[0][0]:
                heapq.heapreplace(heap, (score, document_id))

        return sorted(heap, reverse=True)