import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from app.services.rag_service import RAGService
from app.services.semantic_search_service import SearchHit


class FakeSemanticSearchService:
    def __init__(self, hits: list[SearchHit]) -> None:
        self.hits = hits
        self.last_query = None
        self.last_owner_id = None

    def search_for_owner(self, query: str, owner_id: str, *, limit: int = 5) -> list[SearchHit]:
        self.last_query = query
        self.last_owner_id = owner_id
        return self.hits


def test_rag_service_generates_grounded_answer() -> None:
    # Arrange
    test_hit = SearchHit(
        chunk_id="chunk-1",
        document_id="doc-123",
        document_title="HR Leave Policy",
        category="HR",
        content="Employees get 25 days of annual leave.",
        page_start=1,
        page_end=1,
        relevance_score=0.95,
    )
    fake_search = FakeSemanticSearchService([test_hit])

    # Setup fake LLM response
    fake_llm = FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content=(
                    "According to the HR Leave Policy, employees get 25 days "
                    "of annual leave."
                )
            )
        ]
    )

    rag_service = RAGService(semantic_search_service=fake_search, llm=fake_llm)

    # Act
    answer, hits = rag_service.answer_query(
        query="How many days of leave do I get?",
        owner_id="user-123",
    )

    # Assert
    assert answer == "According to the HR Leave Policy, employees get 25 days of annual leave."
    assert len(hits) == 1
    assert hits[0].chunk_id == "chunk-1"
    assert fake_search.last_query == "How many days of leave do I get?"
    assert fake_search.last_owner_id == "user-123"


@pytest.mark.anyio
async def test_rag_service_streams_answer() -> None:
    # Arrange
    test_hit = SearchHit(
        chunk_id="chunk-1",
        document_id="doc-123",
        document_title="HR Leave Policy",
        category="HR",
        content="Employees get 25 days of annual leave.",
        page_start=1,
        page_end=1,
        relevance_score=0.95,
    )
    fake_search = FakeSemanticSearchService([test_hit])

    fake_llm = FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content=(
                    "According to the HR Leave Policy, employees get 25 days "
                    "of annual leave."
                )
            )
        ]
    )

    rag_service = RAGService(semantic_search_service=fake_search, llm=fake_llm)

    # Act
    chunks = []
    async for chunk in rag_service.stream_answer(
        query="How many days of leave do I get?",
        owner_id="user-123",
    ):
        chunks.append(chunk)

    # Assert
    assert len(chunks) >= 2
    assert chunks[0]["type"] == "sources"
    assert len(chunks[0]["sources"]) == 1
    assert chunks[0]["sources"][0]["document_id"] == "doc-123"

    # Verify we got tokens
    tokens = [c["token"] for c in chunks if c["type"] == "token"]
    full_answer = "".join(tokens)
    assert "According to the HR Leave Policy" in full_answer


@pytest.mark.anyio
async def test_rag_service_falls_back_to_extractive_answer_when_llm_fails() -> None:
    test_hit = SearchHit(
        chunk_id="chunk-1",
        document_id="doc-123",
        document_title="Security Policy",
        category="security",
        content="Passwords must be at least 14 characters and use MFA.",
        page_start=2,
        page_end=2,
        relevance_score=0.91,
    )
    fake_search = FakeSemanticSearchService([test_hit])

    class FailingLlm:
        async def astream(self, messages):
            raise RuntimeError("provider unavailable")
            yield

        def stream(self, messages):
            raise RuntimeError("provider unavailable")

    rag_service = RAGService(semantic_search_service=fake_search, llm=FailingLlm())

    chunks = []
    async for chunk in rag_service.stream_answer(
        query="What are the password requirements?",
        owner_id="user-123",
    ):
        chunks.append(chunk)

    tokens = [chunk["token"] for chunk in chunks if chunk["type"] == "token"]
    answer = "".join(tokens)
    assert "Based on Security Policy" in answer
    assert "Passwords must be at least 14 characters" in answer
