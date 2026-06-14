from app.processing.normalizer import normalize_binance_trade


def test_normalize_binance_trade():
    tick = normalize_binance_trade(
        {"s": "btcusdt", "p": "65000.5", "q": "0.01", "t": 42, "T": 1710000000000},
    )

    assert tick.symbol == "BTCUSDT"
    assert tick.price == 65000.5
    assert tick.trade_id == "42"
