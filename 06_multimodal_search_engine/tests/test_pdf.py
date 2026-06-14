from app.ingestion.pdf import extract_pages_from_reader


class FakePage:
    def __init__(self, text: str | None) -> None:
        self.text = text

    def extract_text(self) -> str | None:
        return self.text


def test_extract_pages_keeps_page_numbers():
    pages = [FakePage("Intro"), FakePage(None), FakePage("PostgreSQL notes")]

    result = extract_pages_from_reader(pages)

    assert [(item.page, item.text) for item in result] == [
        (1, "Intro"),
        (3, "PostgreSQL notes"),
    ]
