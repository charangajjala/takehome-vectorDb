from fastapi import HTTPException, Response, status
from app.core.exceptions import EntityNotFound, ValidationError
from app.services.document_service import DocumentService
from app.models.schema import Document

class DocumentController:
    def __init__(self, svc: DocumentService):
        self._svc = svc

    def create(self, lib_id: str, doc: Document) -> Document:
        try:
            return self._svc.add_document(lib_id, doc)
        except EntityNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def read(self, lib_id: str, doc_id: str) -> Document:
        try:
            return self._svc.get_document(lib_id, doc_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    def update(self, lib_id: str, doc_id: str, doc: Document) -> Document:
        if doc.id != doc_id:
            raise HTTPException(status_code=400, detail="ID mismatch")
        try:
            return self._svc.update_document(lib_id, doc)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete(self, lib_id: str, doc_id: str) -> Response:
        try:
            self._svc.delete_document(lib_id, doc_id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
