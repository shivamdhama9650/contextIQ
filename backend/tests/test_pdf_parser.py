import fitz

from app.parsers.pdf_parser import PdfParserService


def make_sample_pdf(text: str = "Leave policy section one.") -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_pdf_parser_extracts_page_text() -> None:
    parser = PdfParserService()
    pages = parser.parse(make_sample_pdf("How do I apply for leave?"))

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "apply for leave" in pages[0].text_content
    assert pages[0].metadata["char_count"] > 0


def test_pdf_parser_handles_multiple_pages() -> None:
    document = fitz.open()
    first = document.new_page()
    first.insert_text((72, 72), "Page one")
    second = document.new_page()
    second.insert_text((72, 72), "Page two")
    content = document.tobytes()
    document.close()

    pages = PdfParserService().parse(content)

    assert len(pages) == 2
    assert pages[0].text_content == "Page one"
    assert pages[1].text_content == "Page two"
