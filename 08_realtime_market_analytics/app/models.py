from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TickRow(Base):
    __tablename__ = "ticks"
    __table_args__ = (UniqueConstraint("symbol", "trade_id", name="uq_tick_symbol_trade"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[float] = mapped_column(Float)
    trade_id: Mapped[str] = mapped_column(String(128), index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CandleRow(Base):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint("symbol", "window_seconds", "bucket_start", name="uq_candle_bucket"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    window_seconds: Mapped[int] = mapped_column(Integer, index=True)
    bucket_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    trades: Mapped[int] = mapped_column(Integer)


class AlertRow(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    rule: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(String(500))
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
