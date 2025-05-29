import pytest
from fastapi import status

@pytest.fixture(autouse=True)
def clear_repos(client):
    for lib in client.get("/libraries").json():
        client.delete(f"/libraries/{lib['id']}")

def test_add_and_get_chunk(client):
    # Prepare library + document
    client.post("/libraries", json={"id": "libc", "name": "LibC", "tags": []})
    client.post("/libraries/libc/documents", json={
        "id": "docc", "title": "DocC", "author": "Eve", "language": "en", "chunks": [], "tags": []
    })

    # Add chunk
    chunk = {
        "id": "ch100",
        "text": "Deep learning revolutionizes vision.",
        "embedding": [0.1, 0.2, 0.3],
        "tags": ["ml", "vision"]
    }
    r = client.post("/libraries/libc/documents/docc/chunks", json=chunk)
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["text"].startswith("Deep learning")

    # Get it back
    r = client.get("/libraries/libc/documents/docc/chunks/ch100")
    assert r.status_code == status.HTTP_200_OK

def test_update_and_delete_chunk(client):
    client.post("/libraries", json={"id": "libc2", "name": "LibC2", "tags": []})
    client.post("/libraries/libc2/documents", json={
        "id": "docc2", "title": "DocC2", "author": None, "language": "en", "chunks": [], "tags": []
    })
    client.post("/libraries/libc2/documents/docc2/chunks", json={
        "id": "ch200", "text": "Initial", "embedding": [1.0], "tags": []
    })

    # Update
    r = client.put("/libraries/libc2/documents/docc2/chunks/ch200", json={
        "id": "ch200", "text": "Updated text", "embedding": [0.5, 0.5], "tags": ["updated"]
    })
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["tags"] == ["updated"]

    # Delete
    r = client.delete("/libraries/libc2/documents/docc2/chunks/ch200")
    assert r.status_code == status.HTTP_204_NO_CONTENT
    # Confirm
    r = client.get("/libraries/libc2/documents/docc2/chunks/ch200")
    assert r.status_code == status.HTTP_404_NOT_FOUND

def test_chunk_errors(client):
    # No lib/doc
    r = client.post("/libraries/nolib/documents/nodoc/chunks", json={
        "id": "cX", "text": "X", "embedding": [0.1], "tags": []
    })
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # Duplicate chunk
    client.post("/libraries", json={"id": "libxce", "name": "LibX", "tags": []})
    client.post("/libraries/libxce/documents", json={
        "id": "docxce", "title": "DocX", "author": None, "language": "en", "chunks": [], "tags": []
    })
    client.post("/libraries/libxce/documents/docxce/chunks", json={
        "id": "dupC", "text": "dup", "embedding": [0], "tags": []
    })
    r = client.post("/libraries/libxce/documents/docxce/chunks", json={
        "id": "dupC", "text": "dup", "embedding": [0], "tags": []
    })
    assert r.status_code == status.HTTP_400_BAD_REQUEST
