from unittest.mock import patch

import pytest

from minitap.mobile_use.mcp.android_debug_mcp import (
    android_debug_get_current_app,
    android_debug_tap,
    mcp,
)
from minitap.mobile_use.mcp.android_debug_models import DeviceSelector, TapInput


@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_current_app_tool_returns_service_data(mock_service):
    mock_service.get_current_app.return_value = {
        "serial": "device-1",
        "package": "com.taobao.idlefish",
        "activity": ".maincontainer.activity.MainActivity",
        "raw_output": "raw",
    }

    result = await android_debug_get_current_app(DeviceSelector(serial="device-1"))

    assert result.package == "com.taobao.idlefish"
    assert result.activity == ".maincontainer.activity.MainActivity"


@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_tap_tool_delegates_to_service(mock_service):
    mock_service.tap.return_value = {
        "serial": "device-1",
        "x": 10,
        "y": 20,
        "long_press": False,
        "long_press_duration_ms": 1000,
        "success": True,
    }

    await android_debug_tap(TapInput(serial="device-1", x=10, y=20))

    mock_service.tap.assert_called_once_with(
        "device-1",
        x=10,
        y=20,
        long_press=False,
        long_press_duration_ms=1000,
    )


@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_current_app_tool_surfaces_serial_validation_errors(mock_service):
    mock_service.get_current_app.side_effect = ValueError("Unknown Android device serial: missing")

    with pytest.raises(ValueError, match="Unknown Android device serial: missing"):
        await android_debug_get_current_app(DeviceSelector(serial="missing"))


def test_current_app_tool_has_structured_output_schema():
    tool = mcp._tool_manager._tools["android_debug_get_current_app"]

    assert tool.output_schema is not None
    assert tool.output_schema["type"] == "object"
    assert "package" in tool.output_schema["properties"]
