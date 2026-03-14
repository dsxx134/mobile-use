import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from adbutils import AdbClient, adb
from pydantic import BaseModel, ConfigDict, Field

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


class XianyuLiveBatchPublishItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt: int
    success: bool
    record_id: str | None = None
    final_screen_name: str | None = None
    publish_screen_name: str | None = None
    detail_screen_name: str | None = None
    listing_id: str | None = None
    listing_url: str | None = None
    error: str | None = None


class XianyuLiveBatchPublishResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_run_id: str
    batch_ran_at: str
    requested_count: int
    processed_count: int
    success_count: int
    failure_count: int
    stopped_reason: str
    items: list[XianyuLiveBatchPublishItem] = Field(default_factory=list)


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
    batch_run_id: str | None = None,
    batch_ran_at: str | None = None,
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
    if batch_run_id is not None:
        runner_kwargs["batch_run_id"] = batch_run_id
    if batch_ran_at is not None:
        runner_kwargs["batch_ran_at"] = batch_ran_at

    return live_components.runner.prepare_first_publishable_listing(**runner_kwargs)


def format_live_prepare_result(result: XianyuPrepareListingResult) -> str:
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


def format_live_batch_result(result: XianyuLiveBatchPublishResult) -> str:
    return json.dumps(result.model_dump(), ensure_ascii=False, indent=2)


def _build_batch_item(
    attempt: int,
    result: XianyuPrepareListingResult,
) -> XianyuLiveBatchPublishItem:
    publish = result.publish
    return XianyuLiveBatchPublishItem(
        attempt=attempt,
        success=bool(publish and publish.success),
        record_id=result.record_id,
        final_screen_name=result.final_screen_name,
        publish_screen_name=publish.screen_name if publish is not None else None,
        detail_screen_name=publish.detail_screen_name if publish is not None else None,
        listing_id=publish.listing_id if publish is not None else None,
        listing_url=publish.listing_url if publish is not None else None,
    )


def _build_batch_run_id(batch_ran_at: str) -> str:
    timestamp = (
        batch_ran_at.replace(":", "")
        .replace("-", "")
        .replace("+", "p")
        .replace(".", "")
    )
    return f"xianyu-batch-{timestamp}-{uuid4().hex[:8]}"


def publish_listing_queue_live(
    *,
    settings: XianyuPublishSettings | None = None,
    adb_client: AdbClient | None = None,
    serial: str | None = None,
    staging_root: Path | None = None,
    preheat_max_steps: int = 10,
    preheat_attempts: int = 2,
    max_items: int = 1,
    cooldown_seconds: float = 0.0,
    stop_on_error: bool = False,
    batch_run_id: str | None = None,
    batch_ran_at: str | None = None,
    now_fn: Any | None = None,
    sleep_fn: Any | None = None,
    components: XianyuLivePrepareComponents | None = None,
) -> XianyuLiveBatchPublishResult:
    if max_items < 1:
        raise ValueError("max_items must be at least 1")

    resolved_now_fn = now_fn or (lambda: datetime.now(UTC))
    resolved_batch_ran_at = batch_ran_at or resolved_now_fn().isoformat()
    resolved_batch_run_id = batch_run_id or _build_batch_run_id(resolved_batch_ran_at)
    sleeper = sleep_fn or time.sleep
    items: list[XianyuLiveBatchPublishItem] = []
    stopped_reason = "limit_reached"

    for attempt in range(1, max_items + 1):
        try:
            result = prepare_first_publishable_listing_live(
                settings=settings,
                adb_client=adb_client,
                serial=serial,
                staging_root=staging_root,
                preheat_max_steps=preheat_max_steps,
                preheat_attempts=preheat_attempts,
                auto_publish_after_prepare=True,
                batch_run_id=resolved_batch_run_id,
                batch_ran_at=resolved_batch_ran_at,
                components=components,
            )
        except ValueError as exc:
            if str(exc) == "No publishable Xianyu listing found":
                stopped_reason = "no_publishable_listing"
                break
            raise
        except Exception as exc:
            items.append(
                XianyuLiveBatchPublishItem(
                    attempt=attempt,
                    success=False,
                    error=str(exc),
                )
            )
            if stop_on_error:
                stopped_reason = "stopped_on_error"
                break
        else:
            items.append(_build_batch_item(attempt, result))

        if attempt < max_items and cooldown_seconds > 0:
            sleeper(cooldown_seconds)

    success_count = sum(1 for item in items if item.success)
    failure_count = sum(1 for item in items if not item.success)
    return XianyuLiveBatchPublishResult(
        batch_run_id=resolved_batch_run_id,
        batch_ran_at=resolved_batch_ran_at,
        requested_count=max_items,
        processed_count=len(items),
        success_count=success_count,
        failure_count=failure_count,
        stopped_reason=stopped_reason,
        items=items,
    )
