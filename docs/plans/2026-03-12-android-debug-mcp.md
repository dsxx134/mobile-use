# Android Debug MCP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local MCP server for Android debugging that exposes the same device-reading and device-control capabilities we need for Xianyu publishing automation.

**Architecture:** Add a Python FastMCP server inside this repo that wraps the existing Android stack instead of introducing a second execution stack. The server should reuse `adbutils`, `UIAutomatorClient`, and `AndroidDeviceController`-style behavior so debugging and production automation observe the same device semantics.

**Tech Stack:** Python 3.12, FastMCP (`mcp`), Pydantic v2, adbutils, uiautomator2, existing `minitap.mobile_use` controllers/clients, pytest.

---

### Task 1: Add package surface for the MCP server

**Files:**
- Modify: `pyproject.toml`
- Create: `minitap/mobile_use/mcp/__init__.py`
- Create: `minitap/mobile_use/mcp/android_debug_models.py`
- Create: `minitap/mobile_use/mcp/android_debug_service.py`
- Create: `minitap/mobile_use/mcp/android_debug_mcp.py`

**Step 1: Add the direct runtime dependency and CLI script**

Update `pyproject.toml`:

```toml
dependencies = [
    # existing deps...
    "mcp>=1.26.0",
]

[project.scripts]
mobile-use = "minitap.mobile_use.main:cli"
mobile-use-android-debug-mcp = "minitap.mobile_use.mcp.android_debug_mcp:main"
```

**Step 2: Add the package namespace**

Create `minitap/mobile_use/mcp/__init__.py`:

```python
"""MCP servers and helpers for mobile-use."""
```

**Step 3: Define input/output models**

Create `minitap/mobile_use/mcp/android_debug_models.py` with focused Pydantic models:

```python
class DeviceSelector(BaseModel):
    serial: str = Field(..., min_length=1, description="ADB serial for the Android device")


class TapInput(DeviceSelector):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    long_press: bool = False
    long_press_duration_ms: int = Field(default=1000, ge=1, le=10000)
```

Add similar small models for:
- `SwipeInput`
- `InputTextInput`
- `LaunchAppInput`
- `PushMediaInput`
- `ScreenshotInput`
- `HierarchyInput`

**Step 4: Build a reusable service class**

Create `minitap/mobile_use/mcp/android_debug_service.py` with:

```python
class AndroidDebugService:
    def __init__(self) -> None:
        self._adb = AdbClient()
        self._ui_clients: dict[str, UIAutomatorClient] = {}

    def get_ui_client(self, serial: str) -> UIAutomatorClient:
        ...

    def get_screen_data(self, serial: str) -> dict:
        ...
```

This class should:
- validate that `serial` is present in `adb list`
- cache `UIAutomatorClient` per serial
- expose simple methods for screenshot, hierarchy, current app, tap, swipe, input text, launch app, home/back, and file push

**Step 5: Create the FastMCP server**

Create `minitap/mobile_use/mcp/android_debug_mcp.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("android_debug_mcp")
service = AndroidDebugService()
```

Register tools with clear names:
- `android_debug_list_devices`
- `android_debug_get_current_app`
- `android_debug_get_screen_data`
- `android_debug_dump_ui_hierarchy`
- `android_debug_tap`
- `android_debug_swipe`
- `android_debug_input_text`
- `android_debug_launch_app`
- `android_debug_press_back`
- `android_debug_press_home`
- `android_debug_push_media_to_device`

Add:

```python
def main() -> None:
    mcp.run()
```

**Step 6: Verify import path**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run python -c "from minitap.mobile_use.mcp.android_debug_mcp import mcp; print(mcp.name)"
```

Expected: prints `android_debug_mcp`

**Step 7: Commit**

```powershell
git add pyproject.toml minitap/mobile_use/mcp
git commit -m "feat: add android debug mcp server scaffold"
```

### Task 2: TDD the service layer against fake device dependencies

**Files:**
- Create: `tests/mobile_use/mcp/test_android_debug_service.py`
- Modify: `minitap/mobile_use/mcp/android_debug_service.py`

**Step 1: Write the failing tests**

Create `tests/mobile_use/mcp/test_android_debug_service.py`:

```python
from unittest.mock import Mock

import pytest

from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService


def test_get_ui_client_reuses_cached_client():
    service = AndroidDebugService(adb_client=Mock(), ui_client_factory=Mock())
    service.get_ui_client("device-1")
    service.get_ui_client("device-1")
    assert service._ui_client_factory.call_count == 1


def test_validate_serial_raises_for_missing_device():
    adb_client = Mock()
    adb_client.list.return_value = []
    service = AndroidDebugService(adb_client=adb_client, ui_client_factory=Mock())

    with pytest.raises(ValueError, match="Unknown Android device serial"):
        service.validate_serial("missing-device")
```

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/mcp/test_android_debug_service.py -v
```

Expected: FAIL because the module or constructor behavior does not exist yet.

**Step 3: Write minimal implementation**

Update `AndroidDebugService` to support dependency injection:

```python
def __init__(self, adb_client: AdbClient | None = None, ui_client_factory: Callable[[str], UIAutomatorClient] | None = None):
    self._adb = adb_client or AdbClient()
    self._ui_client_factory = ui_client_factory or UIAutomatorClient
    self._ui_clients = {}
```

Add:

```python
def validate_serial(self, serial: str) -> None:
    ...
```

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Add the next failing tests**

Extend the same test file with:

```python
def test_get_current_app_returns_package_and_activity():
    ...


def test_push_media_uses_device_sync_push():
    ...
```

Mock only the `adbutils` device object and verify the service returns structured results.

