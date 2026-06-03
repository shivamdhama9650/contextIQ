from pydantic import BaseModel, Field


class Source(BaseModel):
    document_id: str = Field(..., description="Supabase document ID")
    page_number: int | None = Field(
        None,
        description="Page number in the original PDF, when available",
    )
    text: str = Field(..., description="Excerpt that contributed to the answer")


class QueryRequest(BaseModel):
    query: str = Field(..., description="User question to answer")
    k: int | None = Field(5, description="Number of chunks to use as context")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="LLM-generated answer")
    sources: list[Source] = Field(
        ...,
        description="Source chunks that ground the answer",
    )

