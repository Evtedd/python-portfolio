from typing import Protocol

import httpx

from app.config import settings
from app.schemas import SearchResultRead


class LLMProvider(Protocol):
    async def answer(self, question: str, sources: list[SearchResultRead]) -> str:
        ...


class ExtractiveLLM:
    async def answer(self, question: str, sources: list[SearchResultRead]) -> str:
        if not sources:
            return "В индексе нет подходящих материалов."
        snippets = "\n".join(f"{source.filename}: {source.text}" for source in sources[:4])
        return f"Найденные материалы по запросу: {question}\n{snippets}"


class OpenAICompatibleLLM:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.llm_base_url,
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=45,
        )

    async def answer(self, question: str, sources: list[SearchResultRead]) -> str:
        context = "\n\n".join(f"{item.filename}: {item.text}" for item in sources)
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": settings.llm_model,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Answer using only the indexed context. Cite filenames.\n\n"
                            f"Context:\n{context}\n\nQuestion: {question}"
                        ),
                    },
                ],
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()


def get_llm() -> LLMProvider:
    if settings.llm_api_key:
        return OpenAICompatibleLLM()
    return ExtractiveLLM()
