import pytest
from fastapi import status

def test_create_and_get_library(client):
    # Create
    r = client.post("/libraries", json={
        "id": "lib1", "name": "Knowledge Base", "tags": ["prod", "v1"]
    })
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["id"] == "lib1"
    assert data["name"] == "Knowledge Base"
    assert "created_at" in data

    # Read
    r = client.get("/libraries/lib1")
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["tags"] == ["prod", "v1"]

def test_update_and_delete_library(client):
    # Prep
    client.post("/libraries", json={"id": "lib2", "name": "Lib2", "tags": []})
    # Update name, add description & tags
    r = client.put("/libraries/lib2", json={
        "id": "lib2",
        "name": "Lib2 Updated",
        "description": "A test library",
        "tags": ["updated"],
        "documents": []
    })
    assert r.status_code == status.HTTP_200_OK
    upd = r.json()
    assert upd["name"] == "Lib2 Updated"
    assert upd["description"] == "A test library"

    # Delete
    r = client.delete("/libraries/lib2")
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Confirm gone
    r = client.get("/libraries/lib2")
    assert r.status_code == status.HTTP_404_NOT_FOUND

def test_duplicate_and_missing_library(client):
    # Duplicate ID
    client.post("/libraries", json={"id": "dup", "name": "First", "tags": []})
    r = client.post("/libraries", json={"id": "dup", "name": "Second", "tags": []})
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    # Missing fields
    r = client.post("/libraries", json={"id": "", "name": "", "tags": []})
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Fetch non-existent
    r = client.get("/libraries/doesnotexist")
    assert r.status_code == status.HTTP_404_NOT_FOUND
