from datetime import datetime, timezone

from app.alerts.rules import AlertEngine, parse_price_rules
from app.domain import Tick


def test_price_alert_triggers_once():
    engine = AlertEngine(parse_price_rules(["BTCUSDT:price_gt:100"]))
    tick = Tick("BTCUSDT", 120.0, 1.0, "1", datetime.now(timezone.utc))

    assert len(engine.check(tick)) == 1
    assert engine.check(tick) == []
