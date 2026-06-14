import json
from collections.abc import AsyncIterator

import websockets

from app.config import settings
from app.domain import Tick
from app.processing.normalizer import normalize_binance_trade


async def binance_ticks(symbols: list[str]) -> AsyncIterator[Tick]:
    streams = "/".join(f"{symbol.lower()}@trade" for symbol in symbols)
    url = f"{settings.exchange_ws_url}/{streams}"
    async for websocket in websockets.connect(url, ping_interval=20):
        try:
            async for raw_message in websocket:
                message = json.loads(raw_message)
                data = message.get("data", message)
                yield normalize_binance_trade(data)
        except websockets.ConnectionClosed:
            continue
