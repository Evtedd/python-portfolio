from app.filters import VacancyFilter
from app.hh_client.schemas import HHVacancyItem


def make_vacancy(
    name: str,
    requirement: str,
    schedule: str = "Удаленная работа",
) -> HHVacancyItem:
    return HHVacancyItem.model_validate(
        {
            "id": "1",
            "name": name,
            "alternate_url": "https://hh.ru/vacancy/1",
            "employer": {"name": "Company"},
            "schedule": {"name": schedule},
            "snippet": {"requirement": requirement, "responsibility": ""},
        },
    )


def test_filter_accepts_remote_python_vacancy():
    vacancy_filter = VacancyFilter(["Python", "FastAPI"], ["продажи"])
    vacancy = make_vacancy("Python developer", "FastAPI, PostgreSQL")

    assert vacancy_filter.matches(vacancy)


def test_filter_rejects_blacklist():
    vacancy_filter = VacancyFilter(["Python"], ["преподаватель"])
    vacancy = make_vacancy("Преподаватель Python", "Удаленно")

    assert not vacancy_filter.matches(vacancy)


def test_filter_rejects_office_work():
    vacancy_filter = VacancyFilter(["Python"], ["продажи"])
    vacancy = make_vacancy("Python developer", "Django", schedule="Полный день")

    assert not vacancy_filter.matches(vacancy)
