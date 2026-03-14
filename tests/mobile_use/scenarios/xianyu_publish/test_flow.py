from unittest.mock import Mock
from unittest.mock import call

import pytest

from minitap.mobile_use.scenarios.xianyu_publish.flow import (
    XianyuFlowAnalyzer,
    XianyuPublishFlowService,
)
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def _make_screen(
    *,
    package: str = "com.taobao.idlefish",
    activity: str = "com.taobao.idlefish.maincontainer.activity.MainActivity",
    elements: list[dict],
) -> dict:
    return {
        "serial": "device-1",
        "platform": "android",
        "current_app": {
            "serial": "device-1",
            "package": package,
            "activity": activity,
            "raw_output": f"{package}/{activity}",
        },
        "width": 2560,
        "height": 1600,
        "base64": "abc123",
        "hierarchy_xml": "<hierarchy />",
        "elements": elements,
        "element_count": len(elements),
    }


class FakeAndroidService:
    def __init__(
        self,
        screens: list[dict],
        advance_on_get_indices: set[int] | None = None,
        advance_on_input_indices: set[int] | None = None,
        advance_on_focused_text_indices: set[int] | None = None,
        advance_on_set_text_by_description_indices: set[int] | None = None,
        advance_on_tap_calls: set[int] | None = None,
        advance_on_swipe_calls: set[int] | None = None,
    ):
        self._screens = screens
        self._index = 0
        self._advance_on_get_indices = advance_on_get_indices or set()
        self._advance_on_input_indices = advance_on_input_indices or set()
        self._advance_on_focused_text_indices = advance_on_focused_text_indices or set()
        self._advance_on_set_text_by_description_indices = (
            advance_on_set_text_by_description_indices or set()
        )
        self._advance_on_tap_calls = advance_on_tap_calls
        self._advance_on_swipe_calls = advance_on_swipe_calls or set()
        self.device = Mock()
        self.tap_calls: list[tuple[str, int, int]] = []
        self.swipe_calls: list[tuple[str, int, int, int, int, int]] = []
        self.back_calls: list[str] = []
        self.long_press_calls: list[tuple[str, int, int]] = []
        self.input_text_calls: list[tuple[str, str]] = []
        self.set_clipboard_text_calls: list[tuple[str, str]] = []
        self.set_focused_text_calls: list[tuple[str, str]] = []
        self.set_text_by_description_calls: list[tuple[str, str, str]] = []
        self.set_text_on_description_child_calls: list[tuple[str, str, str]] = []
        self._tap_count = 0
        self._swipe_count = 0

    def get_current_app(self, serial: str) -> dict:
        return self._screens[self._index]["current_app"]

    def get_screen_data(self, serial: str) -> dict:
        screen = self._screens[self._index]
        if self._index in self._advance_on_get_indices and self._index < len(self._screens) - 1:
            self._index += 1
        return screen

    def tap(
        self,
        serial: str,
        x: int,
        y: int,
        long_press: bool = False,
        long_press_duration_ms: int = 1000,
    ) -> dict:
        self.tap_calls.append((serial, x, y))
        if long_press:
            self.long_press_calls.append((serial, x, y))
        self._tap_count += 1
        should_advance = (
            self._index < len(self._screens) - 1
            and (
                self._advance_on_tap_calls is None
                or self._tap_count in self._advance_on_tap_calls
            )
        )
        if should_advance:
            self._index += 1
        return {
            "serial": serial,
            "x": x,
            "y": y,
            "success": True,
            "long_press": long_press,
            "long_press_duration_ms": long_press_duration_ms,
        }

    def get_device(self, serial: str) -> Mock:
        return self.device

    def press_back(self, serial: str) -> dict:
        self.back_calls.append(serial)
        if self._index < len(self._screens) - 1:
            self._index += 1
        return {"serial": serial, "success": True}

    def swipe(
        self,
        serial: str,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 400,
    ) -> dict:
        self.swipe_calls.append((serial, start_x, start_y, end_x, end_y, duration_ms))
        self._swipe_count += 1
        if (
            self._swipe_count in self._advance_on_swipe_calls
            and self._index < len(self._screens) - 1
        ):
            self._index += 1
        return {
            "serial": serial,
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "duration_ms": duration_ms,
            "success": True,
        }

    def input_text(self, serial: str, text: str) -> dict:
        self.input_text_calls.append((serial, text))
        if self._index in self._advance_on_input_indices and self._index < len(self._screens) - 1:
            self._index += 1
        return {"serial": serial, "text": text, "success": True}

    def set_clipboard_text(self, serial: str, text: str) -> dict:
        self.set_clipboard_text_calls.append((serial, text))
        return {"serial": serial, "text": text, "success": True}

    def set_focused_text(self, serial: str, text: str) -> dict:
        self.set_focused_text_calls.append((serial, text))
        if (
            self._index in self._advance_on_focused_text_indices
            and self._index < len(self._screens) - 1
        ):
            self._index += 1
        return {"serial": serial, "text": text, "success": True}

    def set_text_by_description(self, serial: str, description: str, text: str) -> dict:
        self.set_text_by_description_calls.append((serial, description, text))
        if (
            self._index in self._advance_on_set_text_by_description_indices
            and self._index < len(self._screens) - 1
        ):
            self._index += 1
        return {
            "serial": serial,
            "description": description,
            "text": text,
            "success": True,
        }

    def set_text_on_description_child(self, serial: str, description: str, text: str) -> dict:
        self.set_text_on_description_child_calls.append((serial, description, text))
        if (
            self._index in self._advance_on_set_text_by_description_indices
            and self._index < len(self._screens) - 1
        ):
            self._index += 1
        return {
            "serial": serial,
            "description": description,
            "text": text,
            "success": True,
        }


