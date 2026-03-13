import re
import time
from collections.abc import Iterable
from collections.abc import Callable

from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService
from minitap.mobile_use.scenarios.xianyu_publish.models import TapTarget, XianyuScreenAnalysis
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings

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
            text in loading_noise or text.isdigit() or ":" in text
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

    def open_home(self, serial: str) -> None:
        device = self._android.get_device(serial)
        device.shell(
            "am start -n "
            f"{self._settings.xianyu_package_name}/{self._settings.xianyu_main_activity}"
        )

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
                continue

            if analysis.screen_name == "publish_chooser":
                target = analysis.targets.get("publish_idle_item")
                if target is None:
                    raise RuntimeError("Missing publish option target on Xianyu chooser screen")
                self._tap_target(serial, target, "publish_idle_item")
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
        confirm_target = post_select.targets.get("album_confirm")
        if confirm_target is None:
            return post_select

        self._tap_target(serial, confirm_target, "album_confirm")
        return self._wait_for_post_confirm_screen(serial)

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
