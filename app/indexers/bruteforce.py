import math
import heapq
from typing import List, Tuple
from app.indexers.interfaces import IKnnIndexer
from app.models.schema import Chunk

class BruteForceIndexer(IKnnIndexer):
    """Exact KNN via brute-force cosine similarity using a heap for top-k selection."""
    def __init__(self) -> None:
        self._chunks: List[Chunk] = []

    def build(self, chunks: List[Chunk]) -> None:
        self._chunks = chunks.copy() if chunks else []

    def query(self, embedding: List[float], k: int = 10) -> List[Tuple[Chunk, float]]:
        if not self._chunks or k <= 0:
            return []

        # Compute all cosine similarities
        sims = [(c, self._cosine(embedding, c.embedding)) for c in self._chunks]
        
        # Use heap to get top-k in O(N log k) time
        return heapq.nlargest(k, sims, key=lambda x: x[1])

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        mag = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
        return dot / mag if mag else 0.0
