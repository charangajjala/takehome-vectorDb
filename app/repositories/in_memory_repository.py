import functools
from threading import RLock
from typing import Dict, Generic, List, Optional, TypeVar
from app.repositories.interfaces import IReadOnlyRepository, IWriteRepository

T = TypeVar("T")

def synchronized(method):
    """Decorator to wrap a method in self._lock."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper

class InMemoryRepository(IReadOnlyRepository[T], IWriteRepository[T], Generic[T]):
    """Thread-safe in-memory CRUD store, using a decorator for locking."""
    def __init__(self) -> None:
        self._data: Dict[str, T] = {}
        self._lock = RLock()

    @synchronized
    def get(self, id: str) -> Optional[T]:
        return self._data.get(id)

    @synchronized
    def list(self) -> List[T]:
        return list(self._data.values())

    @synchronized
    def create(self, item: T) -> None:
        if item.id in self._data:
            raise ValueError(f"{item.id!r} already exists")
        self._data[item.id] = item

    @synchronized
    def update(self, item: T) -> None:
        if item.id not in self._data:
            raise KeyError(f"{item.id!r} not found")
        self._data[item.id] = item

    @synchronized
    def delete(self, id: str) -> None:
        if id not in self._data:
            raise KeyError(f"{id!r} not found")
        del self._data[id]
