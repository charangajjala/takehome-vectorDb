import pytest
from app.services.library_service import LibraryService
from app.repositories.in_memory_repository import InMemoryRepository
from app.indexers.bruteforce import BruteForceIndexer
from app.models.schema import Library, Chunk
from app.core.exceptions import EntityNotFound, ValidationError

@pytest.fixture
def lib_svc():
    repo = InMemoryRepository[Library]()
    idx  = BruteForceIndexer()
    return LibraryService(repo, repo, idx)

def test_create_and_get(lib_svc):
    lib = Library(id="L1", name="Lib1", description=None, documents=[], tags=[])
    out = lib_svc.create_library(lib)
    assert out.id == "L1"
    assert lib_svc.get_library("L1").name == "Lib1"

def test_blank_name(lib_svc):
    with pytest.raises(ValidationError):
        lib_svc.create_library(Library(id="X", name="   ", description=None, documents=[], tags=[]))

def test_get_missing(lib_svc):
    with pytest.raises(EntityNotFound):
        lib_svc.get_library("missing")

def test_search_empty(lib_svc):
    lib_svc.create_library(Library(id="L2", name="Empty", description=None, documents=[], tags=[]))
    results = lib_svc.search("L2", embedding=[1.0], k=5)
    assert results == []

def test_search_with_chunks(lib_svc):
    # create lib and doc with one chunk
    lib = Library(
        id="L3", name="WithChunks", description=None, documents=[
            # Document injection omitted for brevity
        ], tags=[]
    )
    # skip doc layer; simulate direct index
    chunk = Chunk(id="c1", text="a", embedding=[1.0, 0.0], tags=[])
    lib.documents = []
    from copy import deepcopy
    lib2 = deepcopy(lib)
    lib_svc._w.create(lib2)
    # manually build and query
    idx = lib_svc._idx
    idx.build([chunk])
    res = idx.query([1.0, 0.0], k=1)
    assert res[0][0].id == "c1"
