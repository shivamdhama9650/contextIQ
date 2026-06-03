import re
from dataclasses import dataclass

DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 180


@dataclass(frozen=True)
class TextChunkDraft:
    chunk_index: int
    content: str
    page_start: int
    page_end: int
    page_id: str | None
    token_count: int
    metadata: dict[str, int | str]


class TextChunker:
    """
    Splits page text into overlapping chunks for embedding and RAG retrieval.

    The splitter preserves document structure where possible. It prefers
    paragraphs, then sentences, then words, and only falls back to character
    windows for unusually long unbroken text.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: list[dict]) -> list[TextChunkDraft]:
        drafts: list[TextChunkDraft] = []
        chunk_index = 0

        for page in pages:
            text = self._normalize_text(str(page.get("text_content") or ""))
            page_number = int(page["page_number"])
            page_id = page.get("id")

            if not text:
                continue

            for piece in self._split_text(text):
                drafts.append(
                    TextChunkDraft(
                        chunk_index=chunk_index,
                        content=piece,
                        page_start=page_number,
                        page_end=page_number,
                        page_id=str(page_id) if page_id else None,
                        token_count=self._estimate_tokens(piece),
                        metadata={
                            "strategy": "recursive_structure_overlap",
                            "chunk_size": self.chunk_size,
                            "chunk_overlap": self.chunk_overlap,
                        },
                    )
                )
                chunk_index += 1

        return drafts

    def _split_text(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        units = self._split_into_units(text)
        chunks: list[str] = []
        current = ""

        for unit in units:
            if len(unit) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(self._split_oversized_unit(unit))
                continue

            candidate = f"{current}\n\n{unit}".strip() if current else unit
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = self._merge_with_overlap(chunks[-1] if chunks else "", unit)

        if current:
            chunks.append(current)

        return chunks

    def _split_into_units(self, text: str) -> list[str]:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        units: list[str] = []

        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                units.append(paragraph)
                continue

            sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
                if sentence.strip()
            ]
            units.extend(sentences or [paragraph])

        return units

    def _split_oversized_unit(self, text: str) -> list[str]:
        words = text.split()
        if len(words) <= 1:
            return self._split_by_char_window(text)

        chunks: list[str] = []
        current_words: list[str] = []
        current_length = 0

        for word in words:
            additional_length = len(word) + (1 if current_words else 0)
            if current_words and current_length + additional_length > self.chunk_size:
                chunk = " ".join(current_words)
                chunks.append(chunk)
                overlap_text = self._tail_overlap(chunk)
                current_words = overlap_text.split() if overlap_text else []
                current_length = len(" ".join(current_words))

            current_words.append(word)
            current_length += additional_length

        if current_words:
            chunks.append(" ".join(current_words))

        return chunks

    def _split_by_char_window(self, text: str) -> list[str]:
        pieces: list[str] = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            piece = text[start:end].strip()
            if piece:
                pieces.append(piece)
            if end >= len(text):
                break
            start = end - self.chunk_overlap

        return pieces

    def _merge_with_overlap(self, previous: str, unit: str) -> str:
        overlap = self._tail_overlap(previous)
        candidate = f"{overlap}\n\n{unit}".strip() if overlap else unit
        if len(candidate) <= self.chunk_size:
            return candidate
        return unit

    def _tail_overlap(self, text: str) -> str:
        if not text or self.chunk_overlap <= 0:
            return ""

        tail = text[-self.chunk_overlap :]
        boundary = max(tail.find(". "), tail.find("\n"), tail.find(" "))
        if boundary > 0:
            tail = tail[boundary + 1 :]
        return tail.strip()

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        # Rough OpenAI-style estimate for planning embedding batch sizes.
        return max(1, len(text) // 4)
