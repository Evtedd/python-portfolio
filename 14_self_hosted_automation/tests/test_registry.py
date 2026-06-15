from app.config import Settings
from app.connectors.registry import build_default_registry


def test_registry_contains_fake_connectors() -> None:
    registry = build_default_registry(Settings(fake_mode=True))

    assert "memory" in registry.names()
    assert "db_log" in registry.names()
