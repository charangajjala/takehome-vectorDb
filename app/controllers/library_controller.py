from fastapi import HTTPException, Response, status
from typing import List
from app.services.library_service import LibraryService
from app.models.schema import Library, Chunk

class LibraryController:
    def __init__(self, svc: LibraryService):
        self._svc = svc

    def create(self, lib: Library) -> Library:
        try:
            return self._svc.create_library(lib)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def read(self, lib_id: str) -> Library:
        try:
            return self._svc.get_library(lib_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    def update(self, lib_id: str, lib: Library) -> Library:
        if lib.id != lib_id:
            raise HTTPException(status_code=400, detail="ID mismatch")
        try:
            return self._svc.update_library(lib_id, lib)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def delete(self, lib_id: str) -> Response:
        try:
            self._svc.delete_library(lib_id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    def rebuild_index(self, lib_id: str) -> Response:
        try:
            lib = self._svc.get_library(lib_id)
            all_chunks = [c for d in lib.documents for c in d.chunks]
            self._svc._idx.build(all_chunks)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    def search(self, lib_id: str, embedding: List[float], k: int) -> List[Chunk]:
        try:
            return self._svc.search(lib_id, embedding, k)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
