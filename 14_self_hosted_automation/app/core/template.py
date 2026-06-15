import re
from typing import Any


TOKEN = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")


def render_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return TOKEN.sub(lambda match: str(resolve_path(context, match.group(1), "")), value)
    if isinstance(value, dict):
        return {key: render_value(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [render_value(item, context) for item in value]
    return value


def resolve_path(context: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = context
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current
