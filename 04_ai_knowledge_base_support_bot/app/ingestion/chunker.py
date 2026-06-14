from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    text: str
    page: int | None


def chunk_text(text: str, chunk_size: int, overlap: int, page: int | None = None) -> list[TextChunk]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    words = text.split()
    chunks: list[TextChunk] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(TextChunk(text=chunk, page=page))
        if end == len(words):
            break
        start = end - overlap
    return chunks
