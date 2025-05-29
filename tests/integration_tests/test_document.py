import pytest
from fastapi import status

@pytest.fixture(autouse=True)
def clear_repos(client):
    # ensure clean state by deleting any libs between tests
    # (since we're in-memory, deleting root libraries suffices)
    # fetch all and delete
    libs = client.get("/libraries").json()
    for lib in libs:
        client.delete(f"/libraries/{lib['id']}")

def test_add_and_get_document(client):
    # Setup library
    client.post("/libraries", json={"id": "doclib", "name": "DocLib", "tags": []})

    # Add document
    payload = {
        "id": "doc1",
        "title": "API Design Best Practices",
        "author": "Alice",
        "language": "en",
        "chunks": [],
        "tags": ["api", "design"]
    }
    r = client.post("/libraries/doclib/documents", json=payload)
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["id"] == "doc1"

    # Read it back
    r = client.get("/libraries/doclib/documents/doc1")
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["title"] == "API Design Best Practices"

def test_update_and_delete_document(client):
    # Setup
    client.post("/libraries", json={"id": "libdoc", "name": "LibDoc", "tags": []})
    client.post("/libraries/libdoc/documents", json={
        "id": "d1", "title": "T1", "author": None, "language": "en", "chunks": [], "tags": []
    })

    # Update
    r = client.put("/libraries/libdoc/documents/d1", json={
        "id": "d1", "title": "T1 Updated", "author": "Bob", "language": "fr", "chunks": [], "tags": []
    })
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["language"] == "fr"

    # Delete
    r = client.delete("/libraries/libdoc/documents/d1")
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Confirm
    r = client.get("/libraries/libdoc/documents/d1")
    assert r.status_code == status.HTTP_404_NOT_FOUND

def test_document_errors(client):
    # Missing library
    r = client.post("/libraries/nolib/documents", json={
        "id": "dx", "title": "X", "author": None, "language": "en", "chunks": [], "tags": []
    })
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # Duplicate document
    client.post("/libraries", json={"id": "libd", "name": "LibD", "tags": []})
    client.post("/libraries/libd/documents", json={
        "id": "dup", "title": "Dup", "author": None, "language": "en", "chunks": [], "tags": []
    })
    r = client.post("/libraries/libd/documents", json={
        "id": "dup", "title": "Dup", "author": None, "language": "en", "chunks": [], "tags": []
    })
    assert r.status_code == status.HTTP_400_BAD_REQUEST
