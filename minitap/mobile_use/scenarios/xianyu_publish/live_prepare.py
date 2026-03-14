import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from adbutils import AdbClient, adb

from minitap.mobile_use.scenarios.xianyu_publish.feishu_source import FeishuBitableSource
from minitap.mobile_use.scenarios.xianyu_publish.flow import XianyuPublishFlowService
from minitap.mobile_use.scenarios.xianyu_publish.media_sync import XianyuMediaSyncService
from minitap.mobile_use.scenarios.xianyu_publish.runner import (
    XianyuPrepareListingResult,
    XianyuPrepareRunner,
)
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


@dataclass(slots=True)
class XianyuLivePrepareComponents:
    source: Any
    media_sync: Any
    flow: Any
    runner: Any


def resolve_adb_serial(adb_client: AdbClient, requested_serial: str | None = None) -> str:
    if requested_serial:
        return requested_serial

    devices = list(adb_client.device_list())
    if not devices:
        raise ValueError("No Android devices are connected")
    if len(devices) > 1:
        serials = ", ".join(sorted(device.serial for device in devices))
        raise ValueError(
            "Multiple Android devices are connected. "
            f"Pass --serial or set XIANYU_ANDROID_SERIAL. Connected: {serials}"
        )
    return devices[0].serial


def build_live_prepare_components(
    settings: XianyuPublishSettings,
    *,
    adb_client: AdbClient | None = None,
    http_client: Any | None = None,
) -> XianyuLivePrepareComponents:
    resolved_adb_client = adb_client or adb
    source = FeishuBitableSource(settings, http_client=http_client)
    media_sync = XianyuMediaSyncService(
        settings,
        resolved_adb_client,
        download_file=source.download_attachment_file,
    )
    flow = XianyuPublishFlowService(settings)
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
        settings=settings,
    )
    return XianyuLivePrepareComponents(
        source=source,
        media_sync=media_sync,
        flow=flow,
        runner=runner,
    )


def prepare_first_publishable_listing_live(
    *,
    settings: XianyuPublishSettings | None = None,
    adb_client: AdbClient | None = None,
    serial: str | None = None,
    staging_root: Path | None = None,
    preheat_max_steps: int = 10,
    preheat_attempts: int = 2,
    review_after_prepare: bool = False,
    auto_publish_after_prepare: bool = False,
    components: XianyuLivePrepareComponents | None = None,
) -> XianyuPrepareListingResult:
    resolved_settings = settings or XianyuPublishSettings()
    resolved_adb_client = adb_client or adb
    resolved_serial = resolve_adb_serial(
        resolved_adb_client,
        requested_serial=serial or resolved_settings.XIANYU_ANDROID_SERIAL,
    )
    resolved_staging_root = (staging_root or Path(".tmp") / "xianyu-prepare").resolve()
    resolved_staging_root.mkdir(parents=True, exist_ok=True)
    live_components = components or build_live_prepare_components(
        resolved_settings,
        adb_client=resolved_adb_client,
    )

    if preheat_attempts < 1:
        raise ValueError("preheat_attempts must be at least 1")

    last_error: RuntimeError | None = None
    for _ in range(preheat_attempts):
        try:
            live_components.flow.open_home(resolved_serial)
            live_components.flow.advance_to_listing_form(
                resolved_serial,
                max_steps=preheat_max_steps,
            )
            last_error = None
            break
        except RuntimeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error

    runner_kwargs: dict[str, Any] = {
        "serial": resolved_serial,
        "staging_root": resolved_staging_root,
        "review_after_prepare": review_after_prepare,
    }
    if auto_publish_after_prepare:
        runner_kwargs["auto_publish_after_prepare"] = True

    return live_components.runner.prepare_first_publishable_listing(**runner_kwargs)


def format_live_prepare_result(result: XianyuPrepareListingResult) -> str:
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)
