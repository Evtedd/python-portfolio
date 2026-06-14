from datetime import datetime, timezone

from app.domain import Candle, Tick


class CandleAggregator:
    def __init__(self, windows: list[int]) -> None:
        self.windows = windows
        self.candles: dict[tuple[str, int, datetime], Candle] = {}
        self.last_trade_ids: set[tuple[str, str]] = set()

    def update(self, tick: Tick) -> list[Candle]:
        key = (tick.symbol, tick.trade_id)
        if key in self.last_trade_ids:
            return []
        self.last_trade_ids.add(key)

        updated: list[Candle] = []
        for window in self.windows:
            bucket = bucket_start(tick.event_time, window)
            candle_key = (tick.symbol, window, bucket)
            candle = self.candles.get(candle_key)
            if candle is None:
                candle = Candle(
                    symbol=tick.symbol,
                    window_seconds=window,
                    bucket_start=bucket,
                    open=tick.price,
                    high=tick.price,
                    low=tick.price,
                    close=tick.price,
                    volume=tick.quantity,
                )
                self.candles[candle_key] = candle
            else:
                candle.apply(tick)
            updated.append(candle)
        return updated


def bucket_start(value: datetime, window_seconds: int) -> datetime:
    timestamp = int(value.timestamp())
    bucket = timestamp - timestamp % window_seconds
    return datetime.fromtimestamp(bucket, tz=timezone.utc)
