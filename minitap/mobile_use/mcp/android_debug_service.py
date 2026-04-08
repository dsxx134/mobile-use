import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from adbutils import AdbClient, AdbDevice

from minitap.mobile_use.clients.ui_automator_client import UIAutomatorClient

_CURRENT_APP_RE = re.compile(r"(?P<package>[A-Za-z0-9._]+)/(?P<activity>[A-Za-z0-9.$_]+)")


class AndroidDebugService:
    def __init__(
        self,
        adb_client: AdbClient | None = None,
        ui_client_factory: Callable[[str], UIAutomatorClient] | None = None,
    ) -> None:
        self._adb = adb_client or AdbClient()
        self._ui_client_factory = ui_client_factory or UIAutomatorClient
        self._ui_clients: dict[str, UIAutomatorClient] = {}

    def list_devices(self) -> list[dict[str, Any]]:
        devices = []
        for device in self._adb.list():
            devices.append(
                {
                    "serial": getattr(device, "serial", None),
                    "state": getattr(device, "state", "device"),
                }
            )
        return devices

    def validate_serial(self, serial: str) -> None:
        known_serials = {device["serial"] for device in self.list_devices()}
        if serial not in known_serials:
            raise ValueError(f"Unknown Android device serial: {serial}")

    def get_device(self, serial: str) -> AdbDevice:
        self.validate_serial(serial)
        return self._adb.device(serial=serial)

    def get_ui_client(self, serial: str) -> UIAutomatorClient:
        self.validate_serial(serial)
        if serial not in self._ui_clients:
            self._ui_clients[serial] = self._ui_client_factory(serial)
        return self._ui_clients[serial]

    def _parse_current_app(self, output: str) -> dict[str, str | None]:
        match = _CURRENT_APP_RE.search(output)
        if match is None:
            return {"package": None, "activity": None}
        return {
            "package": match.group("package"),
            "activity": match.group("activity"),
        }

    def get_current_app(self, serial: str) -> dict[str, Any]:
        device = self.get_device(serial)
        raw_output = str(device.shell("dumpsys window | grep mCurrentFocus")).strip()
        parsed = self._parse_current_app(raw_output)
        return {
            "serial": serial,
            "package": parsed["package"],
            "activity": parsed["activity"],
            "raw_output": raw_output,
        }

    def get_screen_data(self, serial: str) -> dict[str, Any]:
        ui_data = self.get_ui_client(serial).get_screen_data()
        return {
            "serial": serial,
            "platform": "android",
            "current_app": self.get_current_app(serial),
            "width": ui_data.width,
            "height": ui_data.height,
            "base64": ui_data.base64,
            "hierarchy_xml": ui_data.hierarchy_xml,
            "elements": ui_data.elements,
            "element_count": len(ui_data.elements),
        }

    def dump_ui_hierarchy(self, serial: str) -> dict[str, Any]:
        return {
            "serial": serial,
            "hierarchy_xml": self.get_ui_client(serial).get_hierarchy(),
        }

    def dump_activity_activities(self, serial: str) -> dict[str, Any]:
        device = self.get_device(serial)
        return {
            "serial": serial,
            "raw_output": str(device.shell("dumpsys activity activities")),
        }

    def tap(
        self,
        serial: str,
        x: int,
        y: int,
        long_press: bool = False,
        long_press_duration_ms: int = 1000,
    ) -> dict[str, Any]:
        device = self.get_device(serial)
        if long_press:
            device.shell(f"input swipe {x} {y} {x} {y} {long_press_duration_ms}")
        else:
            device.shell(f"input tap {x} {y}")
        return {
            "serial": serial,
            "x": x,
            "y": y,
            "long_press": long_press,
            "long_press_duration_ms": long_press_duration_ms,
            "success": True,
        }

    def swipe(
        self,
        serial: str,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 400,
    ) -> dict[str, Any]:
        device = self.get_device(serial)
        device.shell(f"input touchscreen swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}")
        return {
            "serial": serial,
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "duration_ms": duration_ms,
            "success": True,
        }

    def input_text(self, serial: str, text: str) -> dict[str, Any]:
        self.get_ui_client(serial).send_text(text)
        return {"serial": serial, "text": text, "success": True}

    def set_focused_text(self, serial: str, text: str) -> dict[str, Any]:
        self.get_ui_client(serial).set_focused_text(text)
        return {"serial": serial, "text": text, "success": True}

    def set_clipboard_text(self, serial: str, text: str) -> dict[str, Any]:
        self.get_ui_client(serial).set_clipboard_text(text)
        return {"serial": serial, "text": text, "success": True}

    def get_clipboard_text(self, serial: str) -> dict[str, Any]:
        return {
            "serial": serial,
            "text": self.get_ui_client(serial).get_clipboard_text(),
        }

    def set_text_by_description(self, serial: str, description: str, text: str) -> dict[str, Any]:
        self.get_ui_client(serial).set_text_by_description(description, text)
        return {
            "serial": serial,
            "description": description,
            "text": text,
            "success": True,
        }

    def set_text_on_description_child(
        self,
        serial: str,
        description: str,
        text: str,
    ) -> dict[str, Any]:
        self.get_ui_client(serial).set_text_on_description_child(description, text)
        return {
            "serial": serial,
            "description": description,
            "text": text,
            "success": True,
        }

    def launch_app(self, serial: str, package_name: str) -> dict[str, Any]:
        device = self.get_device(serial)
        device.app_start(package_name)
        return {"serial": serial, "package_name": package_name, "success": True}

    def press_back(self, serial: str) -> dict[str, Any]:
        device = self.get_device(serial)
        device.shell("input keyevent 4")
        return {"serial": serial, "success": True}

    def press_home(self, serial: str) -> dict[str, Any]:
        device = self.get_device(serial)
        device.shell("input keyevent 3")
        return {"serial": serial, "success": True}

    def push_media_to_device(
        self,
        serial: str,
        local_path: str,
        remote_path: str,
        scan_media: bool = True,
    ) -> dict[str, Any]:
        device = self.get_device(serial)
        source_path = Path(local_path).expanduser().resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"Local media file not found: {source_path}")

        device.sync.push(str(source_path), remote_path)
        if scan_media:
            device.shell(
                'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE '
                f'-d "file://{remote_path}"'
            )

        return {
            "serial": serial,
            "local_path": str(source_path),
            "remote_path": remote_path,
            "file_size_bytes": source_path.stat().st_size,
            "scan_media": scan_media,
            "success": True,
        }
