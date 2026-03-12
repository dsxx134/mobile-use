import re
from collections.abc import Iterable

from minitap.mobile_use.scenarios.xianyu_publish.models import TapTarget, XianyuScreenAnalysis

_BOUNDS_RE = re.compile(r"\[(?P<left>\d+),(?P<top>\d+)\]\[(?P<right>\d+),(?P<bottom>\d+)\]")


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


class XianyuFlowAnalyzer:
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

    def detect_screen(self, screen_data: dict) -> XianyuScreenAnalysis:
        current_app = screen_data.get("current_app", {})
        current_package = current_app.get("package")
        current_activity = current_app.get("activity")
        elements = screen_data.get("elements", [])
        visible_texts = self._visible_texts(elements)
        targets: dict[str, TapTarget] = {}

        permission_allow = self._find_target(elements, exact_text="允许")
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

        publish_entry = self._find_target(elements, exact_text="卖闲置")
        if (
            current_package == "com.taobao.idlefish"
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

        publish_idle_item = self._find_target(elements, contains_text="发闲置")
        if (
            current_package == "com.taobao.idlefish"
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

        album_select = self._find_target(elements, exact_text="选择")
        album_confirm = self._find_target(elements, exact_text="确定")
        if (
            current_package == "com.taobao.idlefish"
            and album_select is not None
            and any(text in {"所有文件", "相册"} for text in visible_texts)
        ):
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

        return XianyuScreenAnalysis(
            screen_name="unknown",
            current_package=current_package,
            current_activity=current_activity,
            visible_texts=visible_texts,
            targets=targets,
        )
