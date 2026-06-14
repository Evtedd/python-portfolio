import re


def extract_hh_id(value: str) -> str | None:
    value = value.strip()
    if value.isdigit():
        return value
    match = re.search(r"hh\.ru/vacancy/(\d+)", value)
    return match.group(1) if match else None
