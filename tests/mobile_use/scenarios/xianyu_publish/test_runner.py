from datetime import datetime
from datetime import UTC
from unittest.mock import Mock, call

import pytest

from minitap.mobile_use.scenarios.xianyu_publish.media_sync import ListingMediaSyncResult
from minitap.mobile_use.scenarios.xianyu_publish.models import (
    FeishuAttachment,
    ListingDraft,
    TapTarget,
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
    location_search_query: str | None = None,
    allow_auto_publish: bool = False,
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
        location_search_query=location_search_query,
        allow_auto_publish=allow_auto_publish,
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
        call.source.update_listing_status("recA", "准备中"),
        call.source.get_attachment_download_urls(listing.attachments),
        call.media_sync.download_listing_media(
            listing,
            {"ft-1": "https://files.example/1.jpg"},
            tmp_path,
        ),
        call.media_sync.push_listing_media(downloaded_listing, serial="device-1"),
        call.flow.advance_to_listing_form("device-1"),
        call.flow.fill_price("device-1", 199.0),
        call.flow.fill_description("device-1", "二手显示器\n\n成色很好，支持验货"),
        call.flow.advance_listing_form_to_album_picker("device-1"),
        call.flow.select_cover_image("device-1", preferred_album_name="XianyuPublish"),
        call.flow.advance_photo_analysis_to_publish_chooser("device-1"),
        call.flow.advance_to_listing_form("device-1"),
        call.source.update_listing_status("recA", "已就绪", failure_reason=None),
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
    source.update_listing_status.assert_not_called()
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

    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "已就绪", failure_reason=None),
        ]
    )
    flow.advance_photo_analysis_to_publish_chooser.assert_not_called()
    assert flow.advance_to_listing_form.call_count == 1
    assert result.final_screen_name == "listing_form"


def test_prepare_first_publishable_listing_accepts_metadata_panel_after_image_flow(tmp_path):
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
    flow.select_cover_image.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
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
    assert result.final_screen_name == "metadata_panel"


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
    flow.set_item_category.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
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
        call.source.update_listing_status("recA", "准备中"),
        call.source.get_attachment_download_urls(listing.attachments),
        call.media_sync.download_listing_media(
            listing,
            {"ft-1": "https://files.example/1.jpg"},
            tmp_path,
        ),
        call.media_sync.push_listing_media(listing, serial="device-1"),
        call.flow.advance_to_listing_form("device-1"),
        call.flow.fill_price("device-1", 199.0),
        call.flow.fill_description("device-1", "二手显示器\n\n成色很好，支持验货"),
        call.flow.advance_listing_form_to_album_picker("device-1"),
        call.flow.select_cover_image("device-1", preferred_album_name="XianyuPublish"),
        call.flow.set_item_category("device-1", "家居摆件"),
        call.flow.set_item_condition("device-1", "几乎全新"),
        call.flow.set_item_source("device-1", "闲置"),
        call.source.update_listing_status("recA", "已就绪", failure_reason=None),
    ]
    assert result.final_screen_name == "metadata_panel"


def test_prepare_first_publishable_listing_treats_item_source_as_best_effort(tmp_path):
    listing = _make_listing(item_source="闲置")
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
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.set_item_source.side_effect = RuntimeError(
        "Missing metadata_source_option_闲置 target on metadata panel"
    )
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
    )

    flow.set_item_source.assert_called_once_with("device-1", "闲置")
    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "已就绪", failure_reason=None),
        ]
    )
    assert result.final_screen_name == "listing_form"


def test_prepare_first_publishable_listing_treats_category_as_best_effort(tmp_path):
    listing = _make_listing(category="生活百科")
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
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.advance_listing_form_to_album_picker.return_value = XianyuScreenAnalysis(
        screen_name="album_picker"
    )
    flow.select_cover_image.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.set_item_category.side_effect = RuntimeError(
        "Missing metadata_category_option_生活百科 target on metadata panel"
    )
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
    )

    flow.set_item_category.assert_called_once_with("device-1", "生活百科")
    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "已就绪", failure_reason=None),
        ]
    )
    assert result.final_screen_name == "metadata_panel"


