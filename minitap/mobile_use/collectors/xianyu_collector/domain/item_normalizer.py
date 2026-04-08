from __future__ import annotations

from typing import Any


class ItemNormalizer:
    def normalize_detail(
        self,
        *,
        item_id: str,
        detail_payload: dict[str, Any],
        specification_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if "itemDO" not in detail_payload:
            normalized = dict(detail_payload)
            normalized.setdefault("item_id", item_id)
            normalized.setdefault("item_url", f"https://www.goofish.com/item?id={item_id}")
            normalized.setdefault("data_sources", "采集导入")
            if specification_payload is not None:
                normalized["specification"] = specification_payload
            return normalized

        item_do = detail_payload.get("itemDO", {})
        seller_do = detail_payload.get("sellerDO", {})
        good_name = self._extract_good_name(item_do)
        knife_price = self._extract_knife_price(item_do)
        item_images = self._extract_item_images(item_do)
        user_reg_day = seller_do.get("userRegDay")
        sold_num = seller_do.get("hasSoldNumInteger")
        avg_reply = self._compute_avg_reply(sold_num, user_reg_day)

        normalized = {
            "item_id": item_id,
            "item_url": f"https://www.goofish.com/item?id={item_id}",
            "item_images": item_images,
            "title": item_do.get("title"),
            "desc": item_do.get("desc"),
            "soldPrice": item_do.get("soldPrice"),
            "browseCnt": item_do.get("browseCnt"),
            "wantCnt": item_do.get("wantCnt"),
            "goodName": good_name,
            "create_date": item_do.get("GMT_CREATE_DATE_KEY"),
            "sellerId": seller_do.get("sellerId"),
            "nick": seller_do.get("nick"),
            "signature": seller_do.get("signature"),
            "avgReply30dLong": avg_reply,
            "knife_price": knife_price,
            "maxPrice": item_do.get("maxPrice"),
            "hasSoldNumInteger": sold_num,
            "userRegDay": user_reg_day,
            "data_sources": "采集导入",
        }
        if specification_payload is not None:
            normalized["specification"] = specification_payload
        return normalized

    @staticmethod
    def _extract_good_name(item_do: dict[str, Any]) -> str | None:
        labels = item_do.get("itemLabelExtList") or []
        if not labels:
            return None
        first = labels[0] or {}
        return first.get("text")

    @staticmethod
    def _extract_knife_price(item_do: dict[str, Any]) -> str:
        promotion = item_do.get("promotionPriceDO") or {}
        promotion_name = promotion.get("promotionName")
        if promotion_name and "小刀" in promotion_name:
            return promotion.get("promotionPriceMin", "")
        return ""

    @staticmethod
    def _extract_item_images(item_do: dict[str, Any]) -> str:
        result = ""
        for image in item_do.get("imageInfos", []):
            url = image.get("url")
            if url:
                result += f"{url}_790x10000Q90.jpg_.webp,"
        return result

    @staticmethod
    def _compute_avg_reply(has_sold_num: Any, user_reg_day: Any) -> float:
        try:
            return round(float(has_sold_num) / float(user_reg_day), 2)
        except (TypeError, ValueError, ZeroDivisionError):
            return 0.0
