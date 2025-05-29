# app/indexers/vptree.py

import random
import math
import heapq
from typing import List, Tuple, Optional

from app.indexers.interfaces import IKnnIndexer
from app.models.schema import Chunk

def euclidean(a: List[float], b: List[float]) -> float:
    """Compute Euclidean distance between two equal-length vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

class VPTreeNode:
    __slots__ = ("vp", "radius", "left", "right")

    def __init__(
        self,
        vp: Chunk,
        radius: float,
        left: Optional["VPTreeNode"],
        right: Optional["VPTreeNode"],
    ):
        self.vp = vp
        self.radius = radius
        self.left = left
        self.right = right

class VPTreeIndexer(IKnnIndexer):
    """Exact k-NN using a vantage-point tree on Euclidean distance."""

    def __init__(self) -> None:
        self._root: Optional[VPTreeNode] = None

    def build(self, chunks: List[Chunk]) -> None:
        """Recursively build a VP-tree from the list of chunks."""
        def _build_node(items: List[Chunk]) -> Optional[VPTreeNode]:
            if not items:
                return None
            # Choose a random vantage point
            vp = items.pop(random.randrange(len(items)))
            # Compute distances to all other items
            dists = [euclidean(vp.embedding, c.embedding) for c in items]
            # Median distance is our partition radius
            median = sorted(dists)[len(dists) // 2] if dists else 0.0
            # Partition into left (<= median) and right (> median)
            left_items  = [c for c, d in zip(items, dists) if d <= median]
            right_items = [c for c, d in zip(items, dists) if d >  median]
            # Recurse
            left_node  = _build_node(left_items)
            right_node = _build_node(right_items)
            return VPTreeNode(vp=vp, radius=median, left=left_node, right=right_node)

        # Use a copy so we don’t mutate the original list
        self._root = _build_node(chunks.copy())

    def query(
        self, embedding: List[float], k: int = 10
    ) -> List[Tuple[Chunk, float]]:
        """Return up to k nearest neighbors as (Chunk, distance)."""
        if self._root is None or k <= 0:
            return []

        # max-heap of (–distance, chunk_id, Chunk), so ties break on ID
        heap: List[Tuple[float, str, Chunk]] = []

        def _search(node: Optional[VPTreeNode]):
            if node is None:
                return
            # distance to vantage point
            d = euclidean(embedding, node.vp.embedding)
            key = node.vp.id
            if len(heap) < k:
                heapq.heappush(heap, (-d, key, node.vp))
            elif d < -heap[0][0]:
                heapq.heapreplace(heap, (-d, key, node.vp))

            # Decide which side to search first
            if d < node.radius:
                # inside the ball
                _search(node.left)
                # maybe the other side intersects
                if len(heap) < k or d + node.radius >= -heap[0][0]:
                    _search(node.right)
            else:
                # outside the ball
                _search(node.right)
                if len(heap) < k or d - node.radius <= -heap[0][0]:
                    _search(node.left)

        # Kick off the search
        _search(self._root)

        # Convert heap into a sorted list of (Chunk, distance)
        results = [ (chunk, -dist) for dist, _, chunk in heap ]
        results.sort(key=lambda x: x[1])  # ascending distance
        return results