def test_prepare_first_publishable_listing_applies_optional_location_search_query(tmp_path):
    listing = _make_listing(location_search_query="上海虹桥站")
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
    flow.search_location_and_select_result.return_value = XianyuScreenAnalysis(
        screen_name="listing_form"
    )
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
        call.source.update_listing_status("recA", "准备中"),
        call.source.get_attachment_download_urls(listing.attachments),
        call.media_sync.download_listing_media(
            listing,
            {"ft-1": "https://files.example/1.jpg"},
            tmp_path,
        ),
        call.media_sync.push_listing_media(listing, serial="device-1"),
        call.flow.advance_to_listing_form("device-1"),
        call.flow.fill_price("device-1", 199.0),
        call.flow.fill_description("device-1", "二手显示器\n\n成色很好，支持验货"),
        call.flow.advance_listing_form_to_album_picker("device-1"),
        call.flow.select_cover_image("device-1", preferred_album_name="XianyuPublish"),
        call.flow.search_location_and_select_result("device-1", "上海虹桥站"),
        call.source.update_listing_status("recA", "已就绪", failure_reason=None),
    ]
    assert result.final_screen_name == "listing_form"


def test_prepare_first_publishable_listing_treats_location_search_as_best_effort(tmp_path):
    listing = _make_listing(location_search_query="上海虹桥站")
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
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="metadata_panel")
    flow.search_location_and_select_result.side_effect = RuntimeError(
        "Missing location_entry target on metadata_panel"
    )
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
    )

    flow.search_location_and_select_result.assert_called_once_with("device-1", "上海虹桥站")
    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "已就绪", failure_reason=None),
        ]
    )
    assert result.final_screen_name == "listing_form"


def test_prepare_first_publishable_listing_marks_failure_and_reraises(tmp_path):
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
    flow.fill_price.side_effect = RuntimeError("price panel missing")
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    with pytest.raises(RuntimeError, match="price panel missing"):
        runner.prepare_first_publishable_listing(
            serial="device-1",
            staging_root=tmp_path,
        )

    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "准备失败", failure_reason="price panel missing"),
        ]
    )


def test_prepare_first_publishable_listing_review_mode_marks_manual_publish_ready(tmp_path):
    listing = _make_listing(category="家居摆件", condition="几乎全新")
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
    flow.set_item_category.return_value = XianyuScreenAnalysis(
        screen_name="metadata_panel",
        targets={"submit_listing": TapTarget(x=1500, y=140, text="发布, 发布")},
    )
    flow.set_item_condition.return_value = XianyuScreenAnalysis(
        screen_name="metadata_panel",
        targets={"submit_listing": TapTarget(x=1500, y=140, text="发布, 发布")},
    )
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
        review_after_prepare=True,
    )

    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "待人工发布", failure_reason=None),
        ]
    )
    assert result.review is not None
    assert result.review.ready_for_manual_publish is True
    assert result.review.submit_button_visible is True
    assert result.review.screen_name == "metadata_panel"


def test_prepare_first_publishable_listing_review_mode_fails_without_submit_button(tmp_path):
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

    with pytest.raises(RuntimeError, match="Publish submit button is not visible after prepare"):
        runner.prepare_first_publishable_listing(
            serial="device-1",
            staging_root=tmp_path,
            review_after_prepare=True,
        )

    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call(
                "recA",
                "准备失败",
                failure_reason="Publish submit button is not visible after prepare",
            ),
        ]
    )


