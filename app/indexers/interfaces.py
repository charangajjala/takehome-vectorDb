from abc import ABC, abstractmethod
from typing import List, Tuple
from app.models.schema import Chunk

class IKnnIndexer(ABC):
    @abstractmethod
    def build(self, chunks: List[Chunk]) -> None: ...
    @abstractmethod
    def query(self, embedding: List[float], k: int) -> List[Tuple[Chunk, float]]: ...
