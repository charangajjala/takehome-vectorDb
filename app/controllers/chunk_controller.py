from fastapi import HTTPException, Response, status
from app.core.exceptions import EntityNotFound, ValidationError
from app.services.chunk_service import ChunkService
from app.models.schema import Chunk

class ChunkController:
    def __init__(self, svc: ChunkService):
        self._svc = svc

    def create(self, lib_id: str, doc_id: str, chunk: Chunk) -> Chunk:
        try:
            return self._svc.add_chunk(lib_id, doc_id, chunk)
        except EntityNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    def read(self, lib_id: str, doc_id: str, chunk_id: str) -> Chunk:
        try:
            return self._svc.get_chunk(lib_id, doc_id, chunk_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    def update(self, lib_id: str, doc_id: str, chunk_id: str, chunk: Chunk) -> Chunk:
        if chunk.id != chunk_id:
            raise HTTPException(status_code=400, detail="ID mismatch")
        try:
            return self._svc.update_chunk(lib_id, doc_id, chunk)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete(self, lib_id: str, doc_id: str, chunk_id: str) -> Response:
        try:
            self._svc.delete_chunk(lib_id, doc_id, chunk_id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