def _metadata_panel_elements(
    *,
    selected_category: str | None = None,
    selected_condition: str | None = None,
    selected_source: str | None = None,
) -> list[dict]:
    category_blind_box = (
        "已选中潮玩盲盒, 潮玩盲盒"
        if selected_category == "潮玩盲盒"
        else "可选潮玩盲盒, 潮玩盲盒"
    )
    category_novel = (
        "已选中文学/小说, 文学/小说"
        if selected_category == "文学/小说"
        else "可选文学/小说, 文学/小说"
    )
    category_game = (
        "已选中游戏装备, 游戏装备"
        if selected_category == "游戏装备"
        else "可选游戏装备, 游戏装备"
    )
    category_home = (
        "已选中家居摆件, 家居摆件"
        if selected_category == "家居摆件"
        else "可选家居摆件, 家居摆件"
    )
    category_other = (
        "已选中其他游戏道具, 其他游戏道具"
        if selected_category == "其他游戏道具"
        else "可选其他游戏道具, 其他游戏道具"
    )
    category_life = (
        "已选中生活百科, 生活百科"
        if selected_category == "生活百科"
        else "可选生活百科, 生活百科"
    )
    condition_full_new = "已选中全新, 全新" if selected_condition == "全新" else "可选全新, 全新"
    condition_almost_new = (
        "已选中几乎全新, 几乎全新"
        if selected_condition == "几乎全新"
        else "可选几乎全新, 几乎全新"
    )
    source_idle = "已选中闲置, 闲置" if selected_source == "闲置" else "可选闲置, 闲置"
    source_taobao = (
        "已选中淘宝转卖, 淘宝转卖"
        if selected_source == "淘宝转卖"
        else "可选淘宝转卖, 淘宝转卖"
    )
    return [
        {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
        {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
        {"content-desc": "存草稿", "bounds": "[1265,115][1410,155]"},
        {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]", "clickable": "true"},
        {"content-desc": "删除图片", "bounds": "[70,250][550,730]", "clickable": "true"},
        {"content-desc": "添加图片", "bounds": "[560,250][1040,730]", "clickable": "true"},
        {
            "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
            "bounds": "[30,737][1570,1264]",
            "clickable": "true",
        },
        {
            "content-desc": "AI帮你写, AI帮你写",
            "bounds": "[1280,1264][1560,1380]",
            "clickable": "true",
        },
        {
            "content-desc": "分类/盒袋状态/盒卡状态/等\n款式",
            "bounds": "[0,1494][1600,2515]",
            "clickable": "true",
        },
        {"content-desc": "分类, 分类", "bounds": "[40,1665][215,1705]"},
        {
            "content-desc": category_blind_box,
            "bounds": "[245,1615][435,1755]",
            "clickable": "true",
        },
        {"content-desc": category_novel, "bounds": "[455,1615][660,1755]", "clickable": "true"},
        {"content-desc": category_game, "bounds": "[680,1615][870,1755]", "clickable": "true"},
        {"content-desc": category_home, "bounds": "[890,1615][1080,1755]", "clickable": "true"},
        {
            "content-desc": category_other,
            "bounds": "[1100,1615][1355,1755]",
            "clickable": "true",
        },
        {"content-desc": category_life, "bounds": "[1375,1615][1565,1755]", "clickable": "true"},
        {"content-desc": "成色, 成色", "bounds": "[40,1945][215,1985]"},
        {"content-desc": condition_full_new, "bounds": "[245,2035][375,2175]", "clickable": "true"},
        {
            "content-desc": condition_almost_new,
            "bounds": "[395,2035][585,2175]",
            "clickable": "true",
        },
        {"content-desc": "商品来源, 商品来源", "bounds": "[40,2175][215,2215]"},
        {"content-desc": source_taobao, "bounds": "[665,2175][855,2315]", "clickable": "true"},
        {"content-desc": source_idle, "bounds": "[875,2175][1005,2315]", "clickable": "true"},
        {"content-desc": "请选择款式", "bounds": "[245,2315][513,2455]", "clickable": "true"},
    ]


def _scrolled_metadata_panel_elements(*, selected_category: str | None = None) -> list[dict]:
    category_novel = (
        "已选中文学/小说, 文学/小说"
        if selected_category == "文学/小说"
        else "可选文学/小说, 文学/小说"
    )
    return [
        {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
        {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
        {"content-desc": "存草稿", "bounds": "[1265,115][1410,155]"},
        {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]", "clickable": "true"},
        {"content-desc": "AI生成仅供参考，查看须知", "bounds": "[30,725][510,780]"},
        {
            "content-desc": "AI帮你写, AI帮你写",
            "bounds": "[1280,725][1560,840]",
            "clickable": "true",
        },
        {"content-desc": "ISBN码", "bounds": "[40,920][180,980]"},
        {"content-desc": "分类/ISBN码/成色\uFFFC", "bounds": "[0,1010][1600,1610]"},
        {"content-desc": "分类, 分类", "bounds": "[40,1105][215,1145]"},
        {"content-desc": category_novel, "bounds": "[245,1055][435,1195]", "clickable": "true"},
        {
            "content-desc": "可选家居摆件, 家居摆件",
            "bounds": "[455,1055][645,1195]",
            "clickable": "true",
        },
        {"content-desc": "成色, 成色", "bounds": "[40,1265][215,1305]"},
        {"content-desc": "可选全新, 全新", "bounds": "[245,1355][375,1495]", "clickable": "true"},
        {
            "content-desc": "商品规格\n非必填，设置多个颜色、尺码等",
            "bounds": "[40,1495][1530,1585]",
        },
        {"content-desc": "价格设置", "bounds": "[70,1585][1530,1725]"},
        {"content-desc": "发货方式\n包邮", "bounds": "[70,1725][1530,1865]"},
        {"content-desc": "选择位置", "bounds": "[70,1865][1530,2005]"},
    ]


def _location_region_picker_elements(labels: list[str]) -> list[dict]:
    elements: list[dict] = [
        {"text": "返回", "bounds": "[35,105][90,165]"},
        {"text": "所在地", "bounds": "[735,106][864,164]"},
        {"text": "获取当前位置", "bounds": "[30,228][240,275]"},
        {"text": "当前定位", "bounds": "[270,231][390,272]"},
    ]
    top = 315
    row_height = 102
    for index, label in enumerate(labels):
        row_top = top + (index * row_height)
        row_bottom = row_top + row_height
        elements.append(
            {
                "text": label,
                "clickable": "true",
                "bounds": f"[0,{row_top}][1600,{row_bottom}]",
            }
        )
    return elements


def _location_search_screen_elements(
    *,
    query: str = "",
    results: list[str] | None = None,
) -> list[dict]:
    elements: list[dict] = [
        {
            "class": "android.widget.EditText",
            "package": "com.taobao.idlefish",
            "hint": "搜索地址",
            "text": query,
            "clickable": "true",
            "focused": "true",
            "bounds": "[130,91][1420,179]",
        },
        {
            "text": "取消",
            "package": "com.taobao.idlefish",
            "clickable": "true",
            "bounds": "[1480,111][1560,159]",
        },
    ]
    top = 215
    row_height = 200
    for index, result in enumerate(results or []):
        row_top = top + (index * row_height)
        row_bottom = row_top + row_height
        elements.append(
            {
                "text": result,
                "package": "com.taobao.idlefish",
                "class": "android.view.View",
                "clickable": "true",
                "bounds": f"[0,{row_top}][1600,{row_bottom}]",
            }
        )
    elements.extend(
        [
            {
                "text": "菜单",
                "package": "com.huawei.ohos.inputmethod",
                "class": "android.view.View",
                "clickable": "true",
                "bounds": "[0,1753][266,1895]",
            },
            {
                "text": "隐藏键盘",
                "package": "com.huawei.ohos.inputmethod",
                "class": "android.view.View",
                "clickable": "false",
                "bounds": "[1334,1753][1600,1895]",
            },
        ]
    )
    return elements


def _listing_detail_elements() -> list[dict]:
    return [
        {"text": "返回", "bounds": "[35,105][90,165]"},
        {"text": "搜索按钮", "bounds": "[1120,104][1180,166]"},
        {"text": "搜索你要的宝贝", "bounds": "[140,95][1080,175]"},
        {"text": "分享按钮", "bounds": "[1485,103][1545,167]"},
        {"text": "用户头像", "bounds": "[60,230][160,330]"},
        {"text": "用户昵称：描述为具体的用户昵称", "bounds": "[190,230][980,290]"},
        {"text": "南朝笑不可支的川谷", "bounds": "[60,520][620,600]"},
        {"text": "刚刚擦亮 | 上海", "bounds": "[60,620][420,680]"},
        {"text": "价格-点击播放具体价格", "bounds": "[60,720][520,790]"},
        {"text": "¥", "bounds": "[60,800][105,850]"},
        {"text": "799", "bounds": "[120,780][300,860]"},
        {"text": "包邮", "bounds": "[60,900][180,960]"},
    ]


def test_detects_xianyu_home_screen_and_publish_entry_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        elements=[
            {
                "text": "闲鱼",
                "resource-id": "com.taobao.idlefish:id/tab_title",
                "bounds": "[614,1566][665,1600]",
            },
            {
                "content-desc": "卖闲置",
                "clickable": "true",
                "bounds": "[537,1420][742,1600]",
            },
        ]
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "home"
    assert analysis.current_package == "com.taobao.idlefish"
    assert analysis.visible_texts == ["闲鱼", "卖闲置"]
    assert analysis.targets["publish_entry"].x == 639
    assert analysis.targets["publish_entry"].y == 1510


def test_detects_publish_chooser_from_multiline_accessibility_text():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {
                "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                "clickable": "true",
                "bounds": "[1280,650][2560,873]",
            },
            {
                "content-desc": "关闭",
                "clickable": "true",
                "bounds": "[1280,1470][2560,1600]",
            },
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "publish_chooser"
    assert analysis.targets["publish_idle_item"].x == 1920
    assert analysis.targets["publish_idle_item"].y == 761


def test_detects_draft_resume_dialog_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "你有未编辑完成的宝贝，是否继续？", "bounds": "[0,2025][1600,2560]"},
            {"text": "放弃", "clickable": "true", "bounds": "[40,2355][785,2455]"},
            {"text": "继续", "clickable": "true", "bounds": "[815,2355][1560,2455]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "draft_resume_dialog"
    assert analysis.targets["draft_resume_discard"].x == 412
    assert analysis.targets["draft_resume_continue"].x == 1187
    assert analysis.targets["draft_resume_continue"].y == 2405


def test_detects_portrait_listing_form_instead_of_publish_chooser():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "关闭", "bounds": "[20,100][80,160]"},
            {"text": "发闲置", "bounds": "[120,100][260,160]"},
            {"text": "发布", "bounds": "[1460,100][1560,160]", "clickable": "true"},
            {"text": "添加图片", "bounds": "[80,420][240,480]", "clickable": "true"},
            {"text": "价格设置", "bounds": "[40,2020][220,2080]"},
            {"text": "发货方式\n包邮", "bounds": "[40,2240][260,2320]"},
        ],
        package="com.taobao.idlefish",
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "listing_form"
    assert analysis.targets["submit_listing"].x == 1510
    assert analysis.targets["add_image"].x == 160


def test_detects_portrait_listing_form_targets_from_content_desc():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
            {"content-desc": "草稿箱·1", "bounds": "[1225,115][1410,155]"},
            {
                "content-desc": "发布, 发布",
                "bounds": "[1410,95][1600,175]",
                "clickable": "true",
            },
            {
                "content-desc": "添加图片",
                "bounds": "[70,250][550,730]",
                "clickable": "true",
            },
            {
                "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                "bounds": "[30,737][1570,1264]",
                "clickable": "true",
            },
            {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
            {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "listing_form"
    assert analysis.targets["submit_listing"].text == "发布, 发布"
    assert analysis.targets["submit_listing"].x == 1505
    assert analysis.targets["add_image"].x == 310
    assert analysis.targets["description_entry"].text == "描述, 描述一下宝贝的品牌型号、货品来源…"
    assert analysis.targets["description_entry"].y == 1000


def test_detects_description_entry_and_ignores_description_hint_container():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
            {"content-desc": "存草稿", "bounds": "[1265,115][1410,155]"},
            {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
            {
                "content-desc": "..描述有点少哦，添加品类、品牌等更多商品信息，卖得更快哦",
                "bounds": "[0,190][1600,1693]",
            },
            {"content-desc": "添加图片", "bounds": "[70,645][354,929]"},
            {
                "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                "bounds": "[30,935][1570,1463]",
                "clickable": "true",
            },
            {
                "content-desc": "AI帮你写, AI帮你润色",
                "bounds": "[70,1570][1530,1620]",
                "clickable": "true",
            },
            {"content-desc": "分类, 分类", "bounds": "[40,1765][215,1805]"},
            {
                "content-desc": "已选中生活百科, 生活百科",
                "bounds": "[245,1715][435,1855]",
                "clickable": "true",
            },
            {"content-desc": "分类/游戏名称/客户端", "bounds": "[0,1693][1600,2294]"},
            {"content-desc": "价格设置", "bounds": "[70,2294][1530,2434]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.targets["description_entry"].text == "描述, 描述一下宝贝的品牌型号、货品来源…"
    assert analysis.targets["description_entry"].bounds == "[30,935][1570,1463]"
    assert analysis.targets["description_entry"].y == 1199


def test_detects_listing_form_price_entry_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
            {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
            {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
            {
                "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                "bounds": "[30,737][1570,1264]",
            },
            {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
            {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "listing_form"
    assert analysis.targets["price_entry"].text == "价格设置"
    assert analysis.targets["price_entry"].x == 800
    assert analysis.targets["price_entry"].y == 1705


def test_detects_listing_form_shipping_entry_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
            {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
            {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
            {
                "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                "bounds": "[30,737][1570,1264]",
            },
            {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
            {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "listing_form"
    assert analysis.targets["shipping_entry"].text == "发货方式\n包邮"
    assert analysis.targets["shipping_entry"].x == 800
    assert analysis.targets["shipping_entry"].y == 1845


def test_detects_listing_form_location_entry_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
            {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
            {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
            {
                "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                "bounds": "[30,737][1570,1264]",
            },
            {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
            {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
            {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "listing_form"
    assert analysis.targets["location_entry"].text == "选择位置"
    assert analysis.targets["location_entry"].x == 800
    assert analysis.targets["location_entry"].y == 1985


def test_detects_listing_form_metadata_entry_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
            {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
            {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
            {
                "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                "bounds": "[30,737][1570,1264]",
            },
            {"content-desc": "分类/ISBN码/成色\uFFFC", "bounds": "[0,1494][1600,2095]"},
            {"content-desc": "分类, 分类", "bounds": "[40,1665][215,1705]"},
            {"content-desc": "成色, 成色", "bounds": "[40,1945][215,1985]"},
            {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
            {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2657]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "listing_form"
    assert analysis.targets["metadata_entry"].text == "分类/ISBN码/成色\uFFFC"
    assert analysis.targets["metadata_entry"].x == 800
    assert analysis.targets["metadata_entry"].y == 1794


def test_detects_metadata_panel_instead_of_publish_chooser():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=_metadata_panel_elements(),
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "metadata_panel"
    assert analysis.targets["metadata_category_option_家居摆件"].x == 985
    assert analysis.targets["metadata_category_option_家居摆件"].y == 1685
    assert analysis.targets["metadata_condition_option_几乎全新"].x == 490
    assert analysis.targets["metadata_condition_option_几乎全新"].y == 2105
    assert analysis.targets["metadata_source_option_闲置"].x == 940
    assert analysis.targets["metadata_source_option_闲置"].y == 2245


def test_detects_scrolled_metadata_panel_and_keeps_lower_rows():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=_scrolled_metadata_panel_elements(selected_category="文学/小说"),
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "metadata_panel"
    assert analysis.targets["metadata_category_selected_文学_小说"].x == 340
    assert analysis.targets["price_entry"].text == "价格设置"
    assert analysis.targets["price_entry"].y == 1655
    assert analysis.targets["shipping_entry"].text == "发货方式\n包邮"
    assert analysis.targets["location_entry"].text == "选择位置"


def test_detects_location_panel_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "返回", "bounds": "[0,80][200,190]"},
            {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
            {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
            {"text": "常用地址", "bounds": "[0,420][1600,513]"},
            {
                "text": "EFC LIVE欧美广场商业A区\n景兴路896号",
                "clickable": "true",
                "bounds": "[0,513][1600,713]",
            },
            {"text": "城市区域", "bounds": "[0,1733][1600,1813]"},
            {
                "text": "请选择宝贝所在地",
                "clickable": "true",
                "bounds": "[0,1813][1600,1953]",
            },
            {"text": "去选择", "clickable": "true", "bounds": "[0,1965][1600,2005]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "location_panel"
    assert analysis.targets["location_back"].x == 100
    assert analysis.targets["location_search"].text == "搜索地址"
    assert analysis.targets["location_region_entry"].text == "请选择宝贝所在地"
    assert analysis.targets["location_region_entry"].y == 1883


def test_detects_location_region_picker_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "返回", "bounds": "[35,105][90,165]"},
            {"text": "所在地", "bounds": "[735,106][864,164]"},
            {"text": "获取当前位置", "bounds": "[30,228][240,275]"},
            {"text": "当前定位", "bounds": "[270,231][390,272]"},
            {"text": "北京", "clickable": "true", "bounds": "[0,315][1600,417]"},
            {"text": "上海", "clickable": "true", "bounds": "[0,1147][1600,1249]"},
            {"text": "浙江", "clickable": "true", "bounds": "[0,1355][1600,1457]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "location_region_picker"
    assert analysis.targets["location_region_back"].x == 62
    assert analysis.targets["location_region_get_current"].text == "获取当前位置"
    assert analysis.targets["location_region_option_上海"].x == 800
    assert analysis.targets["location_region_option_上海"].y == 1198


def test_detects_location_search_screen_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=_location_search_screen_elements(
            query="上海虹桥站",
            results=[
                "上海虹桥站\n新虹街道申贵路1500号",
                "上海虹桥站P9地下停车场\n华漕镇申虹路",
            ],
        ),
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "location_search_screen"
    assert analysis.targets["location_search_input"].text == "上海虹桥站"
    assert analysis.targets["location_search_cancel"].text == "取消"
    assert (
        analysis.targets["location_search_result_0"].text
        == "上海虹桥站\n新虹街道申贵路1500号"
    )
    assert (
        analysis.targets["location_search_result_1"].text
        == "上海虹桥站P9地下停车场\n华漕镇申虹路"
    )


def test_detects_publish_success_screen_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "宝贝发布成功", "bounds": "[520,410][1080,490]"},
            {"text": "分享给更多人", "bounds": "[600,560][1000,620]"},
            {"text": "看看宝贝", "clickable": "true", "bounds": "[220,1960][760,2090]"},
            {"text": "继续发布", "clickable": "true", "bounds": "[840,1960][1380,2090]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "publish_success"
    assert analysis.targets["publish_success_view_listing"].text == "看看宝贝"
    assert analysis.targets["publish_success_continue"].text == "继续发布"


def test_detects_publish_success_screen_with_reward_variant():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "发布成功", "bounds": "[698,1303][1000,1381]"},
            {"text": "100闲鱼币", "bounds": "[763,1432][1048,1505]"},
            {"text": "点击领取", "bounds": "[1159,1432][1399,1505]"},
            {"text": "再发一件", "bounds": "[663,2340][938,2422]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "publish_success"
    assert "publish_success_view_listing" not in analysis.targets
    assert analysis.targets["publish_success_continue"].text == "再发一件"


def test_detects_listing_detail_screen_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.taobao.idlefish.detail.DetailActivity",
        elements=_listing_detail_elements(),
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "listing_detail"
    assert analysis.targets["listing_detail_back"].text == "返回"
    assert analysis.targets["listing_detail_search"].text == "搜索按钮"
    assert analysis.targets["listing_detail_share"].text == "分享按钮"


def test_detects_publish_location_required_dialog_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {
                "text": (
                    "无法发布宝贝\n"
                    "系统无法定位您所在的行政区，请点击宝贝图片下方位置图标，手动选择行政区。"
                ),
                "bounds": "[250,980][1350,1380]",
            },
            {"text": "取消", "clickable": "true", "bounds": "[300,1510][700,1610]"},
            {"text": "我知道了", "clickable": "true", "bounds": "[900,1510][1300,1610]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "publish_location_required_dialog"
    assert analysis.targets["publish_location_required_cancel"].text == "取消"
    assert analysis.targets["publish_location_required_ack"].text == "我知道了"


def test_detects_description_editor_from_portrait_form():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
            {"content-desc": "草稿箱·1", "bounds": "[1225,115][1410,155]"},
            {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
            {
                "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                "bounds": "[30,737][1570,1610]",
                "clickable": "true",
            },
            {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
            {"content-desc": "主题", "bounds": "[10,1611][190,1731]"},
            {"content-desc": "表情", "bounds": "[190,1611][380,1731]"},
            {"content-desc": "识物", "bounds": "[380,1611][570,1731]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "description_editor"
    assert analysis.targets["description_done"].text == "完成"
    assert analysis.targets["description_done"].x == 1525
    assert analysis.targets["description_entry"].text == "描述, 描述一下宝贝的品牌型号、货品来源…"


def test_detects_price_panel_with_confirm_delete_and_keypad_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {
                "text": "可以设「粉丝价」啦！快去给你的粉丝专属优惠吧！",
                "bounds": "[0,965][1600,2560]",
            },
            {"text": "价格设置", "bounds": "[40,1258][1560,1378]"},
            {"text": "设置粉丝价", "bounds": "[40,1378][315,1498]"},
            {"text": "原价设置", "bounds": "[40,1503][1560,1623]"},
            {"text": "库存设置", "bounds": "[40,1628][1560,1748]"},
            {"text": "1", "bounds": "[120,1961][280,2109]"},
            {"text": "3", "bounds": "[920,1961][1080,2109]"},
            {"text": "9", "bounds": "[920,2261][1080,2409]"},
            {"text": ".", "bounds": "[120,2411][280,2559]"},
            {"text": "删除", "bounds": "[1320,2035][1480,2185]"},
            {"text": "确定", "bounds": "[1320,2335][1480,2485]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "price_panel"
    assert analysis.targets["price_confirm"].x == 1400
    assert analysis.targets["price_delete"].x == 1400
    assert analysis.targets["price_key_3"].x == 1000
    assert analysis.targets["price_key_9"].y == 2335
    assert analysis.targets["price_key_decimal"].text == "."


def test_detects_shipping_panel_with_mail_option_targets():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
            {
                "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                "bounds": "[30,1255][1570,1893]",
            },
            {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
            {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
            {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
            {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
            {"text": "买家自提", "bounds": "[30,1893][1570,2063]"},
            {"text": "确定", "bounds": "[760,2381][840,2429]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "shipping_panel"
    assert analysis.targets["shipping_confirm"].x == 800
    assert analysis.targets["shipping_option_mail_free"].text == "包邮"
    assert analysis.targets["shipping_option_mail_free"].x == 95
    assert analysis.targets["shipping_option_mail_free"].y == 1446
    assert analysis.targets["shipping_option_mail_distance"].y == 1574
    assert analysis.targets["shipping_option_mail_fixed"].y == 1701
    assert analysis.targets["shipping_option_no_mail"].y == 1829


def test_detects_media_permission_dialog_and_album_picker():
    analyzer = XianyuFlowAnalyzer()
    permission_screen = _make_screen(
        package="com.android.permissioncontroller",
        activity="com.android.permissioncontroller.permission.ui.GrantPermissionsActivity",
        elements=[
            {
                "text": "是否允许“闲鱼”访问媒体？",
                "bounds": "[584,468][1976,562]",
            },
            {
                "text": "允许",
                "clickable": "true",
                "bounds": "[1280,970][1920,1122]",
            },
        ],
    )
    album_screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {
                "text": "所有文件",
                "bounds": "[1179,102][1382,172]",
            },
            {
                "text": "选择",
                "clickable": "true",
                "bounds": "[1790,202][1947,319]",
            },
            {
                "text": "确定",
                "clickable": "true",
                "bounds": "[1680,1320][2160,1510]",
            },
            {
                "text": "相册",
                "bounds": "[1620,1520][1720,1590]",
            },
        ],
    )

    permission_analysis = analyzer.detect_screen(permission_screen)
    album_analysis = analyzer.detect_screen(album_screen)

    assert permission_analysis.screen_name == "media_permission_dialog"
    assert permission_analysis.targets["permission_allow"].x == 1600
    assert permission_analysis.targets["permission_allow"].y == 1046
    assert album_analysis.screen_name == "album_picker"
    assert album_analysis.targets["album_select"].x == 1868
    assert album_analysis.targets["album_select"].y == 260
    assert album_analysis.targets["album_confirm"].x == 1920
    assert album_analysis.targets["album_confirm"].y == 1415


def test_detects_media_source_picker_with_album_tab_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "拍更多细节照", "bounds": "[580,240][1080,320]"},
            {"content-desc": "拍摄, 拍摄", "bounds": "[690,1960][910,2140]"},
            {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
            {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
            {"content-desc": "拍照\nTab 2 of 3", "bounds": "[715,2440][885,2560]"},
            {"content-desc": "拍视频\nTab 3 of 3", "bounds": "[905,2440][1075,2560]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "media_source_picker"
    assert analysis.targets["media_picker_album_tab"].text == "相册\nTab 1 of 3"
    assert analysis.targets["media_picker_album_tab"].x == 610
    assert analysis.targets["media_picker_album_tab"].y == 2500


def test_detects_album_source_menu_and_preferred_source_target():
    analyzer = XianyuFlowAnalyzer(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish")
    )
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "所有文件", "bounds": "[1810,85][2030,185]"},
            {"text": "所有文件·889", "bounds": "[1600,320][2240,470]"},
            {"text": "所有视频·492", "bounds": "[1600,500][2240,650]"},
            {"text": "XianyuPublish·1", "bounds": "[1600,650][2240,800]"},
            {"text": "查看大图", "bounds": "[1601,210][1918,526]"},
            {"text": "选择", "bounds": "[1818,210][1918,310]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "album_source_menu"
    assert analysis.targets["album_source"].x == 1920
    assert analysis.targets["album_source"].y == 135
    assert analysis.targets["preferred_album_source"].text == "XianyuPublish·1"
    assert analysis.targets["preferred_album_source"].x == 1920
    assert analysis.targets["preferred_album_source"].y == 725


def test_detects_album_picker_when_preferred_source_is_selected():
    analyzer = XianyuFlowAnalyzer(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish")
    )
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
            {"text": "预览", "bounds": "[2320,118][2380,165]"},
            {"text": "查看大图", "bounds": "[1601,210][1918,526]"},
            {"text": "选择", "bounds": "[1818,210][1918,310]"},
            {"text": "关闭", "bounds": "[1280,1470][2560,1600]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "album_picker"
    assert analysis.targets["album_source"].text == "XianyuPublish"
    assert analysis.targets["album_select"].x == 1868
    assert analysis.targets["album_select"].y == 260


def test_detects_selected_media_preview_with_next_step_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "关闭", "bounds": "[15,88][115,188]", "clickable": "true"},
            {"text": "XianyuPublish", "bounds": "[633,85][968,185]", "clickable": "true"},
            {"text": "查看大图", "bounds": "[401,210][798,606]", "clickable": "true"},
            {"text": "取消选择, 1", "bounds": "[698,210][798,310]", "clickable": "true"},
            {"text": "删除图片", "bounds": "[40,2380][190,2520]", "clickable": "true"},
            {"text": "下一步 (1)", "bounds": "[1340,2380][1560,2520]", "clickable": "true"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "selected_media_preview"
    assert analysis.targets["media_preview_next_step"].x == 1450
    assert analysis.targets["media_preview_next_step"].y == 2450


def test_detects_media_edit_screen_with_done_target():
    analyzer = XianyuFlowAnalyzer()
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "1/1", "bounds": "[0,0][1600,2560]"},
            {"text": "点击添加标签", "bounds": "[0,190][1600,2135]", "clickable": "true"},
            {"text": "裁剪", "bounds": "[50,2175][300,2315]", "clickable": "true"},
            {"text": "背景模糊", "bounds": "[1300,2175][1550,2315]", "clickable": "true"},
            {"text": "完成", "bounds": "[1300,2410][1520,2490]", "clickable": "true"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "media_edit_screen"
    assert analysis.targets["media_edit_done"].x == 1410
    assert analysis.targets["media_edit_done"].y == 2450


def test_detects_photo_analysis_screen_after_confirm():
    analyzer = XianyuFlowAnalyzer(settings=XianyuPublishSettings())
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
            {"text": "7张照片", "bounds": "[1360,607][1460,635]"},
            {"text": "添加", "bounds": "[2268,537][2328,567]"},
            {"text": "照片模糊未识别到宝贝\n删除", "bounds": "[1280,681][2560,1600]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "photo_analysis"
    assert analysis.visible_texts == [
        "宝贝价格是根据市场行情计算得出",
        "7张照片",
        "添加",
        "照片模糊未识别到宝贝\n删除",
    ]


def test_detects_photo_analysis_screen_while_price_is_still_computing():
    analyzer = XianyuFlowAnalyzer(settings=XianyuPublishSettings())
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
            {"text": "13张照片", "bounds": "[1360,607][1460,635]"},
            {"text": "添加", "bounds": "[2268,537][2328,567]"},
            {
                "text": "价格计算中 预计需要2分钟\n宝贝价格是根据市场行情计算得出，完成后通知你",
                "bounds": "[1280,686][2560,1600]",
            },
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "photo_analysis"


def test_detects_space_items_empty_screen_after_switching_to_baobei_tab():
    analyzer = XianyuFlowAnalyzer(settings=XianyuPublishSettings())
    screen = _make_screen(
        activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
        elements=[
            {
                "text": "南朝笑不可支的川谷\n发宝贝\n投缘优惠",
                "bounds": "[1280,0][2560,1600]",
            },
            {"text": "宝贝", "bounds": "[1295,229][1453,324]", "clickable": "true"},
            {"text": "这里空空如也～", "bounds": "[1789,881][2051,941]"},
        ],
    )

    analysis = analyzer.detect_screen(screen)

    assert analysis.screen_name == "space_items_empty"


def test_open_home_uses_explicit_main_activity_shell():
    android_service = FakeAndroidService(screens=[_make_screen(elements=[])])
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    flow.open_home("device-1")

    android_service.device.shell.assert_called_once_with(
        "am start -n com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity"
    )


def test_advance_to_album_picker_taps_home_entry_then_publish_choice():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                    },
                    {"content-desc": "关闭", "bounds": "[1280,1470][2560,1600]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1179,102][1382,172]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                    {"text": "相册", "bounds": "[1620,1520][1720,1590]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_to_album_picker("device-1")

    assert result.screen_name == "album_picker"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
    ]


def test_advance_to_album_picker_handles_media_permission_dialog():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                    },
                    {"content-desc": "关闭", "bounds": "[1280,1470][2560,1600]"},
                ],
            ),
            _make_screen(
                package="com.android.permissioncontroller",
                activity="com.android.permissioncontroller.permission.ui.GrantPermissionsActivity",
                elements=[
                    {
                        "text": "是否允许“闲鱼”访问媒体？",
                        "bounds": "[584,468][1976,562]",
                    },
                    {"text": "允许", "bounds": "[1280,970][1920,1122]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1179,102][1382,172]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                    {"text": "确定", "bounds": "[1680,1320][2160,1510]"},
                    {"text": "相册", "bounds": "[1620,1520][1720,1590]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_to_album_picker("device-1")

    assert result.screen_name == "album_picker"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
        ("device-1", 1600, 1046),
    ]


def test_advance_to_listing_form_forces_portrait_then_taps_publish_entry_and_publish_idle_item():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "关闭", "bounds": "[20,100][80,160]"},
                    {"text": "发闲置", "bounds": "[120,100][260,160]"},
                    {"text": "发布", "bounds": "[1460,100][1560,160]", "clickable": "true"},
                    {"text": "添加图片", "bounds": "[80,420][240,480]", "clickable": "true"},
                    {"text": "价格设置", "bounds": "[40,2020][220,2080]"},
                    {"text": "发货方式\n包邮", "bounds": "[40,2240][260,2320]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
    ]
    android_service.device.shell.assert_has_calls(
        [
            call("settings put system accelerometer_rotation 0"),
            call("settings put system user_rotation 0"),
        ]
    )


def test_advance_to_listing_form_returns_existing_listing_form_without_extra_taps():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "关闭", "bounds": "[20,100][80,160]"},
                    {"text": "发闲置", "bounds": "[120,100][260,160]"},
                    {"text": "发布", "bounds": "[1460,100][1560,160]", "clickable": "true"},
                    {"text": "添加图片", "bounds": "[80,420][240,480]", "clickable": "true"},
                    {"text": "价格设置", "bounds": "[40,2020][220,2080]"},
                    {"text": "发货方式\n包邮", "bounds": "[40,2240][260,2320]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == []


def test_advance_to_listing_form_returns_existing_metadata_panel_without_extra_taps():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == []


def test_advance_to_listing_form_discards_existing_draft_by_default():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "你有未编辑完成的宝贝，是否继续？", "bounds": "[0,2025][1600,2560]"},
                    {"text": "放弃", "clickable": "true", "bounds": "[40,2355][785,2455]"},
                    {"text": "继续", "clickable": "true", "bounds": "[815,2355][1560,2455]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
        ("device-1", 412, 2405),
    ]


def test_advance_to_listing_form_can_continue_existing_draft_when_configured():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "你有未编辑完成的宝贝，是否继续？", "bounds": "[0,2025][1600,2560]"},
                    {"text": "放弃", "clickable": "true", "bounds": "[40,2355][785,2455]"},
                    {"text": "继续", "clickable": "true", "bounds": "[815,2355][1560,2455]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(draft_resume_action="continue"),
        android_service=android_service,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
        ("device-1", 1187, 2405),
    ]


def test_advance_to_listing_form_accepts_metadata_panel_after_draft_resume_discard():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "你有未编辑完成的宝贝，是否继续？", "bounds": "[0,2025][1600,2560]"},
                    {"text": "放弃", "clickable": "true", "bounds": "[40,2355][785,2455]"},
                    {"text": "继续", "clickable": "true", "bounds": "[815,2355][1560,2455]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [("device-1", 412, 2405)]


def test_advance_to_listing_form_waits_for_listing_form_after_tapping_draft_resume_discard():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "你有未编辑完成的宝贝，是否继续？", "bounds": "[0,2025][1600,2560]"},
                    {"text": "放弃", "clickable": "true", "bounds": "[40,2355][785,2455]"},
                    {"text": "继续", "clickable": "true", "bounds": "[815,2355][1560,2455]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "你有未编辑完成的宝贝，是否继续？", "bounds": "[0,2025][1600,2560]"},
                    {"text": "放弃", "clickable": "true", "bounds": "[40,2355][785,2455]"},
                    {"text": "继续", "clickable": "true", "bounds": "[815,2355][1560,2455]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 2, 3},
        advance_on_get_indices={3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
        ("device-1", 412, 2405),
    ]


def test_advance_to_listing_form_waits_through_stale_home_and_publish_chooser_snapshots():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "你有未编辑完成的宝贝，是否继续？", "bounds": "[0,2025][1600,2560]"},
                    {"text": "放弃", "clickable": "true", "bounds": "[40,2355][785,2455]"},
                    {"text": "继续", "clickable": "true", "bounds": "[815,2355][1560,2455]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 2, 3},
        advance_on_get_indices={1, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
        ("device-1", 412, 2405),
    ]


def test_advance_to_listing_form_waits_through_unknown_xianyu_overlay():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                elements=[
                    {"text": "闲鱼", "bounds": "[614,1566][665,1600]"},
                    {"content-desc": "卖闲置", "bounds": "[537,1420][742,1600]"},
                ]
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[1280,1470][2560,1600]"},
                    {"text": "13:46", "bounds": "[0,0][120,60]"},
                    {"text": "开启护眼模式", "bounds": "[0,60][320,120]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 2},
        advance_on_get_indices={1, 2},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.advance_to_listing_form("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 639, 1510),
        ("device-1", 1920, 761),
    ]


def test_advance_listing_form_to_album_picker_taps_add_image():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "所有文件", "bounds": "[690,85][910,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_album_picker("device-1")

    assert result.screen_name == "album_picker"
    assert android_service.tap_calls == [("device-1", 310, 490)]


def test_advance_listing_form_to_album_picker_switches_camera_picker_to_album_tab():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "拍更多细节照", "bounds": "[580,240][1080,320]"},
                    {"content-desc": "拍摄, 拍摄", "bounds": "[690,1960][910,2140]"},
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                    {"content-desc": "拍照\nTab 2 of 3", "bounds": "[715,2440][885,2560]"},
                    {"content-desc": "拍视频\nTab 3 of 3", "bounds": "[905,2440][1075,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "所有文件", "bounds": "[690,85][910,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_album_picker("device-1")

    assert result.screen_name == "album_picker"
    assert android_service.tap_calls == [
        ("device-1", 310, 490),
        ("device-1", 610, 2500),
    ]


def test_advance_listing_form_to_album_picker_can_start_from_metadata_panel():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "分类, 分类", "bounds": "[70,1600][220,1650]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "成色, 成色", "bounds": "[70,1800][220,1850]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "所有文件", "bounds": "[690,85][910,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_album_picker("device-1")

    assert result.screen_name == "album_picker"
    assert android_service.tap_calls == [("device-1", 310, 490)]


def test_advance_listing_form_to_location_region_picker_taps_choose_region():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                    {"text": "去选择", "clickable": "true", "bounds": "[0,1965][1600,2005]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[35,105][90,165]"},
                    {"text": "所在地", "bounds": "[735,106][864,164]"},
                    {"text": "获取当前位置", "bounds": "[30,228][240,275]"},
                    {"text": "当前定位", "bounds": "[270,231][390,272]"},
                    {"text": "上海", "clickable": "true", "bounds": "[0,1147][1600,1249]"},
                    {"text": "浙江", "clickable": "true", "bounds": "[0,1355][1600,1457]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_location_region_picker("device-1")

    assert result.screen_name == "location_region_picker"
    assert android_service.tap_calls == [
        ("device-1", 800, 1985),
        ("device-1", 800, 1883),
    ]


def test_advance_listing_form_to_location_panel_can_start_from_metadata_panel():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_scrolled_metadata_panel_elements(selected_category="文学/小说"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_location_panel("device-1")

    assert result.screen_name == "location_panel"
    assert android_service.tap_calls == [("device-1", 800, 1935)]


def test_location_panel_scrolls_metadata_until_location_row_is_visible():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(
                    selected_category="显示器",
                    selected_condition="几乎全新",
                ),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_scrolled_metadata_panel_elements(selected_category="显示器"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                ],
            ),
        ],
        advance_on_swipe_calls={1},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_location_panel("device-1")

    assert result.screen_name == "location_panel"
    assert android_service.swipe_calls == [
        ("device-1", 800, 2099, 800, 896, 350),
    ]
    assert android_service.tap_calls == [("device-1", 800, 1935)]


def test_set_location_region_path_taps_city_twice_then_district_and_returns_listing_form():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(
                    ["北京", "天津", "河北", "上海", "江苏", "浙江"]
                ),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["上海"]),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["黄浦区", "徐汇区", "长宁区"]),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.set_location_region_path("device-1", ["上海", "黄浦区"])

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 1985),
        ("device-1", 800, 1883),
        ("device-1", 800, 672),
        ("device-1", 800, 366),
        ("device-1", 800, 366),
    ]


def test_set_location_region_path_raises_when_next_segment_never_appears():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["北京", "上海"]),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["上海"]),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["黄浦区", "徐汇区"]),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    with pytest.raises(RuntimeError, match="Location path segment not found"):
        flow.set_location_region_path("device-1", ["上海", "浦东新区"])


def test_set_location_region_path_waits_for_final_picker_tail_to_leave():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(
                    ["北京", "天津", "河北", "上海", "江苏", "浙江"]
                ),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["上海"]),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["黄浦区", "徐汇区", "长宁区"]),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_region_picker_elements(["黄浦区", "徐汇区", "长宁区"]),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 2, 3, 4, 5},
        advance_on_get_indices={5},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.set_location_region_path("device-1", ["上海", "黄浦区"])

    assert result.screen_name == "listing_form"


def test_search_location_and_select_result_uses_focused_text_and_taps_first_result():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_search_screen_elements(),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_search_screen_elements(
                    query="上海虹桥站",
                    results=[
                        "上海虹桥站\n新虹街道申贵路1500号",
                        "上海虹桥站P9地下停车场\n华漕镇申虹路",
                    ],
                ),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ],
        advance_on_focused_text_indices={1},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.search_location_and_select_result("device-1", "上海虹桥站")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 245),
        ("device-1", 800, 315),
    ]
    assert android_service.set_focused_text_calls == [("device-1", "上海虹桥站")]


def test_search_location_and_select_result_waits_for_results_after_setting_text():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_search_screen_elements(),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_search_screen_elements(query="上海虹桥站"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_search_screen_elements(
                    query="上海虹桥站",
                    results=["上海虹桥站\n新虹街道申贵路1500号"],
                ),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                    {"content-desc": "选择位置", "bounds": "[70,1915][1530,2055]"},
                ],
            ),
        ],
        advance_on_focused_text_indices={1},
        advance_on_get_indices={2},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.search_location_and_select_result("device-1", "上海虹桥站")

    assert result.screen_name == "listing_form"
    assert android_service.set_focused_text_calls == [("device-1", "上海虹桥站")]


def test_location_search_can_scroll_metadata_panel_before_opening_search():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(
                    selected_category="显示器",
                    selected_condition="几乎全新",
                ),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_scrolled_metadata_panel_elements(selected_category="显示器"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "返回", "bounds": "[0,80][200,190]"},
                    {"text": "宝贝所在地", "bounds": "[694,110][906,160]"},
                    {"text": "搜索地址", "bounds": "[40,200][1560,290]"},
                    {"text": "常用地址", "bounds": "[0,420][1600,513]"},
                    {
                        "text": "请选择宝贝所在地",
                        "clickable": "true",
                        "bounds": "[0,1813][1600,1953]",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_search_screen_elements(),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_location_search_screen_elements(
                    query="上海虹桥站",
                    results=["上海虹桥站\n新虹街道申贵路1500号"],
                ),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_scrolled_metadata_panel_elements(selected_category="显示器"),
            ),
        ],
        advance_on_swipe_calls={1},
        advance_on_focused_text_indices={3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.search_location_and_select_result("device-1", "上海虹桥站")

    assert result.screen_name == "metadata_panel"
    assert android_service.swipe_calls == [
        ("device-1", 800, 2099, 800, 896, 350),
    ]
    assert android_service.tap_calls == [
        ("device-1", 800, 1935),
        ("device-1", 800, 245),
        ("device-1", 800, 315),
    ]


def test_advance_listing_form_to_metadata_panel_taps_metadata_entry():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "分类/ISBN码/成色\uFFFC", "bounds": "[0,1494][1600,2095]"},
                    {"content-desc": "分类, 分类", "bounds": "[40,1665][215,1705]"},
                    {"content-desc": "成色, 成色", "bounds": "[40,1945][215,1985]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2657]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_metadata_panel("device-1")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [("device-1", 800, 1794)]


def test_set_item_condition_selects_option_and_verifies_selected_state():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "分类/ISBN码/成色\uFFFC", "bounds": "[0,1494][1600,2095]"},
                    {"content-desc": "分类, 分类", "bounds": "[40,1665][215,1705]"},
                    {"content-desc": "成色, 成色", "bounds": "[40,1945][215,1985]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2657]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_condition="几乎全新"),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.set_item_condition("device-1", "几乎全新")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [
        ("device-1", 800, 1794),
        ("device-1", 490, 2105),
    ]


def test_set_item_source_selects_option_and_verifies_selected_state():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_source="闲置"),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.set_item_source("device-1", "闲置")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [("device-1", 940, 2245)]


def test_set_item_category_selects_option_and_verifies_selected_state():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="家居摆件"),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.set_item_category("device-1", "家居摆件")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [("device-1", 985, 1685)]


def test_set_item_category_returns_immediately_when_value_already_matches():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="家居摆件"),
            )
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.set_item_category("device-1", "家居摆件")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == []


def test_advance_listing_form_to_album_picker_handles_media_permission_dialog():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                package="com.android.permissioncontroller",
                activity="com.android.permissioncontroller.permission.ui.GrantPermissionsActivity",
                elements=[
                    {"text": "是否允许“闲鱼”访问媒体？", "bounds": "[584,468][1976,562]"},
                    {"text": "允许", "bounds": "[1280,970][1920,1122]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "所有文件", "bounds": "[690,85][910,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_album_picker("device-1")

    assert result.screen_name == "album_picker"
    assert android_service.tap_calls == [
        ("device-1", 310, 490),
        ("device-1", 1600, 1046),
    ]


def test_advance_listing_form_to_album_picker_waits_for_album_picker_after_loading_gap():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "所有文件", "bounds": "[690,85][910,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
        ],
        advance_on_get_indices={1},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.advance_listing_form_to_album_picker("device-1")

    assert result.screen_name == "album_picker"
    assert android_service.tap_calls == [("device-1", 310, 490)]


def test_advance_listing_form_to_description_editor_taps_description_entry():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_description_editor("device-1")

    assert result.screen_name == "description_editor"
    assert android_service.tap_calls == [("device-1", 800, 1000)]


def test_advance_listing_form_to_description_editor_can_start_from_metadata_panel():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[560,250][1040,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_description_editor("device-1")

    assert result.screen_name == "description_editor"
    assert android_service.tap_calls == [("device-1", 800, 1000)]


def test_advance_listing_form_to_description_editor_waits_through_metadata_panel_tail():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
        ],
        advance_on_get_indices={1},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_description_editor("device-1")

    assert result.screen_name == "description_editor"
    assert android_service.tap_calls == [("device-1", 800, 1000)]


def test_fill_description_inputs_text_and_taps_done():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.fill_description("device-1", "九成新人体工学椅，自提优先")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 1525, 1671),
    ]
    assert android_service.input_text_calls == [("device-1", "九成新人体工学椅，自提优先")]


def test_fill_description_returns_immediately_when_input_text_already_restores_listing_form():
    description = "自动回表单描述"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"text": description, "bounds": "[120,900][900,980]"},
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_input_indices={1},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [("device-1", 800, 1000)]
    assert android_service.input_text_calls == [("device-1", description)]


def test_fill_description_retries_when_input_text_restores_listing_form_without_visible_text():
    description = "34寸显示器 成色很好 北京自提"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "34寸显示器 成色很好 北京自提, 闲鱼",
                        "bounds": "[70,775][1525,833]",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"text": description, "bounds": "[120,900][900,980]"},
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_input_indices={1},
        advance_on_set_text_by_description_indices={3},
        advance_on_tap_calls={1, 2, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "listing_form"
    assert android_service.input_text_calls == [("device-1", description)]
    assert android_service.set_text_by_description_calls == []
    assert android_service.set_text_on_description_child_calls == [
        ("device-1", "描述, 描述一下宝贝的品牌型号、货品来源…", description),
        ("device-1", "描述, 描述一下宝贝的品牌型号、货品来源…", description),
    ]
    assert android_service.set_clipboard_text_calls == []
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 800, 1000),
        ("device-1", 1525, 1671),
    ]


def test_fill_description_prefers_direct_description_child_set_when_listing_form_allows_it():
    description = "34寸显示器\n\n成色很好，北京自提。"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "存草稿", "bounds": "[1265,115][1410,155]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"text": description, "bounds": "[70,775][1525,950]"},
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    *_metadata_panel_elements(
                        selected_category="显示器",
                        selected_condition="几乎全新",
                    ),
                    {"text": description, "bounds": "[120,930][1000,1030]"},
                ],
            ),
        ],
        advance_on_set_text_by_description_indices={0},
        advance_on_tap_calls={1},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "metadata_panel"
    assert android_service.set_text_on_description_child_calls == [
        ("device-1", "描述, 描述一下宝贝的品牌型号、货品来源…", description),
    ]
    assert android_service.input_text_calls == []
    assert android_service.tap_calls == [("device-1", 1525, 1671)]


def test_fill_description_accepts_metadata_panel_after_done():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[560,250][1040,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.fill_description("device-1", "描述完成后滚到规格区域")

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 1525, 1671),
    ]
    assert android_service.input_text_calls == [("device-1", "描述完成后滚到规格区域")]


def test_fill_description_falls_back_to_clipboard_paste_when_input_text_does_not_persist():
    description = "34寸显示器\n\n成色很好，北京自提。"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "分类, 分类", "bounds": "[70,1600][220,1650]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "成色, 成色", "bounds": "[70,1800][220,1850]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"text": "34寸显示器", "bounds": "[120,930][600,980]"},
                    {"text": "粘贴", "bounds": "[260,860][420,940]", "clickable": "true"},
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"text": "34寸显示器", "bounds": "[120,930][600,980]"},
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_input_indices={1},
        advance_on_tap_calls={1, 2, 3, 5},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "listing_form"
    assert android_service.input_text_calls == [
        ("device-1", description),
        ("device-1", description),
    ]
    assert android_service.set_clipboard_text_calls == [("device-1", description)]
    assert android_service.long_press_calls == [("device-1", 800, 1173)]
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 800, 1000),
        ("device-1", 800, 1173),
        ("device-1", 340, 900),
        ("device-1", 1525, 1671),
    ]


def test_fill_description_clipboard_fallback_waits_through_publish_chooser_tail():
    description = "34寸显示器\n\n成色很好，北京自提。"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"text": "34寸显示器", "bounds": "[120,930][600,980]"},
                    {"text": "粘贴", "bounds": "[260,860][420,940]", "clickable": "true"},
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "clickable": "true",
                        "bounds": "[1280,650][2560,873]",
                    },
                    {
                        "content-desc": "关闭",
                        "clickable": "true",
                        "bounds": "[1280,1470][2560,1600]",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    *_metadata_panel_elements(selected_category="生活百科"),
                    {"text": "34寸显示器", "bounds": "[120,930][600,980]"},
                ],
            ),
        ],
        advance_on_get_indices={5},
        advance_on_input_indices={1},
        advance_on_tap_calls={1, 2, 3, 5},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 800, 1000),
        ("device-1", 800, 1173),
        ("device-1", 340, 900),
        ("device-1", 1525, 1671),
    ]


