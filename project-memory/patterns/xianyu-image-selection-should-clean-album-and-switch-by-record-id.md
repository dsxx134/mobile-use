# xianyu-image-selection-should-clean-album-and-switch-by-record-id

Updated: 2026-03-15

## Pattern
- Before pushing listing media, clear the dedicated Android album root under `/sdcard/DCIM/XianyuPublish`.
- Stage the current listing under its own record-scoped subdirectory, such as `/sdcard/DCIM/XianyuPublish/{record_id}`.
- When selecting media in Xianyu, switch the picker source to the current `record_id` folder instead of a static album label like `XianyuPublish`.

## Why
- The Huawei-tablet picker can keep stale test images in the dedicated automation album across runs.
- After switching to record-scoped directories, the picker source menu exposes rows such as `{record_id}·1`, not the root folder label.
- If the flow keeps looking for a static source name, it can either select an old placeholder image or fail to switch sources even though the current record folder is visible.

## Implementation Notes
- `XianyuMediaSyncService.push_listing_media()` now removes the dedicated album root before pushing current files.
- `XianyuPrepareRunner` passes `staged_listing.record_id` into `select_cover_image(..., preferred_album_name=...)`.
- `XianyuPublishFlowService.switch_album_source()` now falls back to tapping a visible `{record_id}·N` source row even when the analyzer still classifies the overlay as `album_picker`.
