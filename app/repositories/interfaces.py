from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class IReadOnlyRepository(ABC, Generic[T]):
    @abstractmethod
    def get(self, id: str) -> Optional[T]: ...
    @abstractmethod
    def list(self) -> List[T]: ...

class IWriteRepository(ABC, Generic[T]):
    @abstractmethod
    def create(self, item: T) -> None: ...
    @abstractmethod
    def update(self, item: T) -> None: ...
    @abstractmethod
    def delete(self, id: str) -> None: ...
