from app.parsing.vacancy import extract_hh_id


def test_extract_hh_id_from_url_and_plain_id():
    assert extract_hh_id("https://hh.ru/vacancy/123456") == "123456"
    assert extract_hh_id("98765") == "98765"
    assert extract_hh_id("https://example.com") is None
