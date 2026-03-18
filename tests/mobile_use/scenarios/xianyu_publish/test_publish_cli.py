import json
from pathlib import Path

from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    XianyuLiveBatchPublishResult,
)
from minitap.mobile_use.scenarios.xianyu_publish.publish_cli import run_publish_cli


def _make_result(*, failure_count: int = 0) -> XianyuLiveBatchPublishResult:
    success_count = 0 if failure_count else 1
    return XianyuLiveBatchPublishResult(
        batch_run_id="batch-1",
        batch_ran_at="2026-03-18T12:00:00+08:00",
        requested_count=1,
        processed_count=1,
        success_count=success_count,
        failure_count=failure_count,
        stopped_reason="limit_reached",
        items=[],
    )


def test_run_publish_cli_passes_args_and_returns_json():
    captured: dict[str, object] = {}

    def fake_publish_queue(**kwargs):
        captured.update(kwargs)
        return _make_result()

    output, exit_code = run_publish_cli(
        [
            "--serial",
            "device-1",
            "--staging-root",
            "C:/tmp/xianyu",
            "--preheat-max-steps",
            "7",
            "--preheat-attempts",
            "3",
            "--max-items",
            "2",
            "--cooldown-seconds",
            "1.5",
            "--stop-on-error",
        ],
        publish_queue_fn=fake_publish_queue,
    )

    payload = json.loads(output)
    assert payload["batch_run_id"] == "batch-1"
    assert exit_code == 0
    assert captured["serial"] == "device-1"
    assert captured["staging_root"] == Path("C:/tmp/xianyu")
    assert captured["preheat_max_steps"] == 7
    assert captured["preheat_attempts"] == 3
    assert captured["max_items"] == 2
    assert captured["cooldown_seconds"] == 1.5
    assert captured["stop_on_error"] is True


def test_run_publish_cli_sets_failure_exit_code():
    def fake_publish_queue(**_kwargs):
        return _make_result(failure_count=1)

    _output, exit_code = run_publish_cli([], publish_queue_fn=fake_publish_queue)

    assert exit_code == 2
