import pytest
from app.repositories.in_memory_repository import InMemoryRepository
from app.models.schema import Library

@pytest.fixture
def repo():
    return InMemoryRepository[Library]()

def test_crud(repo):
    lib = Library(id="L1", name="TestLib", description=None, documents=[], tags=[])
    repo.create(lib)
    fetched = repo.get("L1")
    assert fetched.name == "TestLib"

    # update
    lib2 = Library(id="L1", name="Updated", description=None, documents=[], tags=[])
    repo.update(lib2)
    assert repo.get("L1").name == "Updated"

    # delete
    repo.delete("L1")
    assert repo.get("L1") is None

def test_list(repo):
    repo.create(Library(id="A", name="A", description=None, documents=[], tags=[]))
    repo.create(Library(id="B", name="B", description=None, documents=[], tags=[]))
    ids = {l.id for l in repo.list()}
    assert ids == {"A", "B"}
