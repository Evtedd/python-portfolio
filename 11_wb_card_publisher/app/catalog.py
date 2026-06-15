from app.wb_client import WBClient


class CatalogService:
    def __init__(self, wb_client: WBClient) -> None:
        self.wb_client = wb_client
        self._subject_characteristics: dict[int, list[dict]] = {}
        self._colors: set[str] | None = None
        self._countries: set[str] | None = None

    async def required_characteristics(self, subject_id: int) -> list[dict]:
        if subject_id not in self._subject_characteristics:
            data = await self.wb_client.subject_characteristics(subject_id)
            self._subject_characteristics[subject_id] = [row for row in data if row.get("required")]
        return self._subject_characteristics[subject_id]

    async def known_colors(self) -> set[str]:
        if self._colors is None:
            self._colors = {str(row.get("name", "")).lower() for row in await self.wb_client.colors()}
        return self._colors

    async def known_countries(self) -> set[str]:
        if self._countries is None:
            self._countries = {str(row.get("name", "")).lower() for row in await self.wb_client.countries()}
        return self._countries
