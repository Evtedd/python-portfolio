from app.llm.prompts import build_match_prompt
from app.schemas import VacancyData


def test_build_match_prompt_contains_resume_and_vacancy():
    prompt = build_match_prompt(
        "Python, FastAPI",
        VacancyData(title="Backend Python", text="Need FastAPI and Docker"),
    )

    assert "Backend Python" in prompt
    assert "Python, FastAPI" in prompt
    assert "strict JSON" in prompt
