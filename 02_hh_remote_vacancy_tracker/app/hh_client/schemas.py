from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class HHSalary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    from_: int | None = Field(default=None, alias="from")
    to: int | None = None
    currency: str | None = None
    gross: bool | None = None

    def humanize(self) -> str | None:
        if self.from_ is None and self.to is None:
            return None
        left = f"от {self.from_}" if self.from_ is not None else ""
        right = f"до {self.to}" if self.to is not None else ""
        amount = " ".join(part for part in (left, right) if part)
        return f"{amount} {self.currency or ''}".strip()


class HHNamedObject(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    name: str


class HHSnippet(BaseModel):
    model_config = ConfigDict(extra="ignore")

    requirement: str | None = None
    responsibility: str | None = None


class HHVacancyItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    alternate_url: HttpUrl
    employer: HHNamedObject
    area: HHNamedObject | None = None
    salary: HHSalary | None = None
    schedule: HHNamedObject | None = None
    snippet: HHSnippet | None = None
    published_at: datetime | None = None

    @property
    def searchable_text(self) -> str:
        snippet = self.snippet or HHSnippet()
        return " ".join(
            item
            for item in (
                self.name,
                self.employer.name,
                self.schedule.name if self.schedule else "",
                snippet.requirement or "",
                snippet.responsibility or "",
            )
            if item
        )


class HHVacancyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    items: list[HHVacancyItem]
    found: int
    pages: int
    page: int
    per_page: int
