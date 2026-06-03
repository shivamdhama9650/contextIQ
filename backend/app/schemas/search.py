from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class SearchHitResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    category: str
    content: str
    page_start: int
    page_end: int
    relevance_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchHitResponse]


class VectorIndexResponse(BaseModel):
    document_id: str
    vector_count: int
    message: str
