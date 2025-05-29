from fastapi import APIRouter, Depends
from typing import List
from app.models.schema import Document
from app.controllers.document_controller import DocumentController
from app.di import get_document_controller

router = APIRouter(prefix="/libraries/{lib_id}/documents", tags=["Documents"])

@router.get("/", response_model=List[Document])
def list_documents(lib_id: str, ctl: DocumentController = Depends(get_document_controller)):
    lib = ctl._svc._r.get(lib_id)
    return lib.documents if lib else []

@router.post("/", response_model=Document, status_code=201)
def create_document(lib_id: str, doc: Document, ctl: DocumentController = Depends(get_document_controller)):
    return ctl.create(lib_id, doc)

@router.get("/{doc_id}", response_model=Document)
def read_document(lib_id: str, doc_id: str, ctl: DocumentController = Depends(get_document_controller)):
    return ctl.read(lib_id, doc_id)

@router.put("/{doc_id}", response_model=Document)
def update_document(lib_id: str, doc_id: str, doc: Document, ctl: DocumentController = Depends(get_document_controller)):
    return ctl.update(lib_id, doc_id, doc)

@router.delete("/{doc_id}", status_code=204)
def delete_document(lib_id: str, doc_id: str, ctl: DocumentController = Depends(get_document_controller)):
    return ctl.delete(lib_id, doc_id)
