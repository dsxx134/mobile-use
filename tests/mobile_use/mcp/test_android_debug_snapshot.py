from unittest.mock import patch

import pytest

from minitap.mobile_use.mcp.android_debug_mcp import android_debug_get_screen_data, mcp
from minitap.mobile_use.mcp.android_debug_models import DeviceSelector


@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_screen_data_tool_returns_app_and_debug_snapshot_fields(mock_service):
    mock_service.get_screen_data.return_value = {
        "serial": "device-1",
        "platform": "android",
        "current_app": {
            "serial": "device-1",
            "package": "com.taobao.idlefish",
            "activity": ".maincontainer.activity.MainActivity",
            "raw_output": "raw",
        },
        "width": 2560,
        "height": 1600,
        "base64": "abc123",
        "elements": [],
        "element_count": 0,
        "hierarchy_xml": "<hierarchy />",
    }

    result = await android_debug_get_screen_data(DeviceSelector(serial="device-1"))

    assert result.platform == "android"
    assert result.width == 2560
    assert result.current_app.package == "com.taobao.idlefish"
    assert result.element_count == 0
    assert result.hierarchy_xml == "<hierarchy />"


def test_screen_data_tool_has_structured_snapshot_schema():
    tool = mcp._tool_manager._tools["android_debug_get_screen_data"]

    assert tool.output_schema is not None
    properties = tool.output_schema["properties"]
    assert "hierarchy_xml" in properties
    assert "element_count" in properties
