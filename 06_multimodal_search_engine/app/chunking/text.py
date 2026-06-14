from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    text: str
    page: int | None = None
    start_seconds: float | None = None
    end_seconds: float | None = None


def chunk_words(
    text: str,
    size: int,
    overlap: int,
    page: int | None = None,
    start_seconds: float | None = None,
    end_seconds: float | None = None,
) -> list[Chunk]:
    if size <= overlap:
        raise ValueError("chunk size must be greater than overlap")

    words = text.split()
    chunks: list[Chunk] = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunk_text = " ".join(words[start:end]).strip()
        if chunk_text:
            chunks.append(
                Chunk(
                    text=chunk_text,
                    page=page,
                    start_seconds=start_seconds,
                    end_seconds=end_seconds,
                ),
            )
        if end == len(words):
            break
        start = end - overlap
    return chunks
