from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ParsedTask:
    text: str
    deadline_at: datetime | None
    category: str | None


def parse_task_message(raw_text: str) -> ParsedTask:
    parts = raw_text.strip().split()
    deadline_at: datetime | None = None
    category: str | None = None
    clean_parts: list[str] = []

    for part in parts:
        if part.startswith("#") and len(part) > 1:
            category = part[1:80]
            continue

        if part.startswith("due:"):
            deadline_at = parse_deadline(part.removeprefix("due:"))
            continue

        clean_parts.append(part)

    text = " ".join(clean_parts).strip()
    if not text:
        raise ValueError("Task text is empty")

    return ParsedTask(text=text, deadline_at=deadline_at, category=category)


def parse_deadline(value: str) -> datetime:
    formats = ("%Y-%m-%dT%H:%M", "%Y-%m-%d", "%Y.%m.%dT%H:%M", "%Y.%m.%d")
    for date_format in formats:
        try:
            parsed = datetime.strptime(value, date_format)
            if date_format in {"%Y-%m-%d", "%Y.%m.%d"}:
                parsed = parsed.replace(hour=23, minute=59)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    raise ValueError("Deadline format must be YYYY.MM.DD or YYYY.MM.DDTHH:MM")
