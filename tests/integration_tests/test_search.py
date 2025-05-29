import pytest
from fastapi import status

def test_search_flow(client, embed):
    # Setup
    lib_id = "searchlib"
    client.post("/libraries", json={"id": lib_id, "name": "SearchLib", "tags": []})
    client.post(f"/libraries/{lib_id}/documents", json={
        "id": "docS", "title": "SearchDoc", "author": "Zoe", "language": "en", "chunks": [], "tags": []
    })

    # Realistic chunk texts
    texts = [
        "Natural language processing enables chatbots.",
        "Quantum computing explores new physics."
    ]
    vectors = embed(texts)

    # Insert chunks
    for idx, (txt, vec) in enumerate(zip(texts, vectors), start=1):
        client.post(f"/libraries/{lib_id}/documents/docS/chunks", json={
            "id": f"c{idx}", "text": txt, "embedding": vec, "tags": []
        })

    # Rebuild index
    r = client.post(f"/libraries/{lib_id}/index")
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Positive search: expect first text
    query_vec = embed(["language models"])[0]
    r = client.post(f"/libraries/{lib_id}/search", json={"embedding": query_vec, "k": 1})
    assert r.status_code == status.HTTP_200_OK
    results = r.json()
    assert len(results) == 1
    assert "Natural language processing" in results[0]["text"]

@pytest.mark.parametrize("bad_payload", [
    {},  # missing fields
    {"embedding": "notalist", "k": 1},
    {"embedding": [1.0], "k": 0},  # k too small
])
def test_search_bad_requests(client, bad_payload):
    lib_id = "badsearch"
    client.post("/libraries", json={"id": lib_id, "name": "BadSearchLib", "tags": []})
    # missing chunks but test validation first
    r = client.post(f"/libraries/{lib_id}/search", json=bad_payload)
    assert r.status_code in {status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST}

def test_search_no_library(client, embed):
    r = client.post("/libraries/nolib/search", json={"embedding": embed(["x"])[0], "k": 1})
    assert r.status_code == status.HTTP_404_NOT_FOUND