def test_fill_description_rechecks_editor_before_using_clipboard_fallback():
    description = "34寸显示器\n\n成色很好，北京自提。"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"text": "34寸显示器", "bounds": "[120,930][600,980]"},
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
        ],
        advance_on_input_indices={1},
        advance_on_set_text_by_description_indices={3},
        advance_on_tap_calls={1, 2, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "metadata_panel"
    assert android_service.input_text_calls == [("device-1", description)]
    assert android_service.set_clipboard_text_calls == []
    assert android_service.long_press_calls == []
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 800, 1000),
        ("device-1", 1525, 1671),
    ]


def test_fill_description_retries_input_from_editor_before_using_clipboard_fallback():
    description = "34寸显示器\n\n成色很好，北京自提。"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"text": "34寸显示器", "bounds": "[120,930][600,980]"},
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    *_metadata_panel_elements(selected_category="生活百科"),
                    {"text": "34寸显示器", "bounds": "[120,930][600,980]"},
                ],
            ),
        ],
        advance_on_input_indices={1, 3},
        advance_on_tap_calls={1, 2, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "metadata_panel"
    assert android_service.input_text_calls == [
        ("device-1", description),
        ("device-1", description),
    ]
    assert android_service.set_clipboard_text_calls == []
    assert android_service.long_press_calls == []
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 800, 1000),
        ("device-1", 1525, 1671),
    ]


