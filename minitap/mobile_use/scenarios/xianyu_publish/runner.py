from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from minitap.mobile_use.scenarios.xianyu_publish.models import ListingDraft
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


class XianyuPrepareReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    screen_name: str
    submit_button_visible: bool
    ready_for_manual_publish: bool


class XianyuPublishResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    screen_name: str
    detail_screen_name: str | None = None
    published_at: str | None = None
    listing_id: str | None = None
    listing_url: str | None = None


class XianyuPrepareListingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    serial: str
    remote_media_paths: list[str]
    body_text: str
    final_screen_name: str
    review: XianyuPrepareReview | None = None
    publish: XianyuPublishResult | None = None


def build_listing_body(listing: ListingDraft) -> str:
    title = listing.title.strip()
    description = listing.description.strip()

    if description.startswith(title):
        return description
    return f"{title}\n\n{description}"


def _is_optional_item_source_visibility_error(error: RuntimeError) -> bool:
    message = str(error)
    return "metadata_source_option_" in message and "target on metadata panel" in message


def _is_optional_category_visibility_error(error: RuntimeError) -> bool:
    message = str(error)
    return "metadata_category_option_" in message and "target on metadata panel" in message


def _is_best_effort_location_error(error: RuntimeError) -> bool:
    message = str(error)
    return (
        "location_entry target on metadata_panel" in message
        or "location_entry target on listing_form" in message
        or "location" in message.lower()
    )


class XianyuPrepareRunner:
    def __init__(
        self,
        *,
        source: Any,
        media_sync: Any,
        flow: Any,
        settings: XianyuPublishSettings | None = None,
        now_fn: Any | None = None,
    ) -> None:
        self._source = source
        self._media_sync = media_sync
        self._flow = flow
        self._settings = settings or XianyuPublishSettings()
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def prepare_first_publishable_listing(
        self,
        *,
        serial: str,
        staging_root: Path,
        review_after_prepare: bool = False,
        auto_publish_after_prepare: bool = False,
    ) -> XianyuPrepareListingResult:
        listing = self._source.pick_first_publishable_record()
        if listing is None:
            raise ValueError("No publishable Xianyu listing found")

        self._source.update_listing_status(listing.record_id, "准备中")
        review: XianyuPrepareReview | None = None
        publish: XianyuPublishResult | None = None
        try:
            download_urls = self._source.get_attachment_download_urls(listing.attachments)
            staged_listing = self._media_sync.download_listing_media(
                listing,
                download_urls,
                staging_root,
            )
            media_result = self._media_sync.push_listing_media(staged_listing, serial=serial)

            self._flow.advance_to_listing_form(serial)
            body_text = build_listing_body(staged_listing)
            final_analysis = self._flow.fill_price(serial, staged_listing.price)
            final_analysis = self._flow.fill_description(serial, body_text)

            self._flow.advance_listing_form_to_album_picker(serial)
            post_image_analysis = self._flow.select_cover_image(
                serial,
                preferred_album_name=self._settings.preferred_album_name,
            )
            if post_image_analysis.screen_name == "photo_analysis":
                self._flow.advance_photo_analysis_to_publish_chooser(serial)
                final_analysis = self._flow.advance_to_listing_form(serial)
            elif post_image_analysis.screen_name not in {"listing_form", "metadata_panel"}:
                raise RuntimeError(
                    "Unsupported post-image screen for prepare runner: "
                    f"{post_image_analysis.screen_name}"
                )
            else:
                final_analysis = post_image_analysis

            if staged_listing.category:
                try:
                    final_analysis = self._flow.set_item_category(serial, staged_listing.category)
                except RuntimeError as exc:
                    if not _is_optional_category_visibility_error(exc):
                        raise
            if staged_listing.condition:
                final_analysis = self._flow.set_item_condition(serial, staged_listing.condition)
            if staged_listing.item_source:
                try:
                    final_analysis = self._flow.set_item_source(serial, staged_listing.item_source)
                except RuntimeError as exc:
                    if not _is_optional_item_source_visibility_error(exc):
                        raise
            if staged_listing.location_search_query:
                try:
                    final_analysis = self._flow.search_location_and_select_result(
                        serial,
                        staged_listing.location_search_query,
                    )
                except RuntimeError as exc:
                    if not _is_best_effort_location_error(exc):
                        raise

            if review_after_prepare or auto_publish_after_prepare:
                review = self._build_prepare_review(final_analysis)

        except Exception as exc:
            self._source.update_listing_status(
                listing.record_id,
                "准备失败",
                failure_reason=str(exc),
            )
            raise

        if auto_publish_after_prepare:
            try:
                if not staged_listing.allow_auto_publish:
                    raise RuntimeError("Auto publish is not enabled for this listing")

                self._source.update_listing_status(
                    staged_listing.record_id,
                    "发布中",
                    failure_reason=None,
                )
                publish_analysis = self._flow.submit_listing_and_wait_for_result(serial)
                detail_screen_name: str | None = None
                try:
                    detail_analysis = self._flow.advance_publish_success_to_listing_detail(serial)
                    detail_screen_name = detail_analysis.screen_name
                except RuntimeError:
                    detail_screen_name = None
                published_at = self._now_fn().isoformat()
                self._source.update_publish_result(
                    staged_listing.record_id,
                    status="已发布",
                    failure_reason=None,
                    published_at=published_at,
                    listing_id=None,
                    listing_url=None,
                )
                publish = XianyuPublishResult(
                    success=True,
                    screen_name=publish_analysis.screen_name,
                    detail_screen_name=detail_screen_name,
                    published_at=published_at,
                    listing_id=None,
                    listing_url=None,
                )
                if detail_screen_name is not None:
                    final_analysis = detail_analysis
                else:
                    final_analysis = publish_analysis
            except Exception as exc:
                self._source.update_publish_result(
                    staged_listing.record_id,
                    status="发布失败",
                    failure_reason=str(exc),
                    published_at=None,
                    listing_id=None,
                    listing_url=None,
                )
                raise
        else:
            next_status = "已就绪"
            if review_after_prepare:
                next_status = self._settings.manual_review_status

            self._source.update_listing_status(
                staged_listing.record_id,
                next_status,
                failure_reason=None,
            )

        return XianyuPrepareListingResult(
            record_id=staged_listing.record_id,
            serial=serial,
            remote_media_paths=media_result.remote_paths,
            body_text=body_text,
            final_screen_name=final_analysis.screen_name,
            review=review,
            publish=publish,
        )

    def _build_prepare_review(self, final_analysis: Any) -> XianyuPrepareReview:
        screen_name = final_analysis.screen_name
        if screen_name not in {"listing_form", "metadata_panel"}:
            raise RuntimeError(
                "Prepare review requires a supported editor screen, got "
                f"{screen_name}"
            )

        submit_button_visible = final_analysis.targets.get("submit_listing") is not None
        if not submit_button_visible:
            raise RuntimeError("Publish submit button is not visible after prepare")

        return XianyuPrepareReview(
            screen_name=screen_name,
            submit_button_visible=submit_button_visible,
            ready_for_manual_publish=True,
        )
