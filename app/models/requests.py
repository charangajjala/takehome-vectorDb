from typing import List
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    embedding: List[float] = Field(
        ...,
        description="Query embedding vector"
    )
    k: int = Field(
        10,
        ge=1,
        description="Number of nearest neighbors to return"
    )