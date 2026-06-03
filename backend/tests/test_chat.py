from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.chat import get_rag_service
from app.main import app

client = TestClient(app)


def test_chat_streaming_endpoint():
    """Verify that the chat streaming endpoint returns a valid SSE stream of sources and tokens."""
    # 1. Mock RAGService
    mock_rag = MagicMock()

    async def mock_stream_answer(query, k, owner_id):
        yield {
            "type": "sources",
            "sources": [{"document_id": "doc-123", "page_number": 1, "text": "chunk text"}],
        }
        yield {"type": "token", "token": "Hello "}
        yield {"type": "token", "token": "world!"}

    mock_rag.stream_answer = mock_stream_answer

    # 2. Override dependency in FastAPI
    app.dependency_overrides[get_rag_service] = lambda: mock_rag

    try:
        # 3. Request streaming endpoint
        response = client.post("/api/chat", json={"query": "hello", "k": 5})
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # 4. Check that standard SSE tags are present in the response payload
        content = response.text
        assert "event: sources" in content
        assert "event: token" in content
        assert "chunk text" in content
        assert "Hello " in content
        assert "world!" in content

    finally:
        app.dependency_overrides.clear()
