import re
import time
from collections.abc import Iterable
from collections.abc import Callable
from decimal import Decimal
from decimal import InvalidOperation

from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService
from minitap.mobile_use.scenarios.xianyu_publish.models import TapTarget, XianyuScreenAnalysis
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings

_BOUNDS_RE = re.compile(r"\[(?P<left>\d+),(?P<top>\d+)\]\[(?P<right>\d+),(?P<bottom>\d+)\]")
_METADATA_CHOICE_RE = re.compile(r"^(?P<state>已选中|可选)(?P<label>.+), (?P=label)$")


def _extract_text(element: dict) -> str | None:
    for key in ("text", "content-desc", "accessibilityText"):
        value = element.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def parse_android_bounds(bounds: str | dict | None) -> TapTarget | None:
    if isinstance(bounds, str):
        match = _BOUNDS_RE.fullmatch(bounds)
        if match is None:
            return None
        left = int(match.group("left"))
        top = int(match.group("top"))
        right = int(match.group("right"))
        bottom = int(match.group("bottom"))
        return TapTarget(
            x=(left + right) // 2,
            y=(top + bottom) // 2,
            bounds=bounds,
        )

    if isinstance(bounds, dict):
        try:
            x = int(bounds["x"])
            y = int(bounds["y"])
            width = int(bounds["width"])
            height = int(bounds["height"])
        except (KeyError, TypeError, ValueError):
            return None
        return TapTarget(
            x=x + width // 2,
            y=y + height // 2,
            bounds=str(bounds),
        )

    return None


def normalize_price_input(price: str | float | int) -> str:
    raw = str(price).strip()
    if not raw:
        raise ValueError("Price input cannot be empty")

    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid price input: {price!r}") from exc

    if value < 0:
        raise ValueError("Price input cannot be negative")

    normalized = format(value, "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def normalize_shipping_method(method: str) -> str:
    raw = str(method).strip()
    if not raw:
        raise ValueError("Shipping method cannot be empty")

    aliases = {
        "包邮": "包邮",
        "邮寄包邮": "包邮",
        "不包邮-按距离付费": "不包邮-按距离付费",
        "不包邮-固定邮费": "不包邮-固定邮费",
        "无需邮寄": "无需邮寄",
    }
    normalized = aliases.get(raw)
    if normalized is None:
        raise ValueError(f"Unsupported shipping method: {method!r}")
    return normalized


def extract_listing_shipping_value(target: TapTarget | None) -> str | None:
    if target is None or not target.text:
        return None
    lines = [line.strip() for line in target.text.splitlines() if line.strip()]
    if len(lines) >= 2 and lines[0] == "发货方式":
        return lines[1]
    return None


def normalize_item_condition(condition: str) -> str:
    raw = str(condition).strip()
    if not raw:
        raise ValueError("Item condition cannot be empty")

    aliases = {
        "全新": "全新",
        "几乎全新": "几乎全新",
        "轻微使用痕迹": "轻微使用痕迹",
        "明显使用痕迹": "明显使用痕迹",
    }
    normalized = aliases.get(raw)
    if normalized is None:
        raise ValueError(f"Unsupported item condition: {condition!r}")
    return normalized


def normalize_item_category(category: str) -> str:
    raw = str(category).strip()
    if not raw:
        raise ValueError("Item category cannot be empty")
    return raw


def normalize_item_source(source: str) -> str:
    raw = str(source).strip()
    if not raw:
        raise ValueError("Item source cannot be empty")

    aliases = {
        "盒机转赠": "盒机转赠",
        "盒机直发": "盒机直发",
        "淘宝转卖": "淘宝转卖",
        "闲置": "闲置",
    }
    normalized = aliases.get(raw)
    if normalized is None:
        raise ValueError(f"Unsupported item source: {source!r}")
    return normalized


def _normalize_target_suffix(text: str) -> str:
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text.strip())
    return normalized.strip("_")


