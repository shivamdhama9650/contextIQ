from app.chunking.text_chunker import TextChunker


def test_chunker_splits_long_page_into_multiple_chunks() -> None:
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    pages = [
        {
            "id": "page-1",
            "page_number": 1,
            "text_content": "A" * 250,
        }
    ]

    chunks = chunker.chunk_pages(pages)

    assert len(chunks) >= 2
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 1
    assert chunks[0].token_count > 0


def test_chunker_skips_empty_pages() -> None:
    chunker = TextChunker()
    pages = [
        {"id": "page-1", "page_number": 1, "text_content": ""},
        {"id": "page-2", "page_number": 2, "text_content": "Leave policy details"},
    ]

    chunks = chunker.chunk_pages(pages)

    assert len(chunks) == 1
    assert "Leave policy" in chunks[0].content


def test_chunker_preserves_sentence_boundaries_when_possible() -> None:
    chunker = TextChunker(chunk_size=80, chunk_overlap=20)
    pages = [
        {
            "id": "page-1",
            "page_number": 1,
            "text_content": (
                "Employees can request leave through the HR portal. "
                "Managers review requests within three business days. "
                "Approved leave is visible in the employee dashboard."
            ),
        }
    ]

    chunks = chunker.chunk_pages(pages)

    assert len(chunks) >= 2
    assert chunks[0].content.endswith(".")
    assert chunks[0].metadata["strategy"] == "recursive_structure_overlap"


def test_chunker_normalizes_whitespace() -> None:
    chunker = TextChunker()
    pages = [
        {
            "id": "page-1",
            "page_number": 1,
            "text_content": "Policy   title\r\n\r\n\r\nDetails\twith extra spacing.",
        }
    ]

    chunks = chunker.chunk_pages(pages)

    assert len(chunks) == 1
    assert "Policy title" in chunks[0].content
    assert "\r" not in chunks[0].content
