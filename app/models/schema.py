from datetime import datetime
from typing import Annotated, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class BaseEntity(BaseModel):
    
    id: str = Field(..., description="Unique identifier")
    tags: List[str] = Field(default_factory=list, description="Optional tags")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")


class Chunk(BaseEntity):
    text: str = Field(..., min_length=1, description="Raw chunk text")
    embedding: Annotated[List[float], Field(min_length=1)]  


class Document(BaseEntity):
    title: str = Field(..., min_length=1, description="Document title")
    author: Optional[str]   = Field(None, description="Author/source")
    language: Optional[str] = Field("en", description="ISO language code")
    chunks: List[Chunk]     = Field(default_factory=list, description="Chunks in this document")

class Library(BaseEntity):
    name: str = Field(..., min_length=1, description="Library name")
    description: Optional[str]     = Field(None, description="Library description")
    documents: List[Document]      = Field(default_factory=list, description="Documents in this library")
