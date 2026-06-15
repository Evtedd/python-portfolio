from app.config import Settings
from app.connectors.base import Connector
from app.connectors.http import HttpConnector, TelegramConnector
from app.connectors.memory import DbLogConnector, EmailConnector, MemoryConnector


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, Connector] = {}

    def register(self, connector: Connector) -> None:
        self._connectors[connector.name] = connector

    def get(self, name: str) -> Connector:
        if name not in self._connectors:
            raise KeyError(f"Connector is not registered: {name}")
        return self._connectors[name]

    def names(self) -> list[str]:
        return sorted(self._connectors)


def build_default_registry(settings: Settings) -> ConnectorRegistry:
    registry = ConnectorRegistry()
    registry.register(MemoryConnector())
    registry.register(DbLogConnector())
    registry.register(EmailConnector())
    if not settings.fake_mode:
        registry.register(HttpConnector())
        registry.register(TelegramConnector())
    else:
        registry.register(HttpConnector())
    return registry
