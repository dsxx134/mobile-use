from unittest.mock import Mock, call

import pytest

from minitap.mobile_use.scenarios.xianyu_publish import live_prepare as live_prepare_module
from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    XianyuLiveBatchPublishResult,
    XianyuLivePrepareComponents,
    build_live_prepare_components,
    publish_listing_queue_live,
    prepare_first_publishable_listing_live,
    resolve_adb_serial,
)
from minitap.mobile_use.scenarios.xianyu_publish.runner import (
    XianyuPrepareListingResult,
    XianyuPublishResult,
)
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def _make_settings(*, serial: str | None = None) -> XianyuPublishSettings:
    return XianyuPublishSettings(
        FEISHU_APP_ID="cli_test",
        FEISHU_APP_SECRET="secret",
        XIANYU_BITABLE_APP_TOKEN="app_token",
        XIANYU_BITABLE_TABLE_ID="table_id",
        XIANYU_ANDROID_SERIAL=serial,
    )


def _make_adb_device(serial: str) -> Mock:
    device = Mock()
    device.serial = serial
    return device


def test_resolve_adb_serial_prefers_explicit_serial():
    adb_client = Mock()

    serial = resolve_adb_serial(adb_client, requested_serial="tablet-1")

    assert serial == "tablet-1"
    adb_client.device_list.assert_not_called()


def test_resolve_adb_serial_uses_only_connected_device_when_unambiguous():
    adb_client = Mock()
    adb_client.device_list.return_value = [_make_adb_device("tablet-1")]

    serial = resolve_adb_serial(adb_client)

    assert serial == "tablet-1"


def test_resolve_adb_serial_raises_when_multiple_devices_are_connected():
    adb_client = Mock()
    adb_client.device_list.return_value = [
        _make_adb_device("tablet-1"),
        _make_adb_device("emulator-5554"),
    ]

    with pytest.raises(ValueError, match="Multiple Android devices are connected"):
        resolve_adb_serial(adb_client)


def test_build_live_prepare_components_wires_authenticated_feishu_downloads():
    settings = _make_settings()
    adb_client = Mock()
    http_client = Mock()

    components = build_live_prepare_components(
        settings,
        adb_client=adb_client,
        http_client=http_client,
    )

    assert components.source.settings is settings
    assert components.media_sync.settings is settings
    assert components.flow._settings is settings
    assert components.runner._settings is settings
    assert components.runner._source is components.source
    assert components.runner._media_sync is components.media_sync
    assert components.runner._flow is components.flow
    assert components.media_sync._download_file.__self__ is components.source
    assert components.media_sync._adb_client is adb_client


def test_prepare_first_publishable_listing_live_preheats_before_runner(tmp_path):
    settings = _make_settings(serial="tablet-1")
    flow = Mock()
    flow.advance_to_listing_form.return_value = Mock(screen_name="listing_form")
    runner = Mock()
    runner.prepare_first_publishable_listing.return_value = XianyuPrepareListingResult(
        record_id="recA",
        serial="tablet-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recA/01_image.png"],
        body_text="34寸显示器\n\n成色很好，北京自提。",
        final_screen_name="metadata_panel",
    )
    components = XianyuLivePrepareComponents(
        source=Mock(),
        media_sync=Mock(),
        flow=flow,
        runner=runner,
    )

    result = prepare_first_publishable_listing_live(
        settings=settings,
        adb_client=Mock(),
        staging_root=tmp_path,
        preheat_max_steps=12,
        components=components,
    )

    assert flow.mock_calls == [
        call.open_home("tablet-1"),
        call.advance_to_listing_form("tablet-1", max_steps=12),
    ]
    runner.prepare_first_publishable_listing.assert_called_once_with(
        serial="tablet-1",
        staging_root=tmp_path,
        review_after_prepare=False,
    )
    assert result.final_screen_name == "metadata_panel"


def test_prepare_first_publishable_listing_live_retries_preheat_once(tmp_path):
    settings = _make_settings(serial="tablet-1")
    flow = Mock()
    flow.advance_to_listing_form.side_effect = [
        RuntimeError("Failed to reach listing form within 10 steps: unknown"),
        Mock(screen_name="listing_form"),
    ]
    runner = Mock()
    runner.prepare_first_publishable_listing.return_value = XianyuPrepareListingResult(
        record_id="recA",
        serial="tablet-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recA/01_image.png"],
        body_text="34寸显示器\n\n成色很好，北京自提。",
        final_screen_name="listing_form",
    )
    components = XianyuLivePrepareComponents(
        source=Mock(),
        media_sync=Mock(),
        flow=flow,
        runner=runner,
    )

    result = prepare_first_publishable_listing_live(
        settings=settings,
        adb_client=Mock(),
        staging_root=tmp_path,
        components=components,
    )

    assert flow.mock_calls == [
        call.open_home("tablet-1"),
        call.advance_to_listing_form("tablet-1", max_steps=10),
        call.open_home("tablet-1"),
        call.advance_to_listing_form("tablet-1", max_steps=10),
    ]
    runner.prepare_first_publishable_listing.assert_called_once_with(
        serial="tablet-1",
        staging_root=tmp_path,
        review_after_prepare=False,
    )
    assert result.final_screen_name == "listing_form"


