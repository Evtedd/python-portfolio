from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Tick:
    symbol: str
    price: float
    quantity: float
    trade_id: str
    event_time: datetime


@dataclass
class Candle:
    symbol: str
    window_seconds: int
    bucket_start: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades: int = 1

    def apply(self, tick: Tick) -> None:
        self.high = max(self.high, tick.price)
        self.low = min(self.low, tick.price)
        self.close = tick.price
        self.volume += tick.quantity
        self.trades += 1
