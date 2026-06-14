import httpx
import pytest

from app.hh_client.client import HHClient


pytestmark = pytest.mark.asyncio


async def test_search_page_parses_hh_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": "123",
                        "name": "Python backend developer",
                        "alternate_url": "https://hh.ru/vacancy/123",
                        "employer": {"name": "Acme"},
                        "schedule": {"name": "Удаленная работа"},
                        "salary": {"from": 100000, "currency": "RUR"},
                        "snippet": {"requirement": "FastAPI", "responsibility": "API"},
                    },
                ],
                "found": 1,
                "pages": 1,
                "page": 0,
                "per_page": 50,
            },
        )

    client = httpx.AsyncClient(
        base_url="https://api.hh.ru",
        transport=httpx.MockTransport(handler),
    )
    hh_client = HHClient(client)

    page = await hh_client.search_page(0)

    assert page.items[0].id == "123"
    assert page.items[0].salary.humanize() == "от 100000 RUR"
