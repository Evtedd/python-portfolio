import hashlib
import math
from dataclasses import dataclass


@dataclass
class MemoryItem:
    text: str
    vector: list[float]


class VectorMemory:
    def __init__(self) -> None:
        self.items: list[MemoryItem] = []

    def save(self, text: str) -> None:
        self.items.append(MemoryItem(text=text, vector=embed(text)))

    def search(self, query: str, limit: int = 3) -> list[str]:
        query_vector = embed(query)
        scored = [(item.text, cosine(query_vector, item.vector)) for item in self.items]
        return [text for text, _ in sorted(scored, key=lambda item: item[1], reverse=True)[:limit]]


def embed(text: str, dimensions: int = 64) -> list[float]:
    vector = [0.0] * dimensions
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        vector[int.from_bytes(digest[:2], "big") % dimensions] += 1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))
