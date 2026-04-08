from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


@dataclass(slots=True)
class CollectionSummary:
    discovered: int = 0
    duplicates: int = 0
    saved: int = 0
    filtered: int = 0
    errors: int = 0


class CollectorService:
    def __init__(
        self,
        *,
        api_client: Any,
        goods_repo: Any,
        item_normalizer: Any,
        filter_engine: Any,
        event_sink: Callable[[str, dict[str, Any]], None] | None = None,
    ):
        self.api_client = api_client
        self.goods_repo = goods_repo
        self.item_normalizer = item_normalizer
        self.filter_engine = filter_engine
        self.event_sink = event_sink

    def collect_keyword(
        self,
        *,
        keywords: list[str],
        pages: int,
        filter_config: FilterConfig,
        multi_spec_enabled: bool = False,
        proxy_config: ProxyConfig | None = None,
        per_keyword_success_limit: int | None = None,
    ) -> CollectionSummary:
        summary = CollectionSummary()
        known_item_ids = set(self.goods_repo.list_goods_item_ids())
        for keyword in keywords:
            saved_for_keyword = 0
            for page in range(1, pages + 1):
                item_ids = self.api_client.search_items(
                    page=page,
                    keyword=keyword,
                    proxy_config=proxy_config,
                )
                for item_id in item_ids:
                    summary.discovered += 1
                    saved = self._process_item(
                        item_id=item_id,
                        known_item_ids=known_item_ids,
                        filter_config=filter_config,
                        gather_type=0,
                        multi_spec_enabled=multi_spec_enabled,
                        proxy_config=proxy_config,
                        summary=summary,
                    )
                    if saved:
                        saved_for_keyword += 1
                        if (
                            per_keyword_success_limit is not None
                            and saved_for_keyword >= per_keyword_success_limit
                        ):
                            break
                if (
                    per_keyword_success_limit is not None
                    and saved_for_keyword >= per_keyword_success_limit
                ):
                    break
        return summary

    def collect_manual(
        self,
        *,
        urls: list[str],
        filter_config: FilterConfig,
        multi_spec_enabled: bool = False,
        proxy_config: ProxyConfig | None = None,
    ) -> CollectionSummary:
        summary = CollectionSummary()
        known_item_ids = set(self.goods_repo.list_goods_item_ids())
        for url in urls:
            item_id = self.api_client.get_item_id_from_url(url)
            if not item_id:
                summary.errors += 1
                self._emit("item_id_parse_failed", {"url": url})
                continue
            summary.discovered += 1
            self._process_item(
                item_id=item_id,
                known_item_ids=known_item_ids,
                filter_config=filter_config,
                gather_type=1,
                multi_spec_enabled=multi_spec_enabled,
                proxy_config=proxy_config,
                summary=summary,
            )
        return summary

    def collect_shop(
        self,
        *,
        shop_urls: list[str],
        pages: int,
        filter_config: FilterConfig,
        multi_spec_enabled: bool = False,
        proxy_config: ProxyConfig | None = None,
        recent_publish_filter: str | None = None,
    ) -> CollectionSummary:
        summary = CollectionSummary()
        known_item_ids = set(self.goods_repo.list_goods_item_ids())
        for shop_url in shop_urls:
            user_id = self.api_client.get_user_id_from_url(shop_url, proxy_config=proxy_config)
            if not user_id:
                summary.errors += 1
                self._emit("user_id_parse_failed", {"url": shop_url})
                continue
            for page in range(1, pages + 1):
                cards = self.api_client.get_shop_items(
                    page=page,
                    user_id=user_id,
                    proxy_config=proxy_config,
                )
                for item_id in self._extract_item_ids_from_cards(
                    cards, recent_publish_filter=recent_publish_filter
                ):
                    summary.discovered += 1
                    self._process_item(
                        item_id=item_id,
                        known_item_ids=known_item_ids,
                        filter_config=filter_config,
                        gather_type=0,
                        multi_spec_enabled=multi_spec_enabled,
                        proxy_config=proxy_config,
                        summary=summary,
                    )
        return summary

    def _process_item(
        self,
        *,
        item_id: str,
        known_item_ids: set[str],
        filter_config: FilterConfig,
        gather_type: int,
        multi_spec_enabled: bool,
        proxy_config: ProxyConfig | None,
        summary: CollectionSummary,
    ) -> bool:
        if item_id in known_item_ids:
            summary.duplicates += 1
            self._emit("item_skipped_duplicate", {"item_id": item_id})
            return False

        detail_payload = self.api_client.get_item_detail(item_id, proxy_config=proxy_config)
        normalized = self.item_normalizer.normalize_detail(
            item_id=item_id,
            detail_payload=detail_payload,
        )

        if multi_spec_enabled and normalized.get("maxPrice"):
            specification_payload = self.api_client.get_item_specification(
                item_id,
                proxy_config=proxy_config,
            )
            normalized = self.item_normalizer.normalize_detail(
                item_id=item_id,
                detail_payload=detail_payload,
                specification_payload=specification_payload,
            )

        should_keep = self.filter_engine.should_keep(
            normalized,
            config=filter_config,
            gather_type=gather_type,
        )
        if not should_keep:
            summary.filtered += 1
            self._emit("item_filtered_out", {"item_id": item_id})
            return False

        self.goods_repo.insert_good(normalized)
        known_item_ids.add(item_id)
        summary.saved += 1
        self._emit("item_saved", {"item_id": item_id})
        return True

    def _extract_item_ids_from_cards(
        self,
        cards: list[dict[str, Any]],
        *,
        recent_publish_filter: str | None = None,
    ) -> list[str]:
        item_ids: list[str] = []
        for card in cards:
            if not self._card_matches_recent_publish_filter(card, recent_publish_filter):
                continue
            found = self._find_item_id(card)
            if found:
                item_ids.append(found)
        return item_ids

    def _card_matches_recent_publish_filter(
        self,
        card: dict[str, Any],
        recent_publish_filter: str | None,
    ) -> bool:
        if not recent_publish_filter:
            return True
        labels = (
            card.get("cardData", {})
            .get("itemLabelDataVO", {})
            .get("serviceUtParams")
        )
        if not labels:
            return False
        if recent_publish_filter == "24小时内发布":
            return "24小时内发布" in labels
        if recent_publish_filter == "72小时内发布":
            return "24小时内发布" in labels or "72小时内发布" in labels
        if recent_publish_filter == "一周内发布":
            return any(label in labels for label in ("24小时内发布", "72小时内发布", "一周内发布"))
        return recent_publish_filter in labels

    def _find_item_id(self, node: Any) -> str | None:
        if isinstance(node, dict):
            if node.get("itemId"):
                return str(node["itemId"])
            for value in node.values():
                found = self._find_item_id(value)
                if found:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = self._find_item_id(value)
                if found:
                    return found
        return None

    def _emit(self, event_name: str, payload: dict[str, Any]) -> None:
        if self.event_sink is not None:
            self.event_sink(event_name, payload)
