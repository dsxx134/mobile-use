import json
import os
import sys

from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService
from minitap.mobile_use.scenarios.xianyu_publish.flow import XianyuFlowAnalyzer
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def _pick_serial(service: AndroidDebugService) -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]

    env_serial = os.getenv("ANDROID_SERIAL")
    if env_serial:
        return env_serial

    devices = service.list_devices()
    if not devices:
        raise SystemExit("No Android devices connected.")
    serial = devices[0].get("serial")
    if not serial:
        raise SystemExit("Connected Android device has no serial.")
    return serial


def main() -> None:
    settings = XianyuPublishSettings()
    service = AndroidDebugService()
    analyzer = XianyuFlowAnalyzer(settings=settings)
    serial = _pick_serial(service)

    screen = service.get_screen_data(serial)
    analysis = analyzer.detect_screen(screen)
    print(
        json.dumps(
            {
                "serial": serial,
                "current_app": screen["current_app"],
                "screen_name": analysis.screen_name,
                "target_keys": sorted(analysis.targets.keys()),
                "visible_text_preview": analysis.visible_texts[:12],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
