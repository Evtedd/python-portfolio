from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


def parse_resume(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(content)
    text = content.decode("utf-8", errors="replace").strip()
    if not text:
        raise ValueError("Resume is empty")
    return text


def parse_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise ValueError("PDF could not be read") from exc

    text = "\n".join((page.extract_text() or "").strip() for page in reader.pages)
    text = text.strip()
    if not text:
        raise ValueError("PDF has no readable text")
    return text
