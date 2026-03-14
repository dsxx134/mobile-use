from unittest.mock import Mock, call

import pytest

from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    XianyuLivePrepareComponents,
    build_live_prepare_components,
    prepare_first_publishable_listing_live,
    resolve_adb_serial,
)
from minitap.mobile_use.scenarios.xianyu_publish.runner import XianyuPrepareListingResult
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
        call.advance_to_listing_form("tablet-1", max_steps=12),
    ]
    runner.prepare_first_publishable_listing.assert_called_once_with(
        serial="tablet-1",
        staging_root=tmp_path,
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
        call.advance_to_listing_form("tablet-1", max_steps=10),
        call.advance_to_listing_form("tablet-1", max_steps=10),
    ]
    runner.prepare_first_publishable_listing.assert_called_once_with(
        serial="tablet-1",
        staging_root=tmp_path,
    )
    assert result.final_screen_name == "listing_form"
