import json
import re
from typing import Protocol

import httpx

from app.config import settings
from app.llm.prompts import build_match_prompt
from app.schemas import MatchAnalysis, VacancyData


class MatchAnalyzer(Protocol):
    def analyze(self, resume_text: str, vacancy: VacancyData) -> MatchAnalysis:
        ...


class OpenAICompatibleAnalyzer:
    def __init__(self) -> None:
        self.client = httpx.Client(
            base_url=settings.llm_base_url,
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=45,
        )

    def analyze(self, resume_text: str, vacancy: VacancyData) -> MatchAnalysis:
        prompt = build_match_prompt(resume_text, vacancy)
        response = self.client.post(
            "/chat/completions",
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return parse_llm_response(content)


class HeuristicAnalyzer:
    skills = [
        "python",
        "fastapi",
        "django",
        "sql",
        "postgresql",
        "docker",
        "asyncio",
        "sqlalchemy",
        "pytest",
        "git",
    ]

    def analyze(self, resume_text: str, vacancy: VacancyData) -> MatchAnalysis:
        resume_lower = resume_text.lower()
        vacancy_lower = vacancy.text.lower() + " " + vacancy.title.lower()
        required = [skill for skill in self.skills if skill in vacancy_lower]
        matched = [skill for skill in required if skill in resume_lower]
        missing = [skill for skill in required if skill not in resume_lower]
        score = 50 if not required else round(len(matched) / len(required) * 100)
        is_remote = any(marker in vacancy_lower for marker in ("remote", "удален", "удалён"))
        suspicious = any(marker in vacancy_lower for marker in ("продажи", "обучение", "офис"))
        cover_letter = (
            f"Здравствуйте. Меня заинтересовала вакансия {vacancy.title}. "
            f"В моём опыте есть "
            f"{', '.join(matched) if matched else 'релевантный backend опыт'}, "
            "и я готов быстро закрыть недостающие требования."
        )
        return MatchAnalysis(
            score=score,
            matched_skills=matched,
            missing_skills=missing,
            cover_letter=cover_letter,
            reasoning=(
                "Оценка построена по пересечению навыков резюме "
                "и текста вакансии."
            ),
            is_remote=is_remote,
            is_suspicious=suspicious,
        )


def parse_llm_response(content: str) -> MatchAnalysis:
    match = re.search(r"\{.*\}", content, flags=re.S)
    if match is None:
        raise ValueError("LLM response does not contain JSON")
    data = json.loads(match.group(0))
    return MatchAnalysis.model_validate(data)


def get_analyzer() -> MatchAnalyzer:
    if settings.llm_api_key:
        return OpenAICompatibleAnalyzer()
    return HeuristicAnalyzer()
