from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable

from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig


class FilterEngine:
    def __init__(self, today_provider: Callable[[], date] | None = None):
        self._today_provider = today_provider or date.today

    def should_keep(
        self,
        item: dict[str, Any],
        *,
        config: FilterConfig,
        gather_type: int,
    ) -> bool:
        if gather_type == 1:
            return True

        title = str(item.get("title", "N/A"))
        if any(word and word in title for word in config.excluded_words):
            return False

        browse_count = self._to_int(item.get("browseCnt"), default=0)
        want_count = self._to_int(item.get("wantCnt"), default=0)
        create_day = max(1, self._days_since(item.get("create_date")))
        consultation_rate = round(want_count / browse_count, 2) if browse_count else 0.0
        item_avg_reply = round(want_count / create_day, 2) if create_day else 0.0
        sold_price = self._to_float(item.get("soldPrice"), default=0.0)
        knife_price = self._to_optional_float(item.get("knife_price"))

        if browse_count < config.browse_min:
            return False
        if want_count < config.want_min:
            return False
        if item_avg_reply < config.daily_item_min:
            return False
        if consultation_rate < (config.consultation_rate_min_percent / 100):
            return False
        if not self._match_publish_days(create_day, config):
            return False
        if not self._match_range(sold_price, config.price_min, config.price_max):
            return False
        if not self._match_optional_range(knife_price, config.knife_price_min, config.knife_price_max):
            return False
        return True

    def _days_since(self, value: Any) -> int:
        if not value:
            return 1

        text = str(value).strip()
        for parser in (datetime.fromisoformat, lambda raw: datetime.strptime(raw, "%Y-%m-%d")):
            try:
                parsed = parser(text)
                if isinstance(parsed, datetime):
                    return (self._today_provider() - parsed.date()).days
            except ValueError:
                continue
        return 1

    @staticmethod
    def _match_publish_days(create_day: int, config: FilterConfig) -> bool:
        if config.publish_days_value is None:
            return True
        if config.publish_days_operator == "小于":
            return create_day <= config.publish_days_value
        if config.publish_days_operator == "大于":
            return create_day >= config.publish_days_value
        return True

    @staticmethod
    def _match_range(value: float, start: float | None, end: float | None) -> bool:
        if start is not None and value < start:
            return False
        if end is not None and value > end:
            return False
        return True

    @staticmethod
    def _match_optional_range(value: float | None, start: float | None, end: float | None) -> bool:
        if start is None and end is None:
            return True
        if value is None:
            return False
        return FilterEngine._match_range(value, start, end)

    @staticmethod
    def _to_int(value: Any, *, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _to_float(value: Any, *, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _to_optional_float(value: Any) -> float | None:
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
