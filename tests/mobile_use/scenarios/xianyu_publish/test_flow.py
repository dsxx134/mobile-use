from unittest.mock import Mock
from unittest.mock import call

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
    def __init__(self, screens: list[dict], advance_on_get_indices: set[int] | None = None):
        self._screens = screens
        self._index = 0
        self._advance_on_get_indices = advance_on_get_indices or set()
        self.device = Mock()
        self.tap_calls: list[tuple[str, int, int]] = []

    def get_current_app(self, serial: str) -> dict:
        return self._screens[self._index]["current_app"]

    def get_screen_data(self, serial: str) -> dict:
        screen = self._screens[self._index]
        if self._index in self._advance_on_get_indices and self._index < len(self._screens) - 1:
            self._index += 1
        return screen

    def tap(self, serial: str, x: int, y: int, long_press: bool = False) -> dict:
        self.tap_calls.append((serial, x, y))
        if self._index < len(self._screens) - 1:
            self._index += 1
        return {"serial": serial, "x": x, "y": y, "success": True, "long_press": long_press}

    def get_device(self, serial: str) -> Mock:
        return self.device


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
