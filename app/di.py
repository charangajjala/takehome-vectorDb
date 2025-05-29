from functools import lru_cache
from fastapi import Depends
from app.config import Settings, get_settings
from app.repositories.in_memory_repository import InMemoryRepository
from app.indexers.bruteforce import BruteForceIndexer
from app.indexers.vptree import VPTreeIndexer
from app.services.library_service import LibraryService
from app.services.document_service import DocumentService
from app.services.chunk_service import ChunkService
from app.controllers.library_controller import LibraryController
from app.controllers.document_controller import DocumentController
from app.controllers.chunk_controller import ChunkController
from app.models.schema import Library

@lru_cache()
def get_repository() -> InMemoryRepository[Library]:
    return InMemoryRepository[Library]()

@lru_cache()
def get_library_controller() -> LibraryController:
    repo     = get_repository()
    settings = get_settings()
    idx      = VPTreeIndexer() if settings.INDEXER_TYPE=="vptree" else BruteForceIndexer()
    svc      = LibraryService(repo, repo, idx)
    return LibraryController(svc)

@lru_cache()
def get_document_controller() -> DocumentController:
    repo = get_repository()
    svc  = DocumentService(repo, repo)
    return DocumentController(svc)

@lru_cache()
def get_chunk_controller() -> ChunkController:
    repo = get_repository()
    svc  = ChunkService(repo, repo)
    return ChunkController(svc)