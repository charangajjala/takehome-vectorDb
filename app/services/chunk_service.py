import logging
from app.models.schema import Chunk, Library
from app.repositories.interfaces import IReadOnlyRepository, IWriteRepository
from app.core.exceptions import EntityNotFound, ValidationError

logger = logging.getLogger(__name__)

class ChunkService:
    def __init__(
        self,
        repo_read: IReadOnlyRepository[Library],
        repo_write: IWriteRepository[Library]
    ):
        self._r = repo_read
        self._w = repo_write

    def add_chunk(self, lib_id: str, doc_id: str, chunk: Chunk) -> Chunk:
        logger.debug("Adding chunk %s to document %s in library %s", chunk.id, doc_id, lib_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        for d in lib.documents:
            if d.id == doc_id:
                if any(c.id == chunk.id for c in d.chunks):
                    raise ValidationError(f"Chunk '{chunk.id}' already exists")
                d.chunks.append(chunk)
                self._w.update(lib)
                logger.info("Chunk %s added to document %s", chunk.id, doc_id)
                return chunk
        raise EntityNotFound(f"Document '{doc_id}' not found")

    def get_chunk(self, lib_id: str, doc_id: str, chunk_id: str) -> Chunk:
        logger.debug("Fetching chunk %s from document %s in library %s", chunk_id, doc_id, lib_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        for d in lib.documents:
            if d.id == doc_id:
                for c in d.chunks:
                    if c.id == chunk_id:
                        return c
                break
        raise EntityNotFound(f"Chunk '{chunk_id}' not found")

    def update_chunk(self, lib_id: str, doc_id: str, chunk: Chunk) -> Chunk:
        logger.debug("Updating chunk %s in document %s", chunk.id, doc_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        for d in lib.documents:
            if d.id == doc_id:
                for i, existing in enumerate(d.chunks):
                    if existing.id == chunk.id:
                        d.chunks[i] = chunk
                        self._w.update(lib)
                        logger.info("Chunk %s updated", chunk.id)
                        return chunk
                raise EntityNotFound(f"Chunk '{chunk.id}' not found")
        raise EntityNotFound(f"Document '{doc_id}' not found")

    def delete_chunk(self, lib_id: str, doc_id: str, chunk_id: str) -> None:
        logger.debug("Deleting chunk %s from document %s", chunk_id, doc_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        for d in lib.documents:
            if d.id == doc_id:
                d.chunks = [c for c in d.chunks if c.id != chunk_id]
                self._w.update(lib)
                logger.info("Chunk %s deleted", chunk_id)
                return
        raise EntityNotFound(f"Document '{doc_id}' not found")
