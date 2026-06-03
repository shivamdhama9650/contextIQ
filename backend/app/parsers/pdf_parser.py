from dataclasses import dataclass

import fitz


@dataclass(frozen=True)
class ParsedPage:
    page_number: int
    text_content: str
    metadata: dict[str, str | int | float]


class PdfParserService:
    """Extracts text from PDF bytes using PyMuPDF (fitz)."""

    def parse(self, content: bytes) -> list[ParsedPage]:
        document = fitz.open(stream=content, filetype="pdf")
        pages: list[ParsedPage] = []

        try:
            for index in range(document.page_count):
                page = document.load_page(index)
                text = page.get_text("text").strip()
                pages.append(
                    ParsedPage(
                        page_number=index + 1,
                        text_content=text,
                        metadata={
                            "width": round(page.rect.width, 2),
                            "height": round(page.rect.height, 2),
                            "char_count": len(text),
                        },
                    )
                )
        finally:
            document.close()

        return pages