class XianyuFlowAnalyzer:
    def __init__(self, settings: XianyuPublishSettings | None = None) -> None:
        self._settings = settings or XianyuPublishSettings()

    def _visible_texts(self, elements: Iterable[dict]) -> list[str]:
        visible_texts: list[str] = []
        for element in elements:
            text = _extract_text(element)
            if text is not None and text not in visible_texts:
                visible_texts.append(text)
        return visible_texts

    def _find_target(
        self,
        elements: Iterable[dict],
        *,
        exact_text: str | None = None,
        contains_text: str | None = None,
    ) -> TapTarget | None:
        for element in elements:
            text = _extract_text(element)
            if text is None:
                continue
            if exact_text is not None and text != exact_text:
                continue
            if contains_text is not None and contains_text not in text:
                continue
            target = parse_android_bounds(element.get("bounds"))
            if target is None:
                continue
            return target.model_copy(update={"text": text})
        return None

    def _find_multiline_option_target(
        self,
        elements: Iterable[dict],
        *,
        header_text: str,
        option_text: str,
    ) -> TapTarget | None:
        for element in elements:
            text = _extract_text(element)
            bounds = element.get("bounds")
            if text is None or not isinstance(bounds, str):
                continue
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if header_text not in lines or option_text not in lines:
                continue
            match = _BOUNDS_RE.fullmatch(bounds)
            if match is None:
                continue
            left = int(match.group("left"))
            top = int(match.group("top"))
            right = int(match.group("right"))
            bottom = int(match.group("bottom"))
            row_height = (bottom - top) / len(lines)
            line_index = lines.index(option_text)
            return TapTarget(
                x=(left + right) // 2,
                y=int(top + ((line_index + 0.5) * row_height)),
                bounds=bounds,
                text=option_text,
            )
        return None

    def _find_shipping_mail_option_targets(self, elements: Iterable[dict]) -> dict[str, TapTarget]:
        multiline_target = self._find_target(elements, contains_text="包邮")
        if multiline_target is None or multiline_target.text is None:
            return {}

        lines = [line.strip() for line in multiline_target.text.splitlines() if line.strip()]
        if not lines or lines[0] != "邮寄":
            return {}

        option_labels = [line for line in lines[1:] if line.strip()]
        if not option_labels:
            return {}

        icon_targets: list[TapTarget] = []
        for element in elements:
            element_class = element.get("class") or element.get("className")
            if element_class != "android.widget.ImageView":
                continue
            target = parse_android_bounds(element.get("bounds"))
            if target is None or target.x > 200:
                continue
            if target.y < multiline_target.y - 200 or target.y > multiline_target.y + 500:
                continue
            icon_targets.append(target)

        if len(icon_targets) < len(option_labels):
            return {}

        icon_targets.sort(key=lambda target: target.y)
        target_names = {
            "包邮": "shipping_option_mail_free",
            "不包邮-按距离付费": "shipping_option_mail_distance",
            "不包邮-固定邮费": "shipping_option_mail_fixed",
            "无需邮寄": "shipping_option_no_mail",
        }
        option_targets: dict[str, TapTarget] = {}
        for label, icon_target in zip(option_labels, icon_targets, strict=False):
            target_name = target_names.get(label)
            if target_name is None:
                continue
            option_targets[target_name] = icon_target.model_copy(update={"text": label})
        return option_targets

    def _find_location_region_option_targets(
        self,
        elements: Iterable[dict],
    ) -> dict[str, TapTarget]:
        excluded_labels = {"返回", "所在地", "获取当前位置", "当前定位"}
        option_targets: dict[str, TapTarget] = {}
        for element in elements:
            text = _extract_text(element)
            if text is None or text in excluded_labels:
                continue
            target = parse_android_bounds(element.get("bounds"))
            if target is None or target.y < 300:
                continue
            suffix = _normalize_target_suffix(text)
            if not suffix:
                continue
            option_targets[f"location_region_option_{suffix}"] = target.model_copy(
                update={"text": text}
            )
        return option_targets

    def _find_metadata_choice_targets(
        self,
        elements: Iterable[dict],
        *,
        prefix: str,
        options: Iterable[str],
    ) -> dict[str, TapTarget]:
        targets: dict[str, TapTarget] = {}
        for option in options:
            selected = self._find_target(elements, exact_text=f"已选中{option}, {option}")
            available = self._find_target(elements, exact_text=f"可选{option}, {option}")
            resolved = selected or available
            if resolved is None:
                continue
            suffix = _normalize_target_suffix(option)
            targets[f"{prefix}_option_{suffix}"] = resolved.model_copy(update={"text": option})
            if selected is not None:
                targets[f"{prefix}_selected_{suffix}"] = selected.model_copy(
                    update={"text": option}
                )
        return targets

    def _find_metadata_category_targets(self, elements: Iterable[dict]) -> dict[str, TapTarget]:
        category_header = self._find_target(elements, exact_text="分类, 分类")
        if category_header is None:
            return {}

        next_section_y_candidates: list[int] = []
        for header_text in ("盒袋状态, 盒袋状态", "盒卡状态, 盒卡状态", "成色, 成色"):
            header_target = self._find_target(elements, exact_text=header_text)
            if header_target is not None and header_target.y >= category_header.y:
                next_section_y_candidates.append(header_target.y)
        lower_y_bound = min(next_section_y_candidates) if next_section_y_candidates else 10_000

        targets: dict[str, TapTarget] = {}
        for element in elements:
            text = _extract_text(element)
            if text is None:
                continue
            match = _METADATA_CHOICE_RE.fullmatch(text)
            if match is None:
                continue
            target = parse_android_bounds(element.get("bounds"))
            if target is None:
                continue
            if target.x <= 200:
                continue
            if target.y < category_header.y - 120 or target.y >= lower_y_bound:
                continue

            label = match.group("label")
            suffix = _normalize_target_suffix(label)
            if not suffix:
                continue

            targets[f"metadata_category_option_{suffix}"] = target.model_copy(
                update={"text": label}
            )
            if match.group("state") == "已选中":
                targets[f"metadata_category_selected_{suffix}"] = target.model_copy(
                    update={"text": label}
                )
        return targets

    def detect_screen(self, screen_data: dict) -> XianyuScreenAnalysis:
        current_app = screen_data.get("current_app", {})
        current_package = current_app.get("package")
        current_activity = current_app.get("activity")
        elements = screen_data.get("elements", [])
        visible_texts = self._visible_texts(elements)
        targets: dict[str, TapTarget] = {}
        preferred_album_menu_label = f"{self._settings.preferred_album_name}·"

        permission_allow = self._find_target(
            elements, exact_text=self._settings.permission_allow_text
        )
        if (
            current_package == "com.android.permissioncontroller"
            and any("是否允许" in text for text in visible_texts)
            and permission_allow is not None
        ):
            targets["permission_allow"] = permission_allow
            return XianyuScreenAnalysis(
                screen_name="media_permission_dialog",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        publish_entry = self._find_target(elements, exact_text=self._settings.publish_entry_text)
        if (
            current_package == self._settings.xianyu_package_name
            and publish_entry is not None
            and any(text == "闲鱼" for text in visible_texts)
        ):
            targets["publish_entry"] = publish_entry
            return XianyuScreenAnalysis(
                screen_name="home",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        draft_resume_continue = self._find_target(elements, exact_text="继续")
        draft_resume_discard = self._find_target(elements, exact_text="放弃")
        if (
            current_package == self._settings.xianyu_package_name
            and draft_resume_continue is not None
            and any("未编辑完成的宝贝" in text for text in visible_texts)
        ):
            targets["draft_resume_continue"] = draft_resume_continue
            if draft_resume_discard is not None:
                targets["draft_resume_discard"] = draft_resume_discard
            return XianyuScreenAnalysis(
                screen_name="draft_resume_dialog",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        submit_listing = self._find_target(elements, exact_text="发布") or self._find_target(
            elements, contains_text="发布"
        )
        add_image = self._find_target(elements, exact_text="添加图片")
        description_entry = self._find_target(elements, contains_text="描述")
        metadata_entry = self._find_target(elements, contains_text="分类/")
        price_entry = self._find_target(elements, exact_text="价格设置")
        shipping_entry = self._find_target(elements, contains_text="发货方式")
        location_entry = self._find_target(elements, exact_text="选择位置")
        description_done = self._find_target(elements, exact_text="完成")
        metadata_category_targets = self._find_metadata_category_targets(elements)
        metadata_condition_targets = self._find_metadata_choice_targets(
            elements,
            prefix="metadata_condition",
            options=("全新", "几乎全新", "轻微使用痕迹", "明显使用痕迹"),
        )
        metadata_source_targets = self._find_metadata_choice_targets(
            elements,
            prefix="metadata_source",
            options=("盒机转赠", "盒机直发", "淘宝转卖", "闲置"),
        )
        if (
            current_package == self._settings.xianyu_package_name
            and any(text == "发闲置" for text in visible_texts)
            and description_entry is not None
            and description_done is not None
        ):
            targets["description_entry"] = description_entry
            targets["description_done"] = description_done
            if submit_listing is not None:
                targets["submit_listing"] = submit_listing
            if add_image is not None:
                targets["add_image"] = add_image
            return XianyuScreenAnalysis(
                screen_name="description_editor",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        price_confirm = self._find_target(elements, exact_text="确定")
        price_delete = self._find_target(elements, exact_text="删除")
        if (
            current_package == self._settings.xianyu_package_name
            and price_confirm is not None
            and price_delete is not None
            and any("价格设置" in text for text in visible_texts)
            and any("原价设置" in text for text in visible_texts)
            and any("库存设置" in text for text in visible_texts)
        ):
            targets["price_confirm"] = price_confirm
            targets["price_delete"] = price_delete
            for digit in "0123456789":
                digit_target = self._find_target(elements, exact_text=digit)
                if digit_target is not None:
                    targets[f"price_key_{digit}"] = digit_target
            decimal_target = self._find_target(elements, exact_text=".")
            if decimal_target is not None:
                targets["price_key_decimal"] = decimal_target
            return XianyuScreenAnalysis(
                screen_name="price_panel",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        shipping_confirm = self._find_target(elements, exact_text="确定")
        shipping_mail_targets = self._find_shipping_mail_option_targets(elements)
        if (
            current_package == self._settings.xianyu_package_name
            and shipping_confirm is not None
            and shipping_mail_targets
            and any(text == "发货方式" for text in visible_texts)
        ):
            targets["shipping_confirm"] = shipping_confirm
            targets.update(shipping_mail_targets)
            return XianyuScreenAnalysis(
                screen_name="shipping_panel",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        location_back = self._find_target(elements, exact_text="返回")
        location_search = self._find_target(elements, exact_text="搜索地址")
        location_region_entry = self._find_target(elements, exact_text="请选择宝贝所在地")
        if (
            current_package == self._settings.xianyu_package_name
            and location_back is not None
            and location_search is not None
            and location_region_entry is not None
            and any(text == "宝贝所在地" for text in visible_texts)
            and any(text == "常用地址" for text in visible_texts)
        ):
            targets["location_back"] = location_back
            targets["location_search"] = location_search
            targets["location_region_entry"] = location_region_entry
            return XianyuScreenAnalysis(
                screen_name="location_panel",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        location_region_back = self._find_target(elements, exact_text="返回")
        location_region_get_current = self._find_target(elements, exact_text="获取当前位置")
        if (
            current_package == self._settings.xianyu_package_name
            and location_region_back is not None
            and location_region_get_current is not None
            and any(text == "所在地" for text in visible_texts)
            and not any(text == "宝贝所在地" for text in visible_texts)
        ):
            targets["location_region_back"] = location_region_back
            targets["location_region_get_current"] = location_region_get_current
            targets.update(self._find_location_region_option_targets(elements))
            return XianyuScreenAnalysis(
                screen_name="location_region_picker",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        if (
            current_package == self._settings.xianyu_package_name
            and any(text == "发闲置" for text in visible_texts)
            and metadata_entry is not None
            and (metadata_category_targets or metadata_condition_targets or metadata_source_targets)
        ):
            if submit_listing is not None:
                targets["submit_listing"] = submit_listing
            if add_image is not None:
                targets["add_image"] = add_image
            if description_entry is not None:
                targets["description_entry"] = description_entry
            targets["metadata_entry"] = metadata_entry
            targets.update(metadata_category_targets)
            targets.update(metadata_condition_targets)
            targets.update(metadata_source_targets)
            if price_entry is not None:
                targets["price_entry"] = price_entry
            if shipping_entry is not None:
                targets["shipping_entry"] = shipping_entry
            if location_entry is not None:
                targets["location_entry"] = location_entry
            return XianyuScreenAnalysis(
                screen_name="metadata_panel",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        if (
            current_package == self._settings.xianyu_package_name
            and any(text == "发闲置" for text in visible_texts)
            and add_image is not None
            and any("价格设置" in text for text in visible_texts)
            and any("发货方式" in text for text in visible_texts)
        ):
            if submit_listing is not None:
                targets["submit_listing"] = submit_listing
            targets["add_image"] = add_image
            if description_entry is not None:
                targets["description_entry"] = description_entry
            if metadata_entry is not None:
                targets["metadata_entry"] = metadata_entry
            if price_entry is not None:
                targets["price_entry"] = price_entry
            if shipping_entry is not None:
                targets["shipping_entry"] = shipping_entry
            if location_entry is not None:
                targets["location_entry"] = location_entry
            return XianyuScreenAnalysis(
                screen_name="listing_form",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        publish_idle_item = self._find_target(
            elements, contains_text=self._settings.publish_option_text
        )
        if (
            current_package == self._settings.xianyu_package_name
            and publish_idle_item is not None
            and any(text == "关闭" for text in visible_texts)
        ):
            targets["publish_idle_item"] = publish_idle_item
            return XianyuScreenAnalysis(
                screen_name="publish_chooser",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        album_source = self._find_target(
            elements, exact_text=self._settings.album_source_label_text
        )
        preferred_album_source = self._find_target(
            elements, contains_text=preferred_album_menu_label
        )
        if (
            current_package == self._settings.xianyu_package_name
            and album_source is not None
            and preferred_album_source is not None
        ):
            targets["album_source"] = album_source
            targets["preferred_album_source"] = preferred_album_source
            return XianyuScreenAnalysis(
                screen_name="album_source_menu",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        album_select = self._find_target(elements, exact_text=self._settings.album_select_text)
        album_confirm = self._find_target(elements, exact_text=self._settings.album_confirm_text)
        selected_album_source = self._find_target(
            elements, exact_text=self._settings.preferred_album_name
        ) or album_source
        if (
            current_package == self._settings.xianyu_package_name
            and (album_select is not None or album_confirm is not None)
            and any(
                text in {
                    self._settings.album_source_label_text,
                    "相册",
                    self._settings.preferred_album_name,
                }
                for text in visible_texts
            )
        ):
            if selected_album_source is not None:
                targets["album_source"] = selected_album_source
            if album_select is not None:
                targets["album_select"] = album_select
            if album_confirm is not None:
                targets["album_confirm"] = album_confirm
            return XianyuScreenAnalysis(
                screen_name="album_picker",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        media_preview_next_step = self._find_target(elements, contains_text="下一步")
        if (
            current_package == self._settings.xianyu_package_name
            and media_preview_next_step is not None
            and any("取消选择" in text for text in visible_texts)
            and any("删除图片" in text for text in visible_texts)
        ):
            targets["media_preview_next_step"] = media_preview_next_step
            return XianyuScreenAnalysis(
                screen_name="selected_media_preview",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        media_edit_done = self._find_target(elements, exact_text="完成")
        if (
            current_package == self._settings.xianyu_package_name
            and media_edit_done is not None
            and any(text == "裁剪" for text in visible_texts)
            and any(text == "背景模糊" for text in visible_texts)
            and any("点击添加标签" in text for text in visible_texts)
        ):
            targets["media_edit_done"] = media_edit_done
            return XianyuScreenAnalysis(
                screen_name="media_edit_screen",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        if (
            current_package == self._settings.xianyu_package_name
            and any("宝贝价格是根据市场行情计算得出" in text for text in visible_texts)
            and any(text == "添加" for text in visible_texts)
            and (
                any("删除" in text for text in visible_texts)
                or any(text.endswith("张照片") for text in visible_texts)
                or any("价格计算中" in text for text in visible_texts)
            )
        ):
            space_items_tab = self._find_target(elements, exact_text="宝贝")
            if space_items_tab is not None:
                targets["space_items_tab"] = space_items_tab
            return XianyuScreenAnalysis(
                screen_name="photo_analysis",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        if (
            current_package == self._settings.xianyu_package_name
            and any("这里空空如也" in text for text in visible_texts)
            and any("发宝贝" in text for text in visible_texts)
        ):
            return XianyuScreenAnalysis(
                screen_name="space_items_empty",
                current_package=current_package,
                current_activity=current_activity,
                visible_texts=visible_texts,
                targets=targets,
            )

        return XianyuScreenAnalysis(
            screen_name="unknown",
            current_package=current_package,
            current_activity=current_activity,
            visible_texts=visible_texts,
            targets=targets,
        )


class XianyuPublishFlowService:
    def __init__(
        self,
        settings: XianyuPublishSettings | None = None,
        android_service: AndroidDebugService | None = None,
        analyzer: XianyuFlowAnalyzer | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self._settings = settings or XianyuPublishSettings()
        self._android = android_service or AndroidDebugService()
        self._analyzer = analyzer or XianyuFlowAnalyzer(settings=self._settings)
        self._sleep = sleep_fn or time.sleep

    def _analyze(self, serial: str) -> XianyuScreenAnalysis:
        return self._analyzer.detect_screen(self._android.get_screen_data(serial))

    def _looks_like_loading_overlay(self, analysis: XianyuScreenAnalysis) -> bool:
        if analysis.screen_name != "unknown":
            return False
        if analysis.current_package != self._settings.xianyu_package_name:
            return False
        if not analysis.visible_texts:
            return True
        loading_noise = {
            "开启护眼模式",
            "勿扰",
            "振铃器静音。",
            "WLAN 信号强度满格。",
        }
        return all(
            text in loading_noise
            or text.isdigit()
            or ":" in text
            or text.startswith("正在充电")
            for text in analysis.visible_texts
        )

    def _tap_target(self, serial: str, target: TapTarget, target_name: str) -> None:
        if target is None:
            raise RuntimeError(f"Missing tap target for {target_name}")
        self._android.tap(serial, target.x, target.y)

    def _tap_ratio(self, serial: str, x_ratio: float, y_ratio: float) -> None:
        screen = self._android.get_screen_data(serial)
        width = int(screen["width"])
        height = int(screen["height"])
        self._android.tap(serial, int(width * x_ratio), int(height * y_ratio))

    def _wait_for_non_loading_screen(
        self,
        serial: str,
        *,
        max_polls: int = 6,
    ) -> XianyuScreenAnalysis:
        analysis = self._analyze(serial)
        for _ in range(max_polls):
            if not self._looks_like_loading_overlay(analysis):
                return analysis
            self._sleep(1.0)
            analysis = self._analyze(serial)
        return analysis

    def _wait_for_post_confirm_screen(
        self,
        serial: str,
        *,
        max_polls: int = 6,
    ) -> XianyuScreenAnalysis:
        analysis = self._analyze(serial)
        for _ in range(max_polls):
            if self._looks_like_loading_overlay(analysis) or analysis.screen_name == "album_picker":
                self._sleep(1.0)
                analysis = self._analyze(serial)
                continue
            return analysis

        if analysis.screen_name == "album_picker":
            raise RuntimeError(
                f"Post-confirm flow did not leave album picker within {max_polls} polls"
            )
        return analysis

    def _wait_for_post_shipping_confirm_screen(
        self,
        serial: str,
        *,
        max_polls: int = 6,
    ) -> XianyuScreenAnalysis:
        analysis = self._analyze(serial)
        for _ in range(max_polls):
            if (
                self._looks_like_loading_overlay(analysis)
                or analysis.screen_name == "shipping_panel"
            ):
                self._sleep(1.0)
                analysis = self._analyze(serial)
                continue
            return analysis

        if analysis.screen_name == "shipping_panel":
            raise RuntimeError(
                f"Shipping confirm flow did not leave shipping panel within {max_polls} polls"
            )
        return analysis

    def _wait_for_post_draft_resume_screen(
        self,
        serial: str,
        *,
        max_polls: int = 6,
    ) -> XianyuScreenAnalysis:
        analysis = self._analyze(serial)
        for _ in range(max_polls):
            if (
                self._looks_like_loading_overlay(analysis)
                or analysis.screen_name == "draft_resume_dialog"
            ):
                self._sleep(1.0)
                analysis = self._analyze(serial)
                continue
            return analysis

        if analysis.screen_name == "draft_resume_dialog":
            raise RuntimeError(
                "Draft resume flow did not leave draft_resume_dialog within "
                f"{max_polls} polls"
            )
        return analysis

    def _wait_for_screen_transition(
        self,
        serial: str,
        *,
        transient_screen_names: set[str],
        max_polls: int = 6,
    ) -> XianyuScreenAnalysis:
        analysis = self._analyze(serial)
        for _ in range(max_polls):
            if (
                self._looks_like_loading_overlay(analysis)
                or analysis.screen_name in transient_screen_names
            ):
                self._sleep(1.0)
                analysis = self._analyze(serial)
                continue
            return analysis
        return analysis

    def open_home(self, serial: str) -> None:
        device = self._android.get_device(serial)
        device.shell(
            "am start -n "
            f"{self._settings.xianyu_package_name}/{self._settings.xianyu_main_activity}"
        )

    def ensure_portrait(self, serial: str) -> None:
        device = self._android.get_device(serial)
        device.shell("settings put system accelerometer_rotation 0")
        device.shell("settings put system user_rotation 0")

    def advance_to_album_picker(
        self,
        serial: str,
        max_steps: int = 6,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "album_picker":
                return analysis

            if (
                analysis.current_package != self._settings.xianyu_package_name
                and analysis.screen_name != "media_permission_dialog"
            ):
                self.open_home(serial)
                continue

            if analysis.screen_name == "home":
                target = analysis.targets.get("publish_entry")
                if target is None:
                    raise RuntimeError("Missing publish entry target on Xianyu home screen")
                self._tap_target(serial, target, "publish_entry")
                analysis = self._wait_for_screen_transition(
                    serial,
                    transient_screen_names={"home"},
                )
                if analysis.screen_name == "listing_form":
                    return analysis
                continue

            if analysis.screen_name == "publish_chooser":
                target = analysis.targets.get("publish_idle_item")
                if target is None:
                    raise RuntimeError("Missing publish option target on Xianyu chooser screen")
                self._tap_target(serial, target, "publish_idle_item")
                analysis = self._wait_for_screen_transition(
                    serial,
                    transient_screen_names={"publish_chooser"},
                )
                if analysis.screen_name == "listing_form":
                    return analysis
                continue

            if analysis.screen_name == "media_permission_dialog":
                target = analysis.targets.get("permission_allow")
                if target is None:
                    raise RuntimeError("Missing allow button target on media permission dialog")
                self._tap_target(serial, target, "permission_allow")
                continue

            self.open_home(serial)

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "album_picker":
            return final_analysis
        raise RuntimeError(
            f"Failed to reach album picker within {max_steps} steps: {final_analysis.screen_name}"
        )

    def switch_album_source(
        self,
        serial: str,
        preferred_album_name: str | None = None,
    ) -> XianyuScreenAnalysis:
        target_album_name = preferred_album_name or self._settings.preferred_album_name
        analysis = self._analyze(serial)
        if analysis.screen_name != "album_picker":
            raise RuntimeError(
                f"Cannot switch album source from screen: {analysis.screen_name}"
            )

        current_source = analysis.targets.get("album_source")
        if current_source is not None and current_source.text == target_album_name:
            return analysis

        source_target = analysis.targets.get("album_source")
        if source_target is None:
            raise RuntimeError("Missing current album source target on album picker")
        self._tap_target(serial, source_target, "album_source")

        source_menu = self._analyze(serial)
        if source_menu.screen_name != "album_source_menu":
            raise RuntimeError(
                "Expected album source menu after tapping source label, "
                f"got {source_menu.screen_name}"
            )

        preferred_source = source_menu.targets.get("preferred_album_source")
        if preferred_source is None:
            raise RuntimeError(f"Missing preferred album source target for {target_album_name}")
        self._tap_target(serial, preferred_source, "preferred_album_source")

        updated_picker = self._analyze(serial)
        if updated_picker.screen_name != "album_picker":
            raise RuntimeError(
                f"Expected album picker after switching source, got {updated_picker.screen_name}"
            )
        return updated_picker

    def select_cover_image(
        self,
        serial: str,
        preferred_album_name: str | None = None,
    ) -> XianyuScreenAnalysis:
        analysis = self._analyze(serial)
        if analysis.screen_name != "album_picker":
            raise RuntimeError(
                f"Cannot select album media from screen: {analysis.screen_name}"
            )

        if preferred_album_name is not None:
            analysis = self.switch_album_source(serial, preferred_album_name=preferred_album_name)

        select_target = analysis.targets.get("album_select")
        if select_target is None:
            raise RuntimeError("Missing selectable media target on album picker")
        self._tap_target(serial, select_target, "album_select")

        post_select = self._wait_for_non_loading_screen(serial)
        if post_select.screen_name == "selected_media_preview":
            next_step_target = post_select.targets.get("media_preview_next_step")
            if next_step_target is None:
                raise RuntimeError("Missing media_preview_next_step target on preview screen")
            self._tap_target(serial, next_step_target, "media_preview_next_step")
            post_next_step = self._wait_for_non_loading_screen(serial)
            if post_next_step.screen_name == "media_edit_screen":
                done_target = post_next_step.targets.get("media_edit_done")
                if done_target is None:
                    raise RuntimeError("Missing media_edit_done target on media edit screen")
                self._tap_target(serial, done_target, "media_edit_done")
                return self._wait_for_non_loading_screen(serial)
            return post_next_step

        confirm_target = post_select.targets.get("album_confirm")
        if confirm_target is None:
            return post_select

        self._tap_target(serial, confirm_target, "album_confirm")
        post_confirm = self._wait_for_post_confirm_screen(serial)
        if post_confirm.screen_name == "selected_media_preview":
            next_step_target = post_confirm.targets.get("media_preview_next_step")
            if next_step_target is None:
                raise RuntimeError("Missing media_preview_next_step target on preview screen")
            self._tap_target(serial, next_step_target, "media_preview_next_step")
            post_next_step = self._wait_for_non_loading_screen(serial)
            if post_next_step.screen_name == "media_edit_screen":
                done_target = post_next_step.targets.get("media_edit_done")
                if done_target is None:
                    raise RuntimeError("Missing media_edit_done target on media edit screen")
                self._tap_target(serial, done_target, "media_edit_done")
                return self._wait_for_non_loading_screen(serial)
            return post_next_step
        return post_confirm

    def advance_photo_analysis_to_publish_chooser(
        self,
        serial: str,
    ) -> XianyuScreenAnalysis:
        analysis = self._analyze(serial)
        if analysis.screen_name == "publish_chooser":
            return analysis

        if (
            analysis.current_package == self._settings.xianyu_package_name
            and analysis.screen_name in {"photo_analysis", "unknown"}
        ):
            self._tap_ratio(
                serial,
                self._settings.space_overlay_dismiss_x_ratio,
                self._settings.space_overlay_dismiss_y_ratio,
            )
            analysis = self._analyze(serial)
            if analysis.screen_name != "photo_analysis":
                raise RuntimeError(
                    "Expected photo_analysis after dismissing space overlay, "
                    f"got {analysis.screen_name}"
                )

            space_items_tab = analysis.targets.get("space_items_tab")
            if space_items_tab is None:
                raise RuntimeError("Missing 宝贝 tab target on photo_analysis screen")
            self._tap_target(serial, space_items_tab, "space_items_tab")
            analysis = self._analyze(serial)

        if analysis.screen_name == "space_items_empty":
            self._tap_ratio(
                serial,
                self._settings.space_publish_button_x_ratio,
                self._settings.space_publish_button_y_ratio,
            )
            analysis = self._analyze(serial)

        if analysis.screen_name != "publish_chooser":
            raise RuntimeError(
                "Failed to reach publish chooser from photo_analysis: "
                f"{analysis.screen_name}"
            )
        return analysis

    def advance_to_listing_form(
        self,
        serial: str,
        max_steps: int = 6,
    ) -> XianyuScreenAnalysis:
        self.ensure_portrait(serial)

        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "listing_form":
                return analysis

            if analysis.current_package != self._settings.xianyu_package_name:
                self.open_home(serial)
                continue

            if analysis.screen_name == "home":
                target = analysis.targets.get("publish_entry")
                if target is None:
                    raise RuntimeError("Missing publish entry target on Xianyu home screen")
                self._tap_target(serial, target, "publish_entry")
                analysis = self._wait_for_screen_transition(
                    serial,
                    transient_screen_names={"home"},
                )
                if analysis.screen_name == "listing_form":
                    return analysis
                continue

            if analysis.screen_name == "publish_chooser":
                target = analysis.targets.get("publish_idle_item")
                if target is None:
                    raise RuntimeError("Missing publish option target on Xianyu chooser screen")
                self._tap_target(serial, target, "publish_idle_item")
                analysis = self._wait_for_screen_transition(
                    serial,
                    transient_screen_names={"publish_chooser"},
                )
                if analysis.screen_name == "listing_form":
                    return analysis
                continue

            if analysis.screen_name == "draft_resume_dialog":
                target = analysis.targets.get("draft_resume_continue")
                if target is None:
                    raise RuntimeError("Missing continue target on draft resume dialog")
                self._tap_target(serial, target, "draft_resume_continue")
                analysis = self._wait_for_post_draft_resume_screen(serial)
                if analysis.screen_name == "listing_form":
                    return analysis
                continue

            self.open_home(serial)

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "listing_form":
            return final_analysis
        raise RuntimeError(
            f"Failed to reach listing form within {max_steps} steps: {final_analysis.screen_name}"
        )

    def advance_listing_form_to_album_picker(
        self,
        serial: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "album_picker":
                return analysis

            if analysis.screen_name == "listing_form":
                target = analysis.targets.get("add_image")
                if target is None:
                    raise RuntimeError("Missing add_image target on listing form")
                self._tap_target(serial, target, "add_image")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name == "album_picker":
                    return analysis
                if analysis.screen_name == "media_permission_dialog":
                    continue
                if analysis.screen_name == "unknown":
                    continue
                continue

            if analysis.screen_name == "media_permission_dialog":
                target = analysis.targets.get("permission_allow")
                if target is None:
                    raise RuntimeError("Missing allow button target on media permission dialog")
                self._tap_target(serial, target, "permission_allow")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name == "album_picker":
                    return analysis
                if analysis.screen_name == "unknown":
                    continue
                continue

            raise RuntimeError(
                "Cannot reach album picker from current screen: "
                f"{analysis.screen_name}"
            )

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "album_picker":
            return final_analysis
        raise RuntimeError(
            "Failed to reach album picker from listing form within "
            f"{max_steps} steps: {final_analysis.screen_name}"
        )

    def advance_listing_form_to_location_panel(
        self,
        serial: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "location_panel":
                return analysis

            if analysis.screen_name in {"listing_form", "metadata_panel"}:
                target = analysis.targets.get("location_entry")
                if target is None:
                    raise RuntimeError(
                        f"Missing location_entry target on {analysis.screen_name}"
                    )
                self._tap_target(serial, target, "location_entry")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name in {"location_panel", "unknown"}:
                    continue

            raise RuntimeError(
                "Cannot reach location panel from current screen: "
                f"{analysis.screen_name}"
            )

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "location_panel":
            return final_analysis
        raise RuntimeError(
            "Failed to reach location panel within "
            f"{max_steps} steps: {final_analysis.screen_name}"
        )

    def advance_listing_form_to_location_region_picker(
        self,
        serial: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "location_region_picker":
                return analysis

            if analysis.screen_name == "listing_form":
                analysis = self.advance_listing_form_to_location_panel(
                    serial,
                    max_steps=max_steps,
                )

            if analysis.screen_name == "location_panel":
                target = analysis.targets.get("location_region_entry")
                if target is None:
                    raise RuntimeError("Missing location_region_entry target on location panel")
                self._tap_target(serial, target, "location_region_entry")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name in {"location_region_picker", "unknown"}:
                    continue

            raise RuntimeError(
                "Cannot reach location region picker from current screen: "
                f"{analysis.screen_name}"
            )

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "location_region_picker":
            return final_analysis
        raise RuntimeError(
            "Failed to reach location region picker within "
            f"{max_steps} steps: {final_analysis.screen_name}"
        )

    def advance_listing_form_to_metadata_panel(
        self,
        serial: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "metadata_panel":
                return analysis

            if analysis.screen_name == "listing_form":
                target = analysis.targets.get("metadata_entry")
                if target is None:
                    raise RuntimeError("Missing metadata_entry target on listing form")
                self._tap_target(serial, target, "metadata_entry")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name in {"metadata_panel", "unknown"}:
                    continue

            raise RuntimeError(
                "Cannot reach metadata panel from current screen: "
                f"{analysis.screen_name}"
            )

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "metadata_panel":
            return final_analysis
        raise RuntimeError(
            "Failed to reach metadata panel within "
            f"{max_steps} steps: {final_analysis.screen_name}"
        )

    def advance_listing_form_to_description_editor(
        self,
        serial: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "description_editor":
                return analysis

            if analysis.screen_name == "listing_form":
                target = analysis.targets.get("description_entry")
                if target is None:
                    raise RuntimeError("Missing description_entry target on listing form")
                self._tap_target(serial, target, "description_entry")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name in {"description_editor", "unknown"}:
                    continue

            raise RuntimeError(
                "Cannot reach description editor from current screen: "
                f"{analysis.screen_name}"
            )

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "description_editor":
            return final_analysis
        raise RuntimeError(
            "Failed to reach description editor within "
            f"{max_steps} steps: {final_analysis.screen_name}"
        )

    def _set_metadata_choice(
        self,
        serial: str,
        *,
        desired_value: str,
        target_prefix: str,
        option_kind: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        current_analysis = self._analyze(serial)
        suffix = _normalize_target_suffix(desired_value)
        selected_target_name = f"{target_prefix}_selected_{suffix}"
        option_target_name = f"{target_prefix}_option_{suffix}"
        if (
            current_analysis.screen_name == "metadata_panel"
            and current_analysis.targets.get(selected_target_name) is not None
        ):
            return current_analysis

        analysis = current_analysis
        if analysis.screen_name != "metadata_panel":
            analysis = self.advance_listing_form_to_metadata_panel(serial, max_steps=max_steps)

        if analysis.targets.get(selected_target_name) is not None:
            return analysis

        option_target = analysis.targets.get(option_target_name)
        if option_target is None:
            raise RuntimeError(f"Missing {option_target_name} target on metadata panel")
        self._tap_target(serial, option_target, option_target_name)

        final_analysis = self._wait_for_non_loading_screen(serial)
        if final_analysis.screen_name != "metadata_panel":
            raise RuntimeError(
                f"{option_kind} flow did not remain on metadata panel: "
                f"{final_analysis.screen_name}"
            )
        if final_analysis.targets.get(selected_target_name) is None:
            raise RuntimeError(
                f"{option_kind} flow did not end on selected value {desired_value!r}"
            )
        return final_analysis

    def advance_listing_form_to_price_panel(
        self,
        serial: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "price_panel":
                return analysis

            if analysis.screen_name in {"listing_form", "metadata_panel"}:
                target = analysis.targets.get("price_entry")
                if target is None:
                    raise RuntimeError(f"Missing price_entry target on {analysis.screen_name}")
                self._tap_target(serial, target, "price_entry")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name in {"price_panel", "unknown"}:
                    continue

            raise RuntimeError(
                "Cannot reach price panel from current screen: "
                f"{analysis.screen_name}"
            )

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "price_panel":
            return final_analysis
        raise RuntimeError(
            f"Failed to reach price panel within {max_steps} steps: {final_analysis.screen_name}"
        )

    def advance_listing_form_to_shipping_panel(
        self,
        serial: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        for _ in range(max_steps):
            analysis = self._analyze(serial)
            if analysis.screen_name == "shipping_panel":
                return analysis

            if analysis.screen_name in {"listing_form", "metadata_panel"}:
                target = analysis.targets.get("shipping_entry")
                if target is None:
                    raise RuntimeError(
                        f"Missing shipping_entry target on {analysis.screen_name}"
                    )
                self._tap_target(serial, target, "shipping_entry")
                analysis = self._wait_for_non_loading_screen(serial)
                if analysis.screen_name in {"shipping_panel", "unknown"}:
                    continue

            raise RuntimeError(
                "Cannot reach shipping panel from current screen: "
                f"{analysis.screen_name}"
            )

        final_analysis = self._analyze(serial)
        if final_analysis.screen_name == "shipping_panel":
            return final_analysis
        raise RuntimeError(
            f"Failed to reach shipping panel within {max_steps} steps: {final_analysis.screen_name}"
        )

    def fill_description(
        self,
        serial: str,
        description: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        analysis = self.advance_listing_form_to_description_editor(serial, max_steps=max_steps)
        self._android.input_text(serial, description)

        post_input = self._wait_for_non_loading_screen(serial)
        if post_input.screen_name == "listing_form":
            return post_input

        done_target = post_input.targets.get("description_done") or analysis.targets.get(
            "description_done"
        )
        if done_target is None:
            raise RuntimeError("Missing description_done target on description editor")
        self._tap_target(serial, done_target, "description_done")

        final_analysis = self._wait_for_non_loading_screen(serial)
        if final_analysis.screen_name != "listing_form":
            raise RuntimeError(
                "Description flow did not return to listing form: "
                f"{final_analysis.screen_name}"
            )
        return final_analysis

    def fill_price(
        self,
        serial: str,
        price: str | float | int,
        max_steps: int = 4,
        max_clear_presses: int = 8,
        key_delay_seconds: float = 0.2,
    ) -> XianyuScreenAnalysis:
        price_text = normalize_price_input(price)
        analysis = self.advance_listing_form_to_price_panel(serial, max_steps=max_steps)

        delete_target = analysis.targets.get("price_delete")
        if delete_target is None:
            raise RuntimeError("Missing price_delete target on price panel")
        for _ in range(max_clear_presses):
            self._tap_target(serial, delete_target, "price_delete")
            if key_delay_seconds > 0:
                self._sleep(key_delay_seconds)

        current_panel = self._analyze(serial)
        targets = (
            current_panel.targets
            if current_panel.screen_name == "price_panel"
            else analysis.targets
        )

        for char in price_text:
            target_name = "price_key_decimal" if char == "." else f"price_key_{char}"
            key_target = targets.get(target_name) or analysis.targets.get(target_name)
            if key_target is None:
                raise RuntimeError(f"Missing keypad target for price character: {char!r}")
            self._tap_target(serial, key_target, target_name)
            if key_delay_seconds > 0:
                self._sleep(key_delay_seconds)
            updated_panel = self._analyze(serial)
            if updated_panel.screen_name == "price_panel":
                targets = updated_panel.targets

        confirm_target = targets.get("price_confirm") or analysis.targets.get("price_confirm")
        if confirm_target is None:
            raise RuntimeError("Missing price_confirm target on price panel")
        self._tap_target(serial, confirm_target, "price_confirm")

        final_analysis = self._wait_for_non_loading_screen(serial)
        if final_analysis.screen_name != "listing_form":
            raise RuntimeError(
                "Price flow did not return to listing form: "
                f"{final_analysis.screen_name}"
            )
        return final_analysis

    def set_shipping_method(
        self,
        serial: str,
        method: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        desired_method = normalize_shipping_method(method)
        current_analysis = self._analyze(serial)
        if current_analysis.screen_name == "listing_form":
            current_method = extract_listing_shipping_value(
                current_analysis.targets.get("shipping_entry")
            )
            if current_method == desired_method:
                return current_analysis

        analysis = self.advance_listing_form_to_shipping_panel(serial, max_steps=max_steps)
        target_name = {
            "包邮": "shipping_option_mail_free",
            "不包邮-按距离付费": "shipping_option_mail_distance",
            "不包邮-固定邮费": "shipping_option_mail_fixed",
            "无需邮寄": "shipping_option_no_mail",
        }[desired_method]
        option_target = analysis.targets.get(target_name)
        if option_target is None:
            raise RuntimeError(f"Missing {target_name} target on shipping panel")
        self._tap_target(serial, option_target, target_name)

        updated_panel = self._wait_for_non_loading_screen(serial)
        if updated_panel.screen_name == "shipping_panel":
            analysis = updated_panel

        confirm_target = analysis.targets.get("shipping_confirm") or updated_panel.targets.get(
            "shipping_confirm"
        )
        if confirm_target is None:
            raise RuntimeError("Missing shipping_confirm target on shipping panel")
        self._tap_target(serial, confirm_target, "shipping_confirm")

        final_analysis = self._wait_for_post_shipping_confirm_screen(serial)
        if final_analysis.screen_name != "listing_form":
            raise RuntimeError(
                "Shipping flow did not return to listing form: "
                f"{final_analysis.screen_name}"
            )

        final_method = extract_listing_shipping_value(final_analysis.targets.get("shipping_entry"))
        if final_method != desired_method:
            raise RuntimeError(
                f"Shipping flow ended on {final_method!r} instead of {desired_method!r}"
            )
        return final_analysis

    def set_item_condition(
        self,
        serial: str,
        condition: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        desired_condition = normalize_item_condition(condition)
        return self._set_metadata_choice(
            serial,
            desired_value=desired_condition,
            target_prefix="metadata_condition",
            option_kind="Condition",
            max_steps=max_steps,
        )

    def set_item_category(
        self,
        serial: str,
        category: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        desired_category = normalize_item_category(category)
        return self._set_metadata_choice(
            serial,
            desired_value=desired_category,
            target_prefix="metadata_category",
            option_kind="Category",
            max_steps=max_steps,
        )

    def set_item_source(
        self,
        serial: str,
        source: str,
        max_steps: int = 4,
    ) -> XianyuScreenAnalysis:
        desired_source = normalize_item_source(source)
        return self._set_metadata_choice(
            serial,
            desired_value=desired_source,
            target_prefix="metadata_source",
            option_kind="Source",
            max_steps=max_steps,
        )
