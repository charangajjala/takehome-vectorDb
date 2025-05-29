# tests/unit_tests/test_indexers.py

import math
import pytest
import numpy as np

from app.models.schema import Chunk
from app.indexers.bruteforce import BruteForceIndexer
from app.indexers.vptree import VPTreeIndexer


@pytest.fixture
def chunks():
    return [
        Chunk(id="c1", text="a", embedding=[1.0, 0.0], tags=[]),
        Chunk(id="c2", text="b", embedding=[0.0, 1.0], tags=[]),
        Chunk(id="c3", text="ab", embedding=[1.0, 1.0], tags=[]),
        Chunk(id="c4", text="d", embedding=[2.0, 2.0], tags=[]),
    ]

# ——— BruteForce tests —————————————————————————————————————————————
def test_bruteforce_empty():
    idx = BruteForceIndexer()
    idx.build([])
    assert idx.query([0, 0], k=5) == []

def test_bruteforce_simple(chunks):
    idx = BruteForceIndexer()
    idx.build(chunks)
    results = idx.query([1.0, 0.0], k=2)
    ids = [c.id for c, _ in results]
    assert ids == ["c1", "c3"]

def test_bruteforce_order(chunks):
    idx = BruteForceIndexer()
    idx.build(chunks)
    results = idx.query([0.0, 0.0], k=3)
    dists = [dist for _, dist in results]
    # distances should be non-decreasing
    assert dists == sorted(dists)

# ——— VPTree tests —————————————————————————————————————————————
def test_vptree_empty():
    idx = VPTreeIndexer()
    idx.build([])
    assert idx.query([0, 0], k=3) == []

def test_vptree_simple(chunks):
    idx = VPTreeIndexer()
    idx.build(chunks)
    results = idx.query([1.0, 1.0], k=1)
    assert results[0][0].id == "c3"

def test_vptree_k_greater_than_size(chunks):
    idx = VPTreeIndexer()
    idx.build(chunks)
    results = idx.query([1.0, 1.0], k=10)
    assert len(results) == len(chunks)
    ids = {c.id for c, _ in results}
    assert ids == {"c1", "c2", "c3", "c4"}


