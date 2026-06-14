from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class ParsedPage:
    text: str
    page: int | None = None


def parse_document(filename: str, content: bytes) -> list[ParsedPage]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(content)
    if suffix in {".txt", ".md"}:
        text = content.decode("utf-8", errors="replace").strip()
        return [ParsedPage(text=text, page=None)] if text else []
    raise ValueError("Supported formats: PDF, TXT, MD")


def parse_pdf(content: bytes) -> list[ParsedPage]:
    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise ValueError("PDF could not be read") from exc

    pages: list[ParsedPage] = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(ParsedPage(text=text, page=index))
    return pages
