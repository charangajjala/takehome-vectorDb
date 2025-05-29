from fastapi import APIRouter, Depends, Query
from typing import List
from app.models.requests import SearchRequest
from app.models.schema import Library, Chunk
from app.controllers.library_controller import LibraryController
from app.di import get_library_controller

router = APIRouter(prefix="/libraries", tags=["Libraries"])

@router.get("/", response_model=List[Library])
def list_libraries(ctl: LibraryController = Depends(get_library_controller)):
    return ctl._svc._r.list()

@router.post("/", response_model=Library, status_code=201)
def create_library(lib: Library, ctl: LibraryController = Depends(get_library_controller)):
    return ctl.create(lib)

@router.get("/{lib_id}", response_model=Library)
def read_library(lib_id: str, ctl: LibraryController = Depends(get_library_controller)):
    return ctl.read(lib_id)

@router.put("/{lib_id}", response_model=Library)
def update_library(lib_id: str, lib: Library, ctl: LibraryController = Depends(get_library_controller)):
    return ctl.update(lib_id, lib)

@router.delete("/{lib_id}", status_code=204)
def delete_library(lib_id: str, ctl: LibraryController = Depends(get_library_controller)):
    return ctl.delete(lib_id)

@router.post("/{lib_id}/index", status_code=204)
def rebuild_index(lib_id: str, ctl: LibraryController = Depends(get_library_controller)):
    return ctl.rebuild_index(lib_id)

@router.post(
    "/{lib_id}/search",
    response_model=List[Chunk],
    summary="k-NN search within a library"
)
def search(
    lib_id: str,
    payload: SearchRequest,
    ctl: LibraryController = Depends(get_library_controller)
):
    return ctl.search(lib_id, payload.embedding, payload.k)
