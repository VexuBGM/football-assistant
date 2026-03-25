from dataclasses import dataclass
from typing import Any


@dataclass
class ParseResult:
    intent: str
    entities: dict[str, Any]
