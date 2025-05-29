import os
import pytest
import cohere
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client() -> TestClient:
    """A TestClient for the FastAPI app."""
    return TestClient(app)

@pytest.fixture(scope="session")
def cohere_client() -> cohere.Client:
    """A Cohere client for embedding generation."""
    api_key = os.getenv("COHERE_API_KEY")
    assert api_key, "Please set COHERE_API_KEY for embedding tests"
    return cohere.Client(api_key)

@pytest.fixture
def embed(cohere_client):
    """
    Returns a function that takes a list of strings and returns
    their embeddings from Cohere.
    """
    def _embed(texts: list[str]) -> list[list[float]]:
        resp = cohere_client.embed(texts=texts)
        return resp.embeddings
    return _embed