def test_prepare_first_publishable_listing_live_can_request_review_mode(tmp_path):
    settings = _make_settings(serial="tablet-1")
    flow = Mock()
    flow.advance_to_listing_form.return_value = Mock(screen_name="listing_form")
    runner = Mock()
    runner.prepare_first_publishable_listing.return_value = XianyuPrepareListingResult(
        record_id="recA",
        serial="tablet-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recA/01_image.png"],
        body_text="34寸显示器\n\n成色很好，北京自提。",
        final_screen_name="metadata_panel",
    )
    components = XianyuLivePrepareComponents(
        source=Mock(),
        media_sync=Mock(),
        flow=flow,
        runner=runner,
    )

    prepare_first_publishable_listing_live(
        settings=settings,
        adb_client=Mock(),
        staging_root=tmp_path,
        components=components,
        review_after_prepare=True,
    )

    runner.prepare_first_publishable_listing.assert_called_once_with(
        serial="tablet-1",
        staging_root=tmp_path,
        review_after_prepare=True,
    )


def test_prepare_first_publishable_listing_live_can_request_auto_publish_mode(tmp_path):
    settings = _make_settings(serial="tablet-1")
    flow = Mock()
    flow.advance_to_listing_form.return_value = Mock(screen_name="listing_form")
    runner = Mock()
    runner.prepare_first_publishable_listing.return_value = XianyuPrepareListingResult(
        record_id="recA",
        serial="tablet-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recA/01_image.png"],
        body_text="34寸显示器\n\n成色很好，北京自提。",
        final_screen_name="publish_success",
    )
    components = XianyuLivePrepareComponents(
        source=Mock(),
        media_sync=Mock(),
        flow=flow,
        runner=runner,
    )

    prepare_first_publishable_listing_live(
        settings=settings,
        adb_client=Mock(),
        staging_root=tmp_path,
        components=components,
        auto_publish_after_prepare=True,
    )

    runner.prepare_first_publishable_listing.assert_called_once_with(
        serial="tablet-1",
        staging_root=tmp_path,
        review_after_prepare=False,
        auto_publish_after_prepare=True,
    )


def test_publish_listing_queue_live_processes_multiple_items_with_cooldown(tmp_path, monkeypatch):
    settings = _make_settings(serial="tablet-1")
    adb_client = Mock()
    first = XianyuPrepareListingResult(
        record_id="recA",
        serial="tablet-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recA/01_image.png"],
        body_text="A",
        final_screen_name="listing_detail",
        publish=XianyuPublishResult(
            success=True,
            screen_name="publish_success",
            detail_screen_name="listing_detail",
            published_at="2026-03-14T20:30:00+00:00",
            listing_id="xyA",
            listing_url="https://m.tb.cn/a",
        ),
    )
    second = XianyuPrepareListingResult(
        record_id="recB",
        serial="tablet-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recB/01_image.png"],
        body_text="B",
        final_screen_name="listing_detail",
        publish=XianyuPublishResult(
            success=True,
            screen_name="publish_success",
            detail_screen_name="listing_detail",
            published_at="2026-03-14T20:31:00+00:00",
            listing_id="xyB",
            listing_url="https://m.tb.cn/b",
        ),
    )
    prepare_mock = Mock(side_effect=[first, second])
    sleep_fn = Mock()
    monkeypatch.setattr(
        live_prepare_module,
        "prepare_first_publishable_listing_live",
        prepare_mock,
    )

    result = publish_listing_queue_live(
        settings=settings,
        adb_client=adb_client,
        staging_root=tmp_path,
        max_items=2,
        cooldown_seconds=3.5,
        sleep_fn=sleep_fn,
        batch_run_id="batch-001",
        batch_ran_at="2026-03-15T09:00:00+08:00",
    )

    assert isinstance(result, XianyuLiveBatchPublishResult)
    assert result.batch_run_id == "batch-001"
    assert result.batch_ran_at == "2026-03-15T09:00:00+08:00"
    assert result.processed_count == 2
    assert result.success_count == 2
    assert result.failure_count == 0
    assert result.stopped_reason == "limit_reached"
    assert [item.record_id for item in result.items] == ["recA", "recB"]
    assert [item.listing_url for item in result.items] == ["https://m.tb.cn/a", "https://m.tb.cn/b"]
    sleep_fn.assert_called_once_with(3.5)
    assert prepare_mock.call_count == 2
    assert prepare_mock.call_args_list == [
        call(
            settings=settings,
            adb_client=adb_client,
            serial=None,
            staging_root=tmp_path,
            preheat_max_steps=10,
            preheat_attempts=2,
            auto_publish_after_prepare=True,
            components=None,
            batch_run_id="batch-001",
            batch_ran_at="2026-03-15T09:00:00+08:00",
        ),
        call(
            settings=settings,
            adb_client=adb_client,
            serial=None,
            staging_root=tmp_path,
            preheat_max_steps=10,
            preheat_attempts=2,
            auto_publish_after_prepare=True,
            components=None,
            batch_run_id="batch-001",
            batch_ran_at="2026-03-15T09:00:00+08:00",
        ),
    ]


