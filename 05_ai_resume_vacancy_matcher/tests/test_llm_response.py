from app.llm.client import HeuristicAnalyzer, parse_llm_response
from app.schemas import VacancyData


def test_parse_llm_response():
    analysis = parse_llm_response(
        """
        {
          "score": 88,
          "matched_skills": ["Python"],
          "missing_skills": ["Docker"],
          "cover_letter": "Hello",
          "reasoning": "Good match",
          "is_remote": true,
          "is_suspicious": false
        }
        """,
    )

    assert analysis.score == 88
    assert analysis.missing_skills == ["Docker"]


def test_heuristic_analyzer_scores_skill_overlap():
    analysis = HeuristicAnalyzer().analyze(
        "Python FastAPI SQLAlchemy pytest",
        VacancyData(
            title="Python backend",
            text="FastAPI, SQLAlchemy, Docker, remote",
        ),
    )

    assert analysis.score == 75
    assert analysis.is_remote
    assert "docker" in analysis.missing_skills
