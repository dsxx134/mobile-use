from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from minitap.mobile_use.scenarios.xianyu_publish.models import ListingDraft
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


class XianyuPrepareListingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    serial: str
    remote_media_paths: list[str]
    body_text: str
    final_screen_name: str


def build_listing_body(listing: ListingDraft) -> str:
    title = listing.title.strip()
    description = listing.description.strip()

    if description.startswith(title):
        return description
    return f"{title}\n\n{description}"


def _is_optional_item_source_visibility_error(error: RuntimeError) -> bool:
    message = str(error)
    return "metadata_source_option_" in message and "target on metadata panel" in message


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
    ) -> None:
        self._source = source
        self._media_sync = media_sync
        self._flow = flow
        self._settings = settings or XianyuPublishSettings()

    def prepare_first_publishable_listing(
        self,
        *,
        serial: str,
        staging_root: Path,
    ) -> XianyuPrepareListingResult:
        listing = self._source.pick_first_publishable_record()
        if listing is None:
            raise ValueError("No publishable Xianyu listing found")

        self._source.update_listing_status(listing.record_id, "准备中")
        try:
            download_urls = self._source.get_attachment_download_urls(listing.attachments)
            staged_listing = self._media_sync.download_listing_media(
                listing,
                download_urls,
                staging_root,
            )
            media_result = self._media_sync.push_listing_media(staged_listing, serial=serial)

            self._flow.advance_to_listing_form(serial)
            self._flow.advance_listing_form_to_album_picker(serial)
            post_image_analysis = self._flow.select_cover_image(
                serial,
                preferred_album_name=self._settings.preferred_album_name,
            )
            if post_image_analysis.screen_name == "photo_analysis":
                self._flow.advance_photo_analysis_to_publish_chooser(serial)
                self._flow.advance_to_listing_form(serial)
            elif post_image_analysis.screen_name != "listing_form":
                raise RuntimeError(
                    "Unsupported post-image screen for prepare runner: "
                    f"{post_image_analysis.screen_name}"
                )

            body_text = build_listing_body(staged_listing)
            self._flow.fill_description(serial, body_text)
            final_analysis = self._flow.fill_price(serial, staged_listing.price)
            if staged_listing.category:
                final_analysis = self._flow.set_item_category(serial, staged_listing.category)
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

            self._source.update_listing_status(
                staged_listing.record_id,
                "已就绪",
                failure_reason=None,
            )
        except Exception as exc:
            self._source.update_listing_status(
                listing.record_id,
                "准备失败",
                failure_reason=str(exc),
            )
            raise

        return XianyuPrepareListingResult(
            record_id=staged_listing.record_id,
            serial=serial,
            remote_media_paths=media_result.remote_paths,
            body_text=body_text,
            final_screen_name=final_analysis.screen_name,
        )
