import asyncio
import json

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.bus.memory import EventBus
from app.config import settings
from app.db.base import Base
from app.db.session import engine, get_session
from app.schemas import CandleRead
from app.service import MarketService
from app.storage.repository import MarketRepository

app = FastAPI(title="Real time Market Analytics", version="1.0.0")
bus = EventBus(settings.queue_max_size)
stop_event = asyncio.Event()
market_task: asyncio.Task | None = None

app.mount("/dashboard", StaticFiles(directory="app/dashboard", html=True), name="dashboard")


@app.on_event("startup")
async def startup() -> None:
    global market_task
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    market_task = asyncio.create_task(MarketService(bus).run(stop_event))


@app.on_event("shutdown")
async def shutdown() -> None:
    stop_event.set()
    if market_task is not None:
        await market_task


@app.get("/symbols", response_model=list[str])
async def symbols() -> list[str]:
    return settings.symbols


@app.get("/candles/{symbol}", response_model=list[CandleRead])
async def candles(
    symbol: str,
    window_seconds: int = 60,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
) -> list[CandleRead]:
    return await MarketRepository(session).candles(symbol, window_seconds, limit)


@app.websocket("/ws/{symbol}")
async def websocket_updates(websocket: WebSocket, symbol: str) -> None:
    await websocket.accept()
    queue = bus.subscribe(symbol)
    try:
        while True:
            event = await queue.get()
            await websocket.send_text(json.dumps(event))
    except WebSocketDisconnect:
        bus.unsubscribe(symbol, queue)