def test_fill_description_uses_description_content_selector_before_clipboard_fallback():
    description = "34寸显示器 成色很好 北京自提"
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                        "clickable": "true",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {"content-desc": "闲鱼", "bounds": "[70,775][1525,833]"},
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1610]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "34寸显示器 成色很好 北京自提, 闲鱼",
                        "bounds": "[70,775][1525,833]",
                    },
                    {"content-desc": "完成", "bounds": "[1461,1646][1590,1696]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    *_metadata_panel_elements(selected_category="生活百科"),
                    {"text": "34寸显示器 成色很好 北京自提", "bounds": "[120,930][880,980]"},
                ],
            ),
        ],
        advance_on_input_indices={1},
        advance_on_set_text_by_description_indices={3},
        advance_on_tap_calls={1, 2, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.fill_description("device-1", description)

    assert result.screen_name == "metadata_panel"
    assert android_service.input_text_calls == [("device-1", description)]
    assert android_service.set_text_by_description_calls == [
        ("device-1", "闲鱼", description),
    ]
    assert android_service.set_clipboard_text_calls == []
    assert android_service.tap_calls == [
        ("device-1", 800, 1000),
        ("device-1", 800, 1000),
        ("device-1", 1525, 1671),
    ]


def test_advance_listing_form_to_price_panel_taps_price_entry():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "价格设置", "bounds": "[40,1258][1560,1378]"},
                    {"text": "原价设置", "bounds": "[40,1503][1560,1623]"},
                    {"text": "库存设置", "bounds": "[40,1628][1560,1748]"},
                    {"text": "1", "bounds": "[120,1961][280,2109]"},
                    {"text": "删除", "bounds": "[1320,2035][1480,2185]"},
                    {"text": "确定", "bounds": "[1320,2335][1480,2485]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_price_panel("device-1")

    assert result.screen_name == "price_panel"
    assert android_service.tap_calls == [("device-1", 800, 1705)]


def test_advance_listing_form_to_price_panel_can_start_from_metadata_panel():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_scrolled_metadata_panel_elements(selected_category="文学/小说"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "价格设置", "bounds": "[40,1258][1560,1378]"},
                    {"text": "原价设置", "bounds": "[40,1503][1560,1623]"},
                    {"text": "库存设置", "bounds": "[40,1628][1560,1748]"},
                    {"text": "删除", "bounds": "[1320,2035][1480,2185]"},
                    {"text": "确定", "bounds": "[1320,2335][1480,2485]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_price_panel("device-1")

    assert result.screen_name == "price_panel"
    assert android_service.tap_calls == [("device-1", 800, 1655)]


def test_fill_price_clears_existing_digits_taps_keypad_and_confirms():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "价格设置", "bounds": "[40,1258][1560,1378]"},
                    {"text": "原价设置", "bounds": "[40,1503][1560,1623]"},
                    {"text": "库存设置", "bounds": "[40,1628][1560,1748]"},
                    {"text": "3", "bounds": "[920,1961][1080,2109]"},
                    {"text": "9", "bounds": "[920,2261][1080,2409]"},
                    {"text": ".", "bounds": "[120,2411][280,2559]"},
                    {"text": "删除", "bounds": "[1320,2035][1480,2185]"},
                    {"text": "确定", "bounds": "[1320,2335][1480,2485]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 8},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.fill_price("device-1", "39.9", max_steps=4, max_clear_presses=2)

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 1705),
        ("device-1", 1400, 2110),
        ("device-1", 1400, 2110),
        ("device-1", 1000, 2035),
        ("device-1", 1000, 2335),
        ("device-1", 200, 2485),
        ("device-1", 1000, 2335),
        ("device-1", 1400, 2410),
    ]


