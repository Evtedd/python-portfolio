import asyncio
import random
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from app.config import settings
from app.domain import Tick


async def simulated_ticks(symbols: list[str]) -> AsyncIterator[Tick]:
    prices = {symbol: 60000.0 if symbol.startswith("BTC") else 3000.0 for symbol in symbols}
    trade_id = 0
    while True:
        for symbol in symbols:
            trade_id += 1
            prices[symbol] = max(1.0, prices[symbol] + random.uniform(-25, 25))
            yield Tick(
                symbol=symbol,
                price=round(prices[symbol], 2),
                quantity=round(random.uniform(0.001, 0.1), 6),
                trade_id=f"sim_{trade_id}",
                event_time=datetime.now(timezone.utc),
            )
        await asyncio.sleep(settings.tick_interval_seconds)
