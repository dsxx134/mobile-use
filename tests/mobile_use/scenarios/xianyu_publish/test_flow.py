from minitap.mobile_use.scenarios.xianyu_publish.flow import XianyuFlowAnalyzer


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
