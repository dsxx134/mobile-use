import json
from pathlib import Path

from minitap.mobile_use.scenarios.xianyu_publish.auto_publish_cli import (
    run_auto_publish_cli,
)
from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    XianyuLiveBatchPublishResult,
    XianyuLiveQueueScheduleResult,
)
from minitap.mobile_use.scenarios.xianyu_publish.prepare_cli import run_prepare_cli
from minitap.mobile_use.scenarios.xianyu_publish.publish_schedule_cli import (
    run_publish_schedule_cli,
)
from minitap.mobile_use.scenarios.xianyu_publish.review_cli import run_review_cli
from minitap.mobile_use.scenarios.xianyu_publish.runner import (
    XianyuPrepareListingResult,
    XianyuPublishResult,
)


def _make_prepare_result() -> XianyuPrepareListingResult:
    return XianyuPrepareListingResult(
        record_id="recA",
        serial="device-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recA/01.png"],
        body_text="标题\n\n描述",
        final_screen_name="metadata_panel",
        publish=XianyuPublishResult(
            success=True,
            screen_name="publish_success",
            detail_screen_name="listing_detail",
            published_at="2026-04-09T21:00:00+08:00",
            listing_id="xy-001",
            listing_url="https://m.tb.cn/example",
        ),
    )


def _make_batch_result(*, failure_count: int = 0) -> XianyuLiveBatchPublishResult:
    success_count = 0 if failure_count else 1
    return XianyuLiveBatchPublishResult(
        batch_run_id="batch-1",
        batch_ran_at="2026-04-09T21:10:00+08:00",
        requested_count=1,
        processed_count=1,
        success_count=success_count,
        failure_count=failure_count,
        stopped_reason="limit_reached",
        items=[],
    )


def _make_schedule_result(*, failure_count: int = 0) -> XianyuLiveQueueScheduleResult:
    success_count = 0 if failure_count else 1
    return XianyuLiveQueueScheduleResult(
        interval_seconds=60.0,
        run_count=1,
        total_processed_count=1,
        total_success_count=success_count,
        total_failure_count=failure_count,
        stopped_reason="max_runs_reached" if failure_count == 0 else "batch_error",
        batch_results=[],
    )


def test_run_prepare_cli_passes_args_and_returns_json():
    captured: dict[str, object] = {}

    def fake_prepare(**kwargs):
        captured.update(kwargs)
        return _make_prepare_result()

    output = run_prepare_cli(
        [
            "--serial",
            "device-1",
            "--staging-root",
            "C:/tmp/xianyu",
            "--preheat-max-steps",
            "7",
            "--preheat-attempts",
            "3",
        ],
        prepare_fn=fake_prepare,
    )

    payload = json.loads(output)
    assert payload["record_id"] == "recA"
    assert captured["serial"] == "device-1"
    assert captured["staging_root"] == Path("C:/tmp/xianyu")
    assert captured["preheat_max_steps"] == 7
    assert captured["preheat_attempts"] == 3
    assert captured["review_after_prepare"] is False
    assert captured["auto_publish_after_prepare"] is False


def test_run_review_cli_enables_review_mode():
    captured: dict[str, object] = {}

    def fake_prepare(**kwargs):
        captured.update(kwargs)
        return _make_prepare_result()

    output = run_review_cli(
        [
            "--serial",
            "device-2",
            "--staging-root",
            "C:/tmp/review",
        ],
        prepare_fn=fake_prepare,
    )

    payload = json.loads(output)
    assert payload["record_id"] == "recA"
    assert captured["serial"] == "device-2"
    assert captured["staging_root"] == Path("C:/tmp/review")
    assert captured["review_after_prepare"] is True
    assert captured["auto_publish_after_prepare"] is False


def test_run_auto_publish_cli_enables_auto_publish_mode():
    captured: dict[str, object] = {}

    def fake_prepare(**kwargs):
        captured.update(kwargs)
        return _make_prepare_result()

    output = run_auto_publish_cli(
        [
            "--serial",
            "device-3",
            "--staging-root",
            "C:/tmp/auto",
            "--preheat-max-steps",
            "11",
            "--preheat-attempts",
            "4",
        ],
        prepare_fn=fake_prepare,
    )

    payload = json.loads(output)
    assert payload["publish"]["listing_id"] == "xy-001"
    assert captured["serial"] == "device-3"
    assert captured["staging_root"] == Path("C:/tmp/auto")
    assert captured["preheat_max_steps"] == 11
    assert captured["preheat_attempts"] == 4
    assert captured["review_after_prepare"] is False
    assert captured["auto_publish_after_prepare"] is True


def test_run_publish_schedule_cli_passes_args_and_returns_json():
    captured: dict[str, object] = {}

    def fake_schedule(**kwargs):
        captured.update(kwargs)
        return _make_schedule_result()

    output, exit_code = run_publish_schedule_cli(
        [
            "--serial",
            "device-4",
            "--staging-root",
            "C:/tmp/schedule",
            "--preheat-max-steps",
            "12",
            "--preheat-attempts",
            "5",
            "--max-items",
            "2",
            "--cooldown-seconds",
            "1.5",
            "--stop-on-error",
            "--interval-seconds",
            "30",
            "--max-runs",
            "9",
            "--stop-when-idle",
            "--stop-on-batch-error",
        ],
        schedule_fn=fake_schedule,
    )

    payload = json.loads(output)
    assert payload["run_count"] == 1
    assert exit_code == 0
    assert captured["serial"] == "device-4"
    assert captured["staging_root"] == Path("C:/tmp/schedule")
    assert captured["preheat_max_steps"] == 12
    assert captured["preheat_attempts"] == 5
    assert captured["max_items"] == 2
    assert captured["cooldown_seconds"] == 1.5
    assert captured["stop_on_error"] is True
    assert captured["interval_seconds"] == 30.0
    assert captured["max_runs"] == 9
    assert captured["stop_when_idle"] is True
    assert captured["stop_on_batch_error"] is True


def test_run_publish_schedule_cli_sets_failure_exit_code():
    def fake_schedule(**_kwargs):
        return _make_schedule_result(failure_count=1)

    _output, exit_code = run_publish_schedule_cli([], schedule_fn=fake_schedule)

    assert exit_code == 2
