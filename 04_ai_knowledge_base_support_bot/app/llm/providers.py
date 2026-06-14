from typing import Protocol

import httpx

from app.config import settings
from app.llm.prompt import build_rag_prompt
from app.retrieval.search import SearchResult


class LLMProvider(Protocol):
    async def answer(self, question: str, results: list[SearchResult]) -> str:
        ...


class ExtractiveLLMProvider:
    async def answer(self, question: str, results: list[SearchResult]) -> str:
        if not results:
            return "В базе знаний нет подходящего ответа."
        best = results[0]
        return f"{best.text}\n\nИсточник: {best.document}, фрагмент {best.index}."


class OpenAICompatibleLLMProvider:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.llm_base_url,
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=45,
        )

    async def answer(self, question: str, results: list[SearchResult]) -> str:
        prompt = build_rag_prompt(question, results)
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()


def get_llm_provider() -> LLMProvider:
    if settings.llm_api_key:
        return OpenAICompatibleLLMProvider()
    return ExtractiveLLMProvider()