def test_fill_price_accepts_metadata_panel_after_confirm():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[560,250][1040,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "价格设置", "bounds": "[40,1258][1560,1378]"},
                    {"text": "原价设置", "bounds": "[40,1503][1560,1623]"},
                    {"text": "库存设置", "bounds": "[40,1628][1560,1748]"},
                    {"text": "3", "bounds": "[920,1961][1080,2109]"},
                    {"text": "9", "bounds": "[920,2261][1080,2409]"},
                    {"text": ".", "bounds": "[120,2411][280,2559]"},
                    {"text": "删除", "bounds": "[1320,2035][1480,2185]"},
                    {"text": "确定", "bounds": "[1320,2335][1480,2485]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[560,250][1040,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "分类/ISBN码/成色￼", "bounds": "[70,1529][408,1582]"},
                    {"content-desc": "已选中生活百科, 生活百科", "bounds": "[245,1615][435,1755]"},
                    {"content-desc": "可选几乎全新, 几乎全新", "bounds": "[395,1895][585,2035]"},
                    {"content-desc": "价格设置", "bounds": "[70,2237][1530,2377]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,2517][1530,2560]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 7},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.fill_price("device-1", "39.9", max_steps=4, max_clear_presses=1)

    assert result.screen_name == "metadata_panel"
    assert android_service.tap_calls == [
        ("device-1", 800, 2307),
        ("device-1", 1400, 2110),
        ("device-1", 1000, 2035),
        ("device-1", 1000, 2335),
        ("device-1", 200, 2485),
        ("device-1", 1000, 2335),
        ("device-1", 1400, 2410),
    ]


def test_advance_listing_form_to_shipping_panel_taps_shipping_entry():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
                    {
                        "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                        "bounds": "[30,1255][1570,1893]",
                    },
                    {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
                    {"text": "买家自提", "bounds": "[30,1893][1570,2063]"},
                    {"text": "确定", "bounds": "[760,2381][840,2429]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_shipping_panel("device-1")

    assert result.screen_name == "shipping_panel"
    assert android_service.tap_calls == [("device-1", 800, 1845)]


def test_advance_listing_form_to_shipping_panel_can_start_from_metadata_panel():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_scrolled_metadata_panel_elements(selected_category="文学/小说"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
                    {
                        "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                        "bounds": "[30,1255][1570,1893]",
                    },
                    {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
                    {"text": "确定", "bounds": "[760,2381][840,2429]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.advance_listing_form_to_shipping_panel("device-1")

    assert result.screen_name == "shipping_panel"
    assert android_service.tap_calls == [("device-1", 800, 1795)]


def test_set_shipping_method_selects_no_mail_and_confirms():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
                    {
                        "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                        "bounds": "[30,1255][1570,1893]",
                    },
                    {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
                    {"text": "买家自提", "bounds": "[30,1893][1570,2063]"},
                    {"text": "确定", "bounds": "[760,2381][840,2429]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n无需邮寄", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.set_shipping_method("device-1", "无需邮寄")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 1845),
        ("device-1", 95, 1829),
        ("device-1", 800, 2405),
    ]


def test_set_shipping_method_selects_free_mail_from_multiline_panel():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n买家自提", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
                    {
                        "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                        "bounds": "[30,1255][1570,1893]",
                    },
                    {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
                    {"text": "买家自提", "bounds": "[30,1893][1570,2063]"},
                    {"text": "确定", "bounds": "[760,2381][840,2429]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_tap_calls={1, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.set_shipping_method("device-1", "包邮")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 1845),
        ("device-1", 95, 1446),
        ("device-1", 800, 2405),
    ]


def test_set_shipping_method_returns_immediately_when_value_already_matches():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.set_shipping_method("device-1", "包邮")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == []


def test_set_shipping_method_waits_until_post_confirm_tail_leaves_shipping_panel():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n无需邮寄", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
                    {
                        "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                        "bounds": "[30,1255][1570,1893]",
                    },
                    {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
                    {"text": "买家自提", "bounds": "[30,1893][1570,2063]"},
                    {"text": "确定", "bounds": "[760,2381][840,2429]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
                    {
                        "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                        "bounds": "[30,1255][1570,1893]",
                    },
                    {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
                    {"text": "买家自提", "bounds": "[30,1893][1570,2063]"},
                    {"text": "确定", "bounds": "[760,2381][840,2429]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_get_indices={2},
        advance_on_tap_calls={1, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.set_shipping_method("device-1", "包邮")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 1845),
        ("device-1", 95, 1446),
        ("device-1", 800, 2405),
    ]


def test_set_shipping_method_waits_through_status_only_unknown_overlay():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发货方式", "bounds": "[721,1161][879,1209]"},
                    {
                        "text": "邮寄\n包邮\n不包邮-按距离付费\n不包邮-固定邮费\n无需邮寄",
                        "bounds": "[30,1255][1570,1893]",
                    },
                    {"class": "android.widget.ImageView", "bounds": "[83,1436][108,1456]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1549][120,1599]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1676][120,1726]"},
                    {"class": "android.widget.ImageView", "bounds": "[70,1804][120,1854]"},
                    {"text": "买家自提", "bounds": "[30,1893][1570,2063]"},
                    {"text": "确定", "bounds": "[760,2381][840,2429]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "21:14", "bounds": "[1460,25][1560,70]"},
                    {"text": "开启护眼模式", "bounds": "[60,60][240,120]"},
                    {"text": "勿扰", "bounds": "[260,60][320,120]"},
                    {"text": "振铃器静音。", "bounds": "[340,60][520,120]"},
                    {"text": "WLAN 信号强度满格。", "bounds": "[540,60][820,120]"},
                    {"text": "正在充电，已完成百分之100。", "bounds": "[840,60][1200,120]"},
                    {"text": "100", "bounds": "[1500,120][1560,180]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n无需邮寄", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ],
        advance_on_get_indices={2},
        advance_on_tap_calls={1, 3},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _: None,
    )

    result = flow.set_shipping_method("device-1", "无需邮寄")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 800, 1845),
        ("device-1", 95, 1829),
        ("device-1", 800, 2405),
    ]


def test_set_shipping_method_rejects_unsupported_pickup_for_now():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    try:
        flow.set_shipping_method("device-1", "买家自提")
    except ValueError as exc:
        assert str(exc) == "Unsupported shipping method: '买家自提'"
    else:
        raise AssertionError("Expected unsupported 买家自提 to raise ValueError")


def test_select_cover_image_taps_first_select_then_confirm():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1179,102][1382,172]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                    {"text": "相册", "bounds": "[1620,1520][1720,1590]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1179,102][1382,172]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                    {"text": "确定", "bounds": "[1680,1320][2160,1510]"},
                    {"text": "相册", "bounds": "[1620,1520][1720,1590]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "标题", "bounds": "[180,330][320,390]"},
                    {"text": "描述一下宝贝吧", "bounds": "[180,450][620,520]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    flow.select_cover_image("device-1")

    assert android_service.tap_calls == [
        ("device-1", 1868, 260),
        ("device-1", 1920, 1415),
    ]


def test_select_cover_image_returns_latest_analysis_after_confirm():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1179,102][1382,172]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                    {"text": "相册", "bounds": "[1620,1520][1720,1590]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1179,102][1382,172]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                    {"text": "确定", "bounds": "[1680,1320][2160,1510]"},
                    {"text": "相册", "bounds": "[1620,1520][1720,1590]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "标题", "bounds": "[180,330][320,390]"},
                    {"text": "描述一下宝贝吧", "bounds": "[180,450][620,520]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.select_cover_image("device-1")

    assert result.screen_name == "unknown"
    assert result.visible_texts == ["标题", "描述一下宝贝吧"]


def test_switch_album_source_opens_source_menu_and_chooses_preferred_album():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1810,85][2030,185]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1810,85][2030,185]"},
                    {"text": "所有文件·889", "bounds": "[1600,320][2240,470]"},
                    {"text": "XianyuPublish·1", "bounds": "[1600,650][2240,800]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "选择", "bounds": "[1818,210][1918,310]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
    )

    result = flow.switch_album_source("device-1")

    assert result.screen_name == "album_picker"
    assert result.targets["album_source"].text == "XianyuPublish"
    assert android_service.tap_calls == [
        ("device-1", 1920, 135),
        ("device-1", 1920, 725),
    ]


def test_select_cover_image_can_switch_to_preferred_album_before_selecting():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1810,85][2030,185]"},
                    {"text": "选择", "bounds": "[1790,202][1947,319]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "所有文件", "bounds": "[1810,85][2030,185]"},
                    {"text": "所有文件·889", "bounds": "[1600,320][2240,470]"},
                    {"text": "XianyuPublish·1", "bounds": "[1600,650][2240,800]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "选择", "bounds": "[1818,210][1918,310]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "预览 (1)", "bounds": "[2385,118][2530,165]"},
                    {"text": "确定", "bounds": "[1620,1365][2220,1465]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "1张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "照片模糊未识别到宝贝\n删除", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
    )

    result = flow.select_cover_image("device-1", preferred_album_name="XianyuPublish")

    assert result.screen_name == "photo_analysis"
    assert android_service.tap_calls == [
        ("device-1", 1920, 135),
        ("device-1", 1920, 725),
        ("device-1", 1868, 260),
        ("device-1", 1920, 1415),
    ]


def test_select_cover_image_waits_for_photo_analysis_after_blank_loading_screen():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "选择", "bounds": "[1818,210][1918,310]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "预览 (1)", "bounds": "[2385,118][2530,165]"},
                    {"text": "确定", "bounds": "[1620,1365][2220,1465]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "10:53", "bounds": "[86,14][180,66]"},
                    {"text": "100", "bounds": "[2391,20][2445,58]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "1张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "照片模糊未识别到宝贝\n删除", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
        ],
        advance_on_get_indices={2},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.select_cover_image("device-1")

    assert result.screen_name == "photo_analysis"
    assert result.visible_texts[-1] == "照片模糊未识别到宝贝\n删除"


def test_select_cover_image_taps_next_step_from_selected_media_preview():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "XianyuPublish", "bounds": "[633,85][968,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "XianyuPublish", "bounds": "[633,85][968,185]"},
                    {"content-desc": "预览 (1)", "bounds": "[670,2380][930,2520]"},
                    {"content-desc": "确定", "bounds": "[1340,2380][1560,2520]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "关闭", "bounds": "[15,88][115,188]", "clickable": "true"},
                    {"text": "XianyuPublish", "bounds": "[633,85][968,185]", "clickable": "true"},
                    {"text": "查看大图", "bounds": "[401,210][798,606]", "clickable": "true"},
                    {"text": "取消选择, 1", "bounds": "[698,210][798,310]", "clickable": "true"},
                    {"text": "删除图片", "bounds": "[40,2380][190,2520]", "clickable": "true"},
                    {"text": "下一步 (1)", "bounds": "[1340,2380][1560,2520]", "clickable": "true"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "1张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "照片模糊未识别到宝贝\n删除", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.select_cover_image("device-1")

    assert result.screen_name == "photo_analysis"
    assert android_service.tap_calls == [
        ("device-1", 748, 260),
        ("device-1", 1450, 2450),
        ("device-1", 1450, 2450),
    ]


def test_select_cover_image_taps_next_step_when_preview_appears_without_confirm_step():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "XianyuPublish", "bounds": "[633,85][968,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "关闭", "bounds": "[15,88][115,188]", "clickable": "true"},
                    {"text": "XianyuPublish", "bounds": "[633,85][968,185]", "clickable": "true"},
                    {"text": "查看大图", "bounds": "[401,210][798,606]", "clickable": "true"},
                    {"text": "取消选择, 1", "bounds": "[698,210][798,310]", "clickable": "true"},
                    {"text": "删除图片", "bounds": "[40,2380][190,2520]", "clickable": "true"},
                    {"text": "下一步 (1)", "bounds": "[1340,2380][1560,2520]", "clickable": "true"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "1张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "照片模糊未识别到宝贝\n删除", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.select_cover_image("device-1")

    assert result.screen_name == "photo_analysis"
    assert android_service.tap_calls == [
        ("device-1", 748, 260),
        ("device-1", 1450, 2450),
    ]


def test_select_cover_image_taps_done_on_media_edit_screen_and_returns_listing_form():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "XianyuPublish", "bounds": "[633,85][968,185]"},
                    {"content-desc": "选择", "bounds": "[698,210][798,310]"},
                    {"content-desc": "相册\nTab 1 of 3", "bounds": "[525,2440][695,2560]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "关闭", "bounds": "[15,88][115,188]", "clickable": "true"},
                    {"text": "XianyuPublish", "bounds": "[633,85][968,185]", "clickable": "true"},
                    {"text": "查看大图", "bounds": "[401,210][798,606]", "clickable": "true"},
                    {"text": "取消选择, 1", "bounds": "[698,210][798,310]", "clickable": "true"},
                    {"text": "删除图片", "bounds": "[40,2380][190,2520]", "clickable": "true"},
                    {"text": "下一步 (1)", "bounds": "[1340,2380][1560,2520]", "clickable": "true"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "1/1", "bounds": "[0,0][1600,2560]"},
                    {"text": "点击添加标签", "bounds": "[0,190][1600,2135]", "clickable": "true"},
                    {"text": "裁剪", "bounds": "[50,2175][300,2315]", "clickable": "true"},
                    {"text": "背景模糊", "bounds": "[1300,2175][1550,2315]", "clickable": "true"},
                    {"text": "完成", "bounds": "[1300,2410][1520,2490]", "clickable": "true"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"content-desc": "关闭", "bounds": "[0,105][90,165]"},
                    {"content-desc": "发闲置", "bounds": "[90,104][255,166]"},
                    {"content-desc": "发布, 发布", "bounds": "[1410,95][1600,175]"},
                    {"content-desc": "添加图片", "bounds": "[70,250][550,730]"},
                    {
                        "content-desc": "描述, 描述一下宝贝的品牌型号、货品来源…",
                        "bounds": "[30,737][1570,1264]",
                    },
                    {"content-desc": "价格设置", "bounds": "[70,1635][1530,1775]"},
                    {"content-desc": "发货方式\n包邮", "bounds": "[70,1775][1530,1915]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
    )

    result = flow.select_cover_image("device-1")

    assert result.screen_name == "listing_form"
    assert android_service.tap_calls == [
        ("device-1", 748, 260),
        ("device-1", 1450, 2450),
        ("device-1", 1410, 2450),
    ]


def test_select_cover_image_waits_for_confirm_button_before_confirming():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "选择", "bounds": "[1818,210][1918,310]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "10:53", "bounds": "[86,14][180,66]"},
                    {"text": "100", "bounds": "[2391,20][2445,58]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "预览 (1)", "bounds": "[2385,118][2530,165]"},
                    {"text": "确定", "bounds": "[1620,1365][2220,1465]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "1张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "照片模糊未识别到宝贝\n删除", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
        ],
        advance_on_get_indices={1},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.select_cover_image("device-1")

    assert result.screen_name == "photo_analysis"
    assert android_service.tap_calls == [
        ("device-1", 1868, 260),
        ("device-1", 1920, 1415),
    ]


def test_select_cover_image_waits_until_album_picker_tail_transitions_to_photo_analysis():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "选择", "bounds": "[1818,210][1918,310]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "预览 (1)", "bounds": "[2385,118][2530,165]"},
                    {"text": "确定", "bounds": "[1620,1365][2220,1465]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "预览 (1)", "bounds": "[2385,118][2530,165]"},
                    {"text": "确定", "bounds": "[1620,1365][2220,1465]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "2张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "照片模糊未识别到宝贝\n删除", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
        ],
        advance_on_get_indices={2},
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.select_cover_image("device-1")

    assert result.screen_name == "photo_analysis"
    assert android_service.tap_calls == [
        ("device-1", 1868, 260),
        ("device-1", 1920, 1415),
    ]


def test_select_cover_image_raises_when_post_confirm_flow_never_leaves_album_picker():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "选择", "bounds": "[1818,210][1918,310]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "预览 (1)", "bounds": "[2385,118][2530,165]"},
                    {"text": "确定", "bounds": "[1620,1365][2220,1465]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "XianyuPublish", "bounds": "[1753,85][2088,185]"},
                    {"text": "预览 (1)", "bounds": "[2385,118][2530,165]"},
                    {"text": "确定", "bounds": "[1620,1365][2220,1465]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    try:
        flow.select_cover_image("device-1")
    except RuntimeError as exc:
        assert str(exc) == "Post-confirm flow did not leave album picker within 6 polls"
    else:
        raise AssertionError("Expected select_cover_image() to raise for a stuck album picker")


def test_advance_photo_analysis_to_publish_chooser_dismisses_overlay_and_taps_space_publish():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝", "bounds": "[1295,229][1453,324]", "clickable": "true"},
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "2张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {
                        "text": (
                            "价格计算中 预计需要2分钟\n"
                            "宝贝价格是根据市场行情计算得出，完成后通知你"
                        ),
                        "bounds": "[1280,681][2560,1600]",
                    },
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝", "bounds": "[1295,229][1453,324]", "clickable": "true"},
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "2张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "¥40~60", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "text": "南朝笑不可支的川谷\n发宝贝\n投缘优惠",
                        "bounds": "[1280,0][2560,1600]",
                    },
                    {"text": "宝贝", "bounds": "[1295,229][1453,324]", "clickable": "true"},
                    {"text": "这里空空如也～", "bounds": "[1789,881][2051,941]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.advance_photo_analysis_to_publish_chooser("device-1")

    assert result.screen_name == "publish_chooser"
    assert android_service.tap_calls == [
        ("device-1", 1920, 1510),
        ("device-1", 1374, 276),
        ("device-1", 1740, 1495),
    ]


def test_advance_photo_analysis_to_publish_chooser_returns_existing_publish_chooser():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.advance_photo_analysis_to_publish_chooser("device-1")

    assert result.screen_name == "publish_chooser"
    assert android_service.tap_calls == []


def test_advance_photo_analysis_to_publish_chooser_can_start_from_unknown_xianyu_overlay():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "南朝笑不可支的川谷", "bounds": "[1280,0][2560,1600]"},
                    {"text": "编辑", "bounds": "[2280,210][2380,280]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝", "bounds": "[1295,229][1453,324]", "clickable": "true"},
                    {"text": "宝贝价格是根据市场行情计算得出", "bounds": "[1320,541][1733,569]"},
                    {"text": "2张照片", "bounds": "[1360,607][1460,635]"},
                    {"text": "添加", "bounds": "[2268,537][2328,567]"},
                    {"text": "¥40~60", "bounds": "[1280,681][2560,1600]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "text": "南朝笑不可支的川谷\n发宝贝\n投缘优惠",
                        "bounds": "[1280,0][2560,1600]",
                    },
                    {"text": "宝贝", "bounds": "[1295,229][1453,324]", "clickable": "true"},
                    {"text": "这里空空如也～", "bounds": "[1789,881][2051,941]"},
                ],
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "content-desc": "发闲置\n自己拍图卖·啥都能换钱",
                        "bounds": "[1280,650][2560,873]",
                        "clickable": "true",
                    },
                    {
                        "content-desc": "关闭",
                        "bounds": "[1280,1470][2560,1600]",
                        "clickable": "true",
                    },
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(preferred_album_name="XianyuPublish"),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.advance_photo_analysis_to_publish_chooser("device-1")

    assert result.screen_name == "publish_chooser"
    assert android_service.tap_calls == [
        ("device-1", 1920, 1510),
        ("device-1", 1374, 276),
        ("device-1", 1740, 1495),
    ]


def test_submit_listing_and_wait_for_result_taps_submit_and_returns_success_screen():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝发布成功", "bounds": "[520,410][1080,490]"},
                    {"text": "分享给更多人", "bounds": "[600,560][1000,620]"},
                    {"text": "看看宝贝", "clickable": "true", "bounds": "[220,1960][760,2090]"},
                    {"text": "继续发布", "clickable": "true", "bounds": "[840,1960][1380,2090]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.submit_listing_and_wait_for_result("device-1")

    assert result.screen_name == "publish_success"
    assert android_service.tap_calls == [("device-1", 1505, 135)]


def test_submit_listing_and_wait_for_result_accepts_reward_success_variant():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "发布成功", "bounds": "[698,1303][1000,1381]"},
                    {"text": "100闲鱼币", "bounds": "[763,1432][1048,1505]"},
                    {"text": "点击领取", "bounds": "[1159,1432][1399,1505]"},
                    {"text": "再发一件", "bounds": "[663,2340][938,2422]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.submit_listing_and_wait_for_result("device-1")

    assert result.screen_name == "publish_success"
    assert result.targets["publish_success_continue"].text == "再发一件"
    assert android_service.tap_calls == [("device-1", 1505, 135)]


def test_submit_listing_and_wait_for_result_raises_when_success_screen_never_appears():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    with pytest.raises(RuntimeError, match="Publish did not reach success screen"):
        flow.submit_listing_and_wait_for_result("device-1")


def test_submit_listing_and_wait_for_result_surfaces_location_required_dialog_reason():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=_metadata_panel_elements(selected_category="生活百科"),
            ),
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {
                        "text": (
                            "无法发布宝贝\n"
                            "系统无法定位您所在的行政区，请点击宝贝图片下方位置图标，手动选择行政区。"
                        ),
                        "bounds": "[250,980][1350,1380]",
                    },
                    {"text": "取消", "clickable": "true", "bounds": "[300,1510][700,1610]"},
                    {"text": "我知道了", "clickable": "true", "bounds": "[900,1510][1300,1610]"},
                ],
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    with pytest.raises(
        RuntimeError,
        match="系统无法定位您所在的行政区",
    ):
        flow.submit_listing_and_wait_for_result("device-1")


def test_advance_publish_success_to_listing_detail_taps_view_listing_when_available():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostActivity",
                elements=[
                    {"text": "宝贝发布成功", "bounds": "[520,410][1080,490]"},
                    {"text": "分享给更多人", "bounds": "[600,560][1000,620]"},
                    {"text": "看看宝贝", "clickable": "true", "bounds": "[220,1960][760,2090]"},
                    {"text": "继续发布", "clickable": "true", "bounds": "[840,1960][1380,2090]"},
                ],
            ),
            _make_screen(
                activity="com.taobao.idlefish.detail.DetailActivity",
                elements=_listing_detail_elements(),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.advance_publish_success_to_listing_detail("device-1")

    assert result.screen_name == "listing_detail"
    assert android_service.tap_calls == [("device-1", 490, 2025)]
    assert android_service.back_calls == []


def test_advance_publish_success_to_listing_detail_presses_back_for_reward_variant():
    android_service = FakeAndroidService(
        screens=[
            _make_screen(
                activity="com.idlefish.flutterbridge.flutterboost.boost.FishFlutterBoostTransparencyActivity",
                elements=[
                    {"text": "发布成功", "bounds": "[698,1303][1000,1381]"},
                    {"text": "100闲鱼币", "bounds": "[763,1432][1048,1505]"},
                    {"text": "点击领取", "bounds": "[1159,1432][1399,1505]"},
                    {"text": "再发一件", "bounds": "[663,2340][938,2422]"},
                ],
            ),
            _make_screen(
                activity="com.taobao.idlefish.detail.DetailActivity",
                elements=_listing_detail_elements(),
            ),
        ]
    )
    flow = XianyuPublishFlowService(
        settings=XianyuPublishSettings(),
        android_service=android_service,
        sleep_fn=lambda _seconds: None,
    )

    result = flow.advance_publish_success_to_listing_detail("device-1")

    assert result.screen_name == "listing_detail"
    assert android_service.tap_calls == []
    assert android_service.back_calls == ["device-1"]
