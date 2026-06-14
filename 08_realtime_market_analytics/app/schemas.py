from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TickRead(BaseModel):
    symbol: str
    price: float
    quantity: float
    trade_id: str
    event_time: datetime


class CandleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    window_seconds: int
    bucket_start: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades: int


class AlertRead(BaseModel):
    symbol: str
    rule: str
    message: str
    event_time: datetime
