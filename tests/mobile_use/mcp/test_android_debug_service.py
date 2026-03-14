from unittest.mock import Mock

import pytest

from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService


def _make_device_info(serial: str = "device-1", state: str = "device") -> Mock:
    device_info = Mock()
    device_info.serial = serial
    device_info.state = state
    return device_info


def test_get_ui_client_reuses_cached_client():
    adb_client = Mock()
    adb_client.list.return_value = [_make_device_info()]
    ui_client = Mock()
    ui_client_factory = Mock(return_value=ui_client)
    service = AndroidDebugService(adb_client=adb_client, ui_client_factory=ui_client_factory)

    first = service.get_ui_client("device-1")
    second = service.get_ui_client("device-1")

    assert first is second
    assert service._ui_client_factory.call_count == 1


def test_validate_serial_raises_for_missing_device():
    adb_client = Mock()
    adb_client.list.return_value = []
    service = AndroidDebugService(adb_client=adb_client, ui_client_factory=Mock())

    with pytest.raises(ValueError, match="Unknown Android device serial"):
        service.validate_serial("missing-device")


def test_get_current_app_returns_package_and_activity():
    adb_client = Mock()
    adb_client.list.return_value = [_make_device_info()]
    device = Mock()
    device.shell.return_value = (
        "mCurrentFocus=Window{b87d8d3 u0 "
        "com.taobao.idlefish/.maincontainer.activity.MainActivity}"
    )
    adb_client.device.return_value = device
    service = AndroidDebugService(adb_client=adb_client, ui_client_factory=Mock())

    result = service.get_current_app("device-1")

    assert result["package"] == "com.taobao.idlefish"
    assert result["activity"] == ".maincontainer.activity.MainActivity"
    device.shell.assert_called_once_with("dumpsys window | grep mCurrentFocus")


def test_push_media_uses_device_sync_push(tmp_path):
    adb_client = Mock()
    adb_client.list.return_value = [_make_device_info()]
    device = Mock()
    adb_client.device.return_value = device
    service = AndroidDebugService(adb_client=adb_client, ui_client_factory=Mock())
    local_file = tmp_path / "item.jpg"
    local_file.write_bytes(b"1234")

    result = service.push_media_to_device(
        "device-1",
        local_path=str(local_file),
        remote_path="/sdcard/DCIM/item.jpg",
    )

    device.sync.push.assert_called_once_with(str(local_file.resolve()), "/sdcard/DCIM/item.jpg")
    device.shell.assert_called_once_with(
        'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE '
        '-d "file:///sdcard/DCIM/item.jpg"'
    )
    assert result["file_size_bytes"] == 4


def test_set_focused_text_uses_ui_client_helper():
    adb_client = Mock()
    adb_client.list.return_value = [_make_device_info()]
    ui_client = Mock()
    ui_client_factory = Mock(return_value=ui_client)
    service = AndroidDebugService(adb_client=adb_client, ui_client_factory=ui_client_factory)

    result = service.set_focused_text("device-1", "上海虹桥站")

    ui_client.set_focused_text.assert_called_once_with("上海虹桥站")
    assert result == {"serial": "device-1", "text": "上海虹桥站", "success": True}
