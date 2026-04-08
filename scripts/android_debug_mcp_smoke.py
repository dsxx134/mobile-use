import json

from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService


def main() -> None:
    service = AndroidDebugService()
    devices = service.list_devices()
    print(json.dumps({"count": len(devices), "devices": devices}, ensure_ascii=False))


if __name__ == "__main__":
    main()
