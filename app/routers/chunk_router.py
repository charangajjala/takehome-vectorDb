from fastapi import APIRouter, Depends
from typing import List
from app.models.schema import Chunk
from app.controllers.chunk_controller import ChunkController
from app.di import get_chunk_controller

router = APIRouter(prefix="/libraries/{lib_id}/documents/{doc_id}/chunks", tags=["Chunks"])

@router.get("/", response_model=List[Chunk])
def list_chunks(lib_id: str, doc_id: str, ctl: ChunkController = Depends(get_chunk_controller)):
    lib = ctl._svc._r.get(lib_id)
    return next((d.chunks for d in lib.documents if d.id == doc_id), [])

@router.post("/", response_model=Chunk, status_code=201)
def create_chunk(lib_id: str, doc_id: str, chunk: Chunk, ctl: ChunkController = Depends(get_chunk_controller)):
    return ctl.create(lib_id, doc_id, chunk)

@router.get("/{chunk_id}", response_model=Chunk)
def read_chunk(lib_id: str, doc_id: str, chunk_id: str, ctl: ChunkController = Depends(get_chunk_controller)):
    return ctl.read(lib_id, doc_id, chunk_id)

@router.put("/{chunk_id}", response_model=Chunk)
def update_chunk(lib_id: str, doc_id: str, chunk_id: str, chunk: Chunk, ctl: ChunkController = Depends(get_chunk_controller)):
    return ctl.update(lib_id, doc_id, chunk_id, chunk)

@router.delete("/{chunk_id}", status_code=204)
def delete_chunk(lib_id: str, doc_id: str, chunk_id: str, ctl: ChunkController = Depends(get_chunk_controller)):
    return ctl.delete(lib_id, doc_id, chunk_id)
