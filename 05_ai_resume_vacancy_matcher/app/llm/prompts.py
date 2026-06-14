from app.schemas import VacancyData


def build_match_prompt(resume_text: str, vacancy: VacancyData) -> str:
    return (
        "Compare the resume with the vacancy and return strict JSON with keys: "
        "score, matched_skills, missing_skills, cover_letter, reasoning, "
        "is_remote, is_suspicious.\n\n"
        f"Vacancy title: {vacancy.title}\n"
        f"Company: {vacancy.company or 'unknown'}\n"
        f"Vacancy text:\n{vacancy.text}\n\n"
        f"Resume:\n{resume_text}\n"
    )
