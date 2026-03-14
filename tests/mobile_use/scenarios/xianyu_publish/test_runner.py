from unittest.mock import Mock, call

import pytest

from minitap.mobile_use.scenarios.xianyu_publish.media_sync import ListingMediaSyncResult
from minitap.mobile_use.scenarios.xianyu_publish.models import (
    FeishuAttachment,
    ListingDraft,
    XianyuScreenAnalysis,
)
from minitap.mobile_use.scenarios.xianyu_publish.runner import (
    XianyuPrepareRunner,
    build_listing_body,
)


def _make_listing(
    *,
    title: str = "二手显示器",
    description: str = "成色很好，支持验货",
    category: str | None = None,
    condition: str | None = None,
    item_source: str | None = None,
) -> ListingDraft:
    return ListingDraft(
        record_id="recA",
        title=title,
        description=description,
        price=199.0,
        attachments=[FeishuAttachment(file_token="ft-1", name="1.jpg")],
        category=category,
        condition=condition,
        item_source=item_source,
    )


def test_build_listing_body_prefers_title_then_blank_line_then_description():
    body = build_listing_body(_make_listing())

    assert body == "二手显示器\n\n成色很好，支持验货"


def test_build_listing_body_deduplicates_when_description_already_starts_with_title():
    listing = _make_listing(description="二手显示器\n成色很好，支持验货")

    body = build_listing_body(listing)

    assert body == "二手显示器\n成色很好，支持验货"


def test_prepare_first_publishable_listing_runs_feishu_media_and_flow_chain_in_order(tmp_path):
    listing = _make_listing()
    downloaded_listing = listing.model_copy(
        update={"local_image_paths": [tmp_path / "recA" / "01_1.jpg"]}
    )
    source = Mock()
    source.pick_first_publishable_record.return_value = listing
    source.get_attachment_download_urls.return_value = {"ft-1": "https://files.example/1.jpg"}
    media_sync = Mock()
    media_sync.download_listing_media.return_value = downloaded_listing
    media_sync.push_listing_media.return_value = ListingMediaSyncResult(
        serial="device-1",
        remote_dir="/sdcard/DCIM/XianyuPublish/recA",
        remote_paths=["/sdcard/DCIM/XianyuPublish/recA/01_1.jpg"],
        pushed_count=1,
    )
    flow = Mock()
    flow.advance_to_listing_form.side_effect = [
        XianyuScreenAnalysis(screen_name="listing_form"),
        XianyuScreenAnalysis(screen_name="listing_form"),
    ]
    flow.advance_listing_form_to_album_picker.return_value = XianyuScreenAnalysis(
        screen_name="album_picker"
    )
    flow.select_cover_image.return_value = XianyuScreenAnalysis(screen_name="photo_analysis")
    flow.advance_photo_analysis_to_publish_chooser.return_value = XianyuScreenAnalysis(
        screen_name="publish_chooser"
    )
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    timeline = Mock()
    timeline.attach_mock(source, "source")
    timeline.attach_mock(media_sync, "media_sync")
    timeline.attach_mock(flow, "flow")
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
    )

    assert timeline.mock_calls == [
        call.source.pick_first_publishable_record(),
        call.source.get_attachment_download_urls(listing.attachments),
        call.media_sync.download_listing_media(
            listing,
            {"ft-1": "https://files.example/1.jpg"},
            tmp_path,
        ),
        call.media_sync.push_listing_media(downloaded_listing, serial="device-1"),
        call.flow.advance_to_listing_form("device-1"),
        call.flow.advance_listing_form_to_album_picker("device-1"),
        call.flow.select_cover_image("device-1", preferred_album_name="XianyuPublish"),
        call.flow.advance_photo_analysis_to_publish_chooser("device-1"),
        call.flow.advance_to_listing_form("device-1"),
        call.flow.fill_description("device-1", "二手显示器\n\n成色很好，支持验货"),
        call.flow.fill_price("device-1", 199.0),
    ]
    assert result.record_id == "recA"
    assert result.serial == "device-1"
    assert result.remote_media_paths == ["/sdcard/DCIM/XianyuPublish/recA/01_1.jpg"]
    assert result.body_text == "二手显示器\n\n成色很好，支持验货"
    assert result.final_screen_name == "listing_form"


