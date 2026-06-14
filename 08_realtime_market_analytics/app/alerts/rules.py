from dataclasses import dataclass

from app.domain import Tick


@dataclass(frozen=True)
class Alert:
    symbol: str
    rule: str
    message: str


@dataclass(frozen=True)
class PriceRule:
    symbol: str
    operator: str
    threshold: float

    def check(self, tick: Tick) -> Alert | None:
        if tick.symbol != self.symbol:
            return None
        if self.operator == "price_gt" and tick.price > self.threshold:
            return Alert(tick.symbol, self.label, f"{tick.symbol} price is above {self.threshold}")
        if self.operator == "price_lt" and tick.price < self.threshold:
            return Alert(tick.symbol, self.label, f"{tick.symbol} price is below {self.threshold}")
        return None

    @property
    def label(self) -> str:
        return f"{self.symbol}:{self.operator}:{self.threshold:g}"


def parse_price_rules(raw_rules: list[str]) -> list[PriceRule]:
    rules: list[PriceRule] = []
    for raw_rule in raw_rules:
        symbol, operator, threshold = raw_rule.split(":", 2)
        rules.append(PriceRule(symbol=symbol.upper(), operator=operator, threshold=float(threshold)))
    return rules


class AlertEngine:
    def __init__(self, rules: list[PriceRule]) -> None:
        self.rules = rules
        self.seen: set[str] = set()

    def check(self, tick: Tick) -> list[Alert]:
        alerts: list[Alert] = []
        for rule in self.rules:
            alert = rule.check(tick)
            if alert is None or alert.rule in self.seen:
                continue
            self.seen.add(alert.rule)
            alerts.append(alert)
        return alerts