def test_publish_listing_queue_live_stops_cleanly_when_no_candidates_exist(tmp_path, monkeypatch):
    settings = _make_settings(serial="tablet-1")
    prepare_mock = Mock(side_effect=ValueError("No publishable Xianyu listing found"))
    sleep_fn = Mock()
    monkeypatch.setattr(
        live_prepare_module,
        "prepare_first_publishable_listing_live",
        prepare_mock,
    )

    result = publish_listing_queue_live(
        settings=settings,
        adb_client=Mock(),
        staging_root=tmp_path,
        max_items=3,
        sleep_fn=sleep_fn,
    )

    assert result.processed_count == 0
    assert result.success_count == 0
    assert result.failure_count == 0
    assert result.stopped_reason == "no_publishable_listing"
    assert result.items == []
    sleep_fn.assert_not_called()
    prepare_mock.assert_called_once()


def test_publish_listing_queue_live_can_continue_after_a_failed_item(tmp_path, monkeypatch):
    settings = _make_settings(serial="tablet-1")
    success = XianyuPrepareListingResult(
        record_id="recB",
        serial="tablet-1",
        remote_media_paths=["/sdcard/DCIM/XianyuPublish/recB/01_image.png"],
        body_text="B",
        final_screen_name="listing_detail",
        publish=XianyuPublishResult(
            success=True,
            screen_name="publish_success",
            detail_screen_name="listing_detail",
            published_at="2026-03-14T20:31:00+00:00",
            listing_id="xyB",
            listing_url="https://m.tb.cn/b",
        ),
    )
    prepare_mock = Mock(
        side_effect=[
            RuntimeError(
                "Publish blocked because Xianyu could not locate the administrative region."
            ),
            success,
            ValueError("No publishable Xianyu listing found"),
        ]
    )
    sleep_fn = Mock()
    monkeypatch.setattr(
        live_prepare_module,
        "prepare_first_publishable_listing_live",
        prepare_mock,
    )

    result = publish_listing_queue_live(
        settings=settings,
        adb_client=Mock(),
        staging_root=tmp_path,
        max_items=3,
        cooldown_seconds=2.0,
        sleep_fn=sleep_fn,
    )

    assert result.processed_count == 2
    assert result.success_count == 1
    assert result.failure_count == 1
    assert result.stopped_reason == "no_publishable_listing"
    assert result.items[0].success is False
    assert result.items[0].error == (
        "Publish blocked because Xianyu could not locate the administrative region."
    )
    assert result.items[1].record_id == "recB"
    assert sleep_fn.call_count == 2


def test_publish_listing_queue_live_can_stop_on_first_error(tmp_path, monkeypatch):
    settings = _make_settings(serial="tablet-1")
    prepare_mock = Mock(side_effect=RuntimeError("Publish blocked"))
    sleep_fn = Mock()
    monkeypatch.setattr(
        live_prepare_module,
        "prepare_first_publishable_listing_live",
        prepare_mock,
    )

    result = publish_listing_queue_live(
        settings=settings,
        adb_client=Mock(),
        staging_root=tmp_path,
        max_items=3,
        sleep_fn=sleep_fn,
        stop_on_error=True,
    )

    assert result.processed_count == 1
    assert result.success_count == 0
    assert result.failure_count == 1
    assert result.stopped_reason == "stopped_on_error"
    assert result.items[0].success is False
    assert result.items[0].error == "Publish blocked"
    sleep_fn.assert_not_called()
