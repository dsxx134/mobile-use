from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FilterConfig:
    excluded_words: list[str] = field(default_factory=list)
    browse_min: int = 0
    want_min: int = 0
    publish_days_operator: str = ""
    publish_days_value: int | None = None
    daily_item_min: float = -1.0
    consultation_rate_min_percent: int = -1
    price_min: float | None = None
    price_max: float | None = None
    knife_price_min: float | None = None
    knife_price_max: float | None = None
