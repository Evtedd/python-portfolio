from datetime import datetime, timezone

from app.domain import Tick
from app.processing.aggregator import CandleAggregator


def test_candle_aggregation_and_deduplication():
    aggregator = CandleAggregator([60])
    first = Tick("BTCUSDT", 10.0, 1.0, "1", datetime(2026, 1, 1, tzinfo=timezone.utc))
    second = Tick("BTCUSDT", 12.0, 2.0, "2", datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc))

    aggregator.update(first)
    candles = aggregator.update(second)
    duplicate = aggregator.update(second)

    candle = candles[0]
    assert candle.open == 10.0
    assert candle.high == 12.0
    assert candle.close == 12.0
    assert candle.volume == 3.0
    assert duplicate == []
