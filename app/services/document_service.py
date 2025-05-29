import logging
from app.models.schema import Document, Library
from app.repositories.interfaces import IReadOnlyRepository, IWriteRepository
from app.core.exceptions import EntityNotFound, ValidationError

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(
        self,
        repo_read: IReadOnlyRepository[Library],
        repo_write: IWriteRepository[Library]
    ):
        self._r = repo_read
        self._w = repo_write

    def add_document(self, lib_id: str, doc: Document) -> Document:
        logger.debug("Adding document %s to library %s", doc.id, lib_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        if any(d.id == doc.id for d in lib.documents):
            raise ValidationError(f"Document '{doc.id}' already exists")
        lib.documents.append(doc)
        self._w.update(lib)
        logger.info("Document %s added to library %s", doc.id, lib_id)
        return doc

    def get_document(self, lib_id: str, doc_id: str) -> Document:
        logger.debug("Fetching document %s from library %s", doc_id, lib_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        for d in lib.documents:
            if d.id == doc_id:
                return d
        raise EntityNotFound(f"Document '{doc_id}' not found")

    def update_document(self, lib_id: str, doc: Document) -> Document:
        logger.debug("Updating document %s in library %s", doc.id, lib_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        for i, existing in enumerate(lib.documents):
            if existing.id == doc.id:
                lib.documents[i] = doc
                self._w.update(lib)
                logger.info("Document %s updated in library %s", doc.id, lib_id)
                return doc
        raise EntityNotFound(f"Document '{doc.id}' not found")

    def delete_document(self, lib_id: str, doc_id: str) -> None:
        logger.debug("Deleting document %s from library %s", doc_id, lib_id)
        lib = self._r.get(lib_id)
        if not lib:
            raise EntityNotFound(f"Library '{lib_id}' not found")
        lib.documents = [d for d in lib.documents if d.id != doc_id]
        self._w.update(lib)
        logger.info("Document %s deleted from library %s", doc_id, lib_id)