def test_prepare_first_publishable_listing_auto_publish_writes_publish_result(tmp_path):
    listing = _make_listing(allow_auto_publish=True)
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
    final_editor = XianyuScreenAnalysis(
        screen_name="metadata_panel",
        targets={"submit_listing": TapTarget(x=1500, y=140, text="发布, 发布")},
    )
    flow = Mock()
    flow.advance_to_listing_form.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.advance_listing_form_to_album_picker.return_value = XianyuScreenAnalysis(
        screen_name="album_picker"
    )
    flow.select_cover_image.return_value = final_editor
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.submit_listing_and_wait_for_result.return_value = XianyuScreenAnalysis(
        screen_name="publish_success",
        targets={
            "publish_success_view_listing": TapTarget(
                x=500,
                y=2000,
                text="看看宝贝",
            )
        },
    )
    flow.advance_publish_success_to_listing_detail.return_value = XianyuScreenAnalysis(
        screen_name="listing_detail"
    )
    fixed_now = datetime(2026, 3, 14, 20, 30, 0, tzinfo=UTC)
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
        now_fn=lambda: fixed_now,
    )

    result = runner.prepare_first_publishable_listing(
        serial="device-1",
        staging_root=tmp_path,
        auto_publish_after_prepare=True,
    )

    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "发布中", failure_reason=None),
        ]
    )
    source.update_publish_result.assert_called_once_with(
        "recA",
        status="已发布",
        failure_reason=None,
        published_at="2026-03-14T20:30:00+00:00",
        listing_id=None,
        listing_url=None,
    )
    flow.submit_listing_and_wait_for_result.assert_called_once_with("device-1")
    flow.advance_publish_success_to_listing_detail.assert_called_once_with("device-1")
    assert result.publish is not None
    assert result.publish.success is True
    assert result.publish.screen_name == "publish_success"
    assert result.publish.detail_screen_name == "listing_detail"
    assert result.publish.published_at == "2026-03-14T20:30:00+00:00"


def test_prepare_first_publishable_listing_auto_publish_requires_listing_opt_in(tmp_path):
    listing = _make_listing(allow_auto_publish=False)
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
    flow.select_cover_image.return_value = XianyuScreenAnalysis(
        screen_name="metadata_panel",
        targets={"submit_listing": TapTarget(x=1500, y=140, text="发布, 发布")},
    )
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    with pytest.raises(RuntimeError, match="Auto publish is not enabled for this listing"):
        runner.prepare_first_publishable_listing(
            serial="device-1",
            staging_root=tmp_path,
            auto_publish_after_prepare=True,
        )

    source.update_publish_result.assert_called_once_with(
        "recA",
        status="发布失败",
        failure_reason="Auto publish is not enabled for this listing",
        published_at=None,
        listing_id=None,
        listing_url=None,
    )


def test_prepare_first_publishable_listing_auto_publish_marks_publish_failure(tmp_path):
    listing = _make_listing(allow_auto_publish=True)
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
    flow.select_cover_image.return_value = XianyuScreenAnalysis(
        screen_name="metadata_panel",
        targets={"submit_listing": TapTarget(x=1500, y=140, text="发布, 发布")},
    )
    flow.fill_description.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.fill_price.return_value = XianyuScreenAnalysis(screen_name="listing_form")
    flow.submit_listing_and_wait_for_result.side_effect = RuntimeError(
        "Publish did not reach success screen: metadata_panel"
    )
    runner = XianyuPrepareRunner(
        source=source,
        media_sync=media_sync,
        flow=flow,
    )

    with pytest.raises(RuntimeError, match="Publish did not reach success screen: metadata_panel"):
        runner.prepare_first_publishable_listing(
            serial="device-1",
            staging_root=tmp_path,
            auto_publish_after_prepare=True,
        )

    source.update_listing_status.assert_has_calls(
        [
            call("recA", "准备中"),
            call("recA", "发布中", failure_reason=None),
        ]
    )
    source.update_publish_result.assert_called_once_with(
        "recA",
        status="发布失败",
        failure_reason="Publish did not reach success screen: metadata_panel",
        published_at=None,
        listing_id=None,
        listing_url=None,
    )