**Step 6: Re-run targeted tests**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/mcp/test_android_debug_service.py -v
```

Expected: PASS.

**Step 7: Commit**

```powershell
git add tests/mobile_use/mcp/test_android_debug_service.py minitap/mobile_use/mcp/android_debug_service.py
git commit -m "test: cover android debug service behavior"
```

### Task 3: TDD the FastMCP tool wrappers

**Files:**
- Create: `tests/mobile_use/mcp/test_android_debug_mcp.py`
- Modify: `minitap/mobile_use/mcp/android_debug_mcp.py`

**Step 1: Write the failing tests**

Create `tests/mobile_use/mcp/test_android_debug_mcp.py`:

```python
from unittest.mock import Mock, patch

import pytest

from minitap.mobile_use.mcp.android_debug_models import DeviceSelector, TapInput
from minitap.mobile_use.mcp.android_debug_mcp import (
    android_debug_get_current_app,
    android_debug_tap,
)


@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_current_app_tool_returns_service_data(mock_service):
    mock_service.get_current_app.return_value = {"package": "com.taobao.idlefish"}
    result = await android_debug_get_current_app(DeviceSelector(serial="device-1"))
    assert result["package"] == "com.taobao.idlefish"


@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_tap_tool_delegates_to_service(mock_service):
    await android_debug_tap(TapInput(serial="device-1", x=10, y=20))
    mock_service.tap.assert_called_once()
```

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/mcp/test_android_debug_mcp.py -v
```

Expected: FAIL because the named tool functions are not exposed yet.

**Step 3: Implement minimal tool wrappers**

Expose the tool functions directly:

```python
@mcp.tool(name="android_debug_get_current_app", annotations={...})
async def android_debug_get_current_app(params: DeviceSelector) -> dict:
    return service.get_current_app(params.serial)
```

Repeat for tap/swipe/input/home/back/launch app/screenshot/hierarchy.

**Step 4: Re-run the tool tests**

Expect PASS.

**Step 5: Add one failure-path test**

Add:

```python
@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_current_app_tool_surfaces_serial_validation_errors(mock_service):
    mock_service.get_current_app.side_effect = ValueError("Unknown Android device serial: missing")
    with pytest.raises(ValueError):
        await android_debug_get_current_app(DeviceSelector(serial="missing"))
```

**Step 6: Re-run targeted tests**

Expected: PASS.

**Step 7: Commit**

```powershell
git add tests/mobile_use/mcp/test_android_debug_mcp.py minitap/mobile_use/mcp/android_debug_mcp.py
git commit -m "feat: expose android debug tools through fastmcp"
```

### Task 4: Add device snapshot and debugging ergonomics

**Files:**
- Modify: `minitap/mobile_use/mcp/android_debug_service.py`
- Modify: `minitap/mobile_use/mcp/android_debug_models.py`
- Modify: `minitap/mobile_use/mcp/android_debug_mcp.py`
- Create: `tests/mobile_use/mcp/test_android_debug_snapshot.py`

**Step 1: Write the failing snapshot test**

Create `tests/mobile_use/mcp/test_android_debug_snapshot.py`:

```python
from unittest.mock import Mock, patch

import pytest

from minitap.mobile_use.mcp.android_debug_models import DeviceSelector
from minitap.mobile_use.mcp.android_debug_mcp import android_debug_get_screen_data


@pytest.mark.asyncio
@patch("minitap.mobile_use.mcp.android_debug_mcp.service")
async def test_screen_data_tool_returns_app_and_dimensions(mock_service):
    mock_service.get_screen_data.return_value = {
        "platform": "android",
        "width": 2560,
        "height": 1600,
        "elements": [],
    }
    result = await android_debug_get_screen_data(DeviceSelector(serial="device-1"))
    assert result["platform"] == "android"
    assert result["width"] == 2560
```

**Step 2: Run to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/mcp/test_android_debug_snapshot.py -v
```

Expected: FAIL if the tool is not yet returning the structured snapshot shape.

**Step 3: Implement consistent snapshot formatting**

Return a stable dict from the service:

```python
{
    "serial": serial,
    "platform": "android",
    "current_app": current_app,
    "width": width,
    "height": height,
    "base64": "...",
    "elements": [...],
}
```

**Step 4: Re-run the snapshot test**

Expected: PASS.

**Step 5: Commit**

```powershell
git add tests/mobile_use/mcp/test_android_debug_snapshot.py minitap/mobile_use/mcp
git commit -m "feat: add structured device snapshot tool"
```

### Task 5: Document and verify the server end-to-end

**Files:**
- Create: `scripts/android_debug_mcp_smoke.py`
- Modify: `README.md`

**Step 1: Add a smoke script**

Create `scripts/android_debug_mcp_smoke.py`:

```python
from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService


def main() -> None:
    service = AndroidDebugService()
    devices = service.list_devices()
    print({"count": len(devices), "devices": devices})


if __name__ == "__main__":
    main()
```

**Step 2: Add README section**

Document:
- required local tools: `adb`, Android device, optional `scrcpy`, optional `uiautodev`
- start command:

```powershell
mobile-use-android-debug-mcp
```

- intended use for Xianyu and Android debugging

**Step 3: Verify syntax and tests**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/mcp -v
uv run ruff check
uv run python scripts/android_debug_mcp_smoke.py
uv run python -m compileall minitap/mobile_use/mcp
```

Expected:
- new MCP tests pass
- `ruff check` passes
- smoke script prints at least one connected device
- compileall succeeds

**Step 4: Commit**

```powershell
git add scripts/android_debug_mcp_smoke.py README.md
git commit -m "docs: add android debug mcp usage notes"
```
