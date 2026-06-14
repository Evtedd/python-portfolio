from datetime import datetime, timezone

from app.domain import Tick


def normalize_binance_trade(message: dict) -> Tick:
    symbol = str(message.get("s") or message.get("symbol") or "").upper()
    price = float(message.get("p") or message.get("price"))
    quantity = float(message.get("q") or message.get("quantity") or 0)
    trade_id = str(message.get("t") or message.get("trade_id"))
    raw_time = message.get("T") or message.get("E")
    event_time = datetime.fromtimestamp(float(raw_time) / 1000, tz=timezone.utc)
    if not symbol or not trade_id:
        raise ValueError("Trade message has no symbol or trade id")
    return Tick(
        symbol=symbol,
        price=price,
        quantity=quantity,
        trade_id=trade_id,
        event_time=event_time,
    )
