from io import BytesIO
from typing import Protocol

from pypdf import PdfReader

from app.ingestion.types import ExtractedText


class PdfPage(Protocol):
    def extract_text(self) -> str | None:
        ...


def extract_pdf_pages(content: bytes) -> list[ExtractedText]:
    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise ValueError("PDF could not be read") from exc
    return extract_pages_from_reader(reader.pages)


def extract_pages_from_reader(pages: list[PdfPage]) -> list[ExtractedText]:
    extracted: list[ExtractedText] = []
    for index, page in enumerate(pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            extracted.append(ExtractedText(text=text, page=index))
    return extracted
