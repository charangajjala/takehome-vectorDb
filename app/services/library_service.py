import logging
from typing import List
from app.models.schema import Library, Chunk
from app.repositories.interfaces import IReadOnlyRepository, IWriteRepository
from app.indexers.interfaces import IKnnIndexer
from app.core.exceptions import EntityNotFound, ValidationError

logger = logging.getLogger(__name__)

class LibraryService:
    def __init__(
        self,
        repo_read: IReadOnlyRepository[Library],
        repo_write: IWriteRepository[Library],
        indexer: IKnnIndexer
    ):
        self._r = repo_read
        self._w = repo_write
        self._idx = indexer

    def create_library(self, lib: Library) -> Library:
        logger.debug("Creating library %s", lib.id)
        if not lib.name.strip():
            raise ValidationError("Library name cannot be blank")
        self._w.create(lib)
        self._idx.build([])
        logger.info("Library %s created", lib.id)
        return lib

    def get_library(self, lib_id: str) -> Library:
        logger.debug("Fetching library %s", lib_id)
        lib = self._r.get(lib_id)
        if not lib:
            logger.error("Library %s not found", lib_id)
            raise EntityNotFound(f"Library '{lib_id}' not found")
        return lib

    def update_library(self, lib_id: str, lib: Library) -> Library:
        logger.debug("Updating library %s", lib_id)
        if lib.id != lib_id or not lib.name.strip():
            raise ValidationError("Invalid library data")
        _ = self.get_library(lib_id)
        self._w.update(lib)
        chunks = [c for d in lib.documents for c in d.chunks]
        self._idx.build(chunks)
        logger.info("Library %s updated", lib_id)
        return lib

    def delete_library(self, lib_id: str) -> None:
        logger.debug("Deleting library %s", lib_id)
        _ = self.get_library(lib_id)
        self._w.delete(lib_id)
        logger.info("Library %s deleted", lib_id)

    def search(self, lib_id: str, embedding: List[float], k: int) -> List[Chunk]:
        logger.debug("Searching library %s k=%d", lib_id, k)
        lib = self.get_library(lib_id)
        chunks = [c for d in lib.documents for c in d.chunks]
        self._idx.build(chunks)
        results = self._idx.query(embedding, k)
        logger.info("Search in %s returned %d results", lib_id, len(results))
        return [c for c, _ in results]
