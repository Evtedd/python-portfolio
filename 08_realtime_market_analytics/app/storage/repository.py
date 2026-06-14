from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.rules import Alert
from app.domain import Candle, Tick
from app.models import AlertRow, CandleRow, TickRow


class MarketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_tick(self, tick: Tick) -> None:
        self.session.add(
            TickRow(
                symbol=tick.symbol,
                price=tick.price,
                quantity=tick.quantity,
                trade_id=tick.trade_id,
                event_time=tick.event_time,
            ),
        )
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()

    async def save_candle(self, candle: Candle) -> None:
        existing = await self.session.scalar(
            select(CandleRow).where(
                CandleRow.symbol == candle.symbol,
                CandleRow.window_seconds == candle.window_seconds,
                CandleRow.bucket_start == candle.bucket_start,
            ),
        )
        if existing is None:
            self.session.add(
                CandleRow(
                    symbol=candle.symbol,
                    window_seconds=candle.window_seconds,
                    bucket_start=candle.bucket_start,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                    trades=candle.trades,
                ),
            )
        else:
            existing.high = candle.high
            existing.low = candle.low
            existing.close = candle.close
            existing.volume = candle.volume
            existing.trades = candle.trades
        await self.session.commit()

    async def save_alert(self, alert: Alert, event_time: datetime) -> None:
        self.session.add(
            AlertRow(
                symbol=alert.symbol,
                rule=alert.rule,
                message=alert.message,
                event_time=event_time,
            ),
        )
        await self.session.commit()

    async def candles(
        self,
        symbol: str,
        window_seconds: int,
        limit: int,
    ) -> list[CandleRow]:
        result = await self.session.execute(
            select(CandleRow)
            .where(
                CandleRow.symbol == symbol.upper(),
                CandleRow.window_seconds == window_seconds,
            )
            .order_by(CandleRow.bucket_start.desc())
            .limit(limit),
        )
        return list(reversed(result.scalars().all()))
