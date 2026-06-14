import asyncio
import logging

from app.alerts.rules import AlertEngine, parse_price_rules
from app.bus.memory import EventBus
from app.config import settings
from app.db.session import SessionFactory
from app.domain import Candle, Tick
from app.ingest.binance import binance_ticks
from app.ingest.simulator import simulated_ticks
from app.processing.aggregator import CandleAggregator
from app.storage.repository import MarketRepository

logger = logging.getLogger(__name__)


class MarketService:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.aggregator = CandleAggregator(settings.windows)
        self.alerts = AlertEngine(parse_price_rules(settings.price_alerts))

    async def run(self, stop_event: asyncio.Event) -> None:
        source = simulated_ticks(settings.symbols) if settings.simulation_mode else binance_ticks(settings.symbols)
        async for tick in source:
            if stop_event.is_set():
                break
            await self.handle_tick(tick)

    async def handle_tick(self, tick: Tick) -> None:
        async with SessionFactory() as session:
            repository = MarketRepository(session)
            await repository.save_tick(tick)
            candles = self.aggregator.update(tick)
            for candle in candles:
                await repository.save_candle(candle)
                await self.bus.publish(tick.symbol, {"type": "candle", "data": candle_to_dict(candle)})

            await self.bus.publish(tick.symbol, {"type": "tick", "data": tick_to_dict(tick)})
            for alert in self.alerts.check(tick):
                await repository.save_alert(alert, tick.event_time)
                await self.bus.publish(
                    tick.symbol,
                    {
                        "type": "alert",
                        "data": {
                            "symbol": alert.symbol,
                            "rule": alert.rule,
                            "message": alert.message,
                            "event_time": tick.event_time.isoformat(),
                        },
                    },
                )


def tick_to_dict(tick: Tick) -> dict:
    return {
        "symbol": tick.symbol,
        "price": tick.price,
        "quantity": tick.quantity,
        "trade_id": tick.trade_id,
        "event_time": tick.event_time.isoformat(),
    }


def candle_to_dict(candle: Candle) -> dict:
    return {
        "symbol": candle.symbol,
        "window_seconds": candle.window_seconds,
        "bucket_start": candle.bucket_start.isoformat(),
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
        "trades": candle.trades,
    }
