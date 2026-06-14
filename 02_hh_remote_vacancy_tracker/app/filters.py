import re

from app.hh_client.schemas import HHVacancyItem


class VacancyFilter:
    def __init__(self, whitelist: list[str], blacklist: list[str]) -> None:
        self.whitelist = [item.lower() for item in whitelist]
        self.blacklist = [item.lower() for item in blacklist]

    def is_remote(self, vacancy: HHVacancyItem) -> bool:
        schedule = vacancy.schedule.name.lower() if vacancy.schedule else ""
        text = normalize(vacancy.searchable_text)
        return schedule == "удаленная работа" or any(
            marker in text
            for marker in ("remote", "удален", "удалён", "из дома")
        )

    def is_relevant(self, vacancy: HHVacancyItem) -> bool:
        text = normalize(vacancy.searchable_text)
        if any(keyword.lower() in text for keyword in self.blacklist):
            return False
        return any(keyword.lower() in text for keyword in self.whitelist)

    def matches(self, vacancy: HHVacancyItem) -> bool:
        return self.is_remote(vacancy) and self.is_relevant(vacancy)


def normalize(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value.lower()).strip()