def test_prepare_first_publishable_listing_raises_when_no_publishable_record_exists(tmp_path):
    source = Mock()
    source.pick_first_publishable_record.return_value = None
    media_sync = Mock()
    flow = Mock()
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    with pytest.raises(ValueError, match="No publishable Xianyu listing found"):
        runner.prepare_first_publishable_listing(serial="device-1", staging_root=tmp_path)

    source.get_attachment_download_urls.assert_not_called()
    media_sync.download_listing_media.assert_not_called()
    flow.advance_to_listing_form.assert_not_called()


def test_prepare_first_publishable_listing_skips_bridge_when_image_flow_returns_listing_form(
    tmp_path,
):
    listing = _make_listing()
    source = Mock()
    source.pick_first_publishable_record.return_value = listing
    source.get_attachment_download_urls.return_value = {"ft-1": "https://files.example/1.jpg"}
    media_sync = Mock()
    media_sync.download_listing_media.return_value = listing
    media_sync.push_listing_media.return_value = ListingMediaSyncResult(
        serial="device-1",
        remote_dir="/sdcard/DCIM/XianyuPublish/recA",
        remote_paths=["/sdcard/DCIM/XianyuPublish/recA/01_1.jpg"],
        pushed_count=1,
    )
    flow = Mock()
    flow.advance_to_listing_form.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.advance_listing_form_to_album_picker.return_value = XianyuScreenAnalysis(
        screen_name="album_picker"
    )
    flow.select_cover_image.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
    )

    flow.advance_photo_analysis_to_publish_chooser.assert_not_called()
    assert flow.advance_to_listing_form.call_count == 1
    assert result.final_screen_name == "listing_form"


def test_prepare_first_publishable_listing_applies_optional_metadata_fields(tmp_path):
    listing = _make_listing(category="家居摆件", condition="几乎全新", item_source="闲置")
    source = Mock()
    source.pick_first_publishable_record.return_value = listing
    source.get_attachment_download_urls.return_value = {"ft-1": "https://files.example/1.jpg"}
    media_sync = Mock()
    media_sync.download_listing_media.return_value = listing
    media_sync.push_listing_media.return_value = ListingMediaSyncResult(
        serial="device-1",
        remote_dir="/sdcard/DCIM/XianyuPublish/recA",
        remote_paths=["/sdcard/DCIM/XianyuPublish/recA/01_1.jpg"],
        pushed_count=1,
    )
    flow = Mock()
    flow.advance_to_listing_form.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.advance_listing_form_to_album_picker.return_value = XianyuScreenAnalysis(
        screen_name="album_picker"
    )
    flow.select_cover_image.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.set_item_category.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.set_item_condition.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.set_item_source.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    timeline = Mock()
    timeline.attach_mock(source, "source")
    timeline.attach_mock(media_sync, "media_sync")
    timeline.attach_mock(flow, "flow")
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
    )

    assert timeline.mock_calls == [
        call.source.pick_first_publishable_record(),
        call.source.get_attachment_download_urls(listing.attachments),
        call.media_sync.download_listing_media(
            listing,
            {"ft-1": "https://files.example/1.jpg"},
            tmp_path,
        ),
        call.media_sync.push_listing_media(listing, serial="device-1"),
        call.flow.advance_to_listing_form("device-1"),
        call.flow.advance_listing_form_to_album_picker("device-1"),
        call.flow.select_cover_image("device-1", preferred_album_name="XianyuPublish"),
        call.flow.fill_description("device-1", "二手显示器\n\n成色很好，支持验货"),
        call.flow.fill_price("device-1", 199.0),
        call.flow.set_item_category("device-1", "家居摆件"),
        call.flow.set_item_condition("device-1", "几乎全新"),
        call.flow.set_item_source("device-1", "闲置"),
    ]
    assert result.final_screen_name == "metadata_panel"
