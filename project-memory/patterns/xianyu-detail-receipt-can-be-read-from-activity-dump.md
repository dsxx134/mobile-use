# xianyu detail receipt can be read from activity dump

Updated: 2026-03-14

## Pattern
- After a successful publish, first bridge into `com.taobao.idlefish.detail.DetailActivity`.
- Then call `adb shell dumpsys activity activities`.
- Parse the resumed detail-page `Intent { dat=fleamarket://awesome_detail?...itemId=... }` line to
  recover:
  - `item_id`
  - the raw app deep link

## Why it matters
- Neither the success screen nor the detail-page accessibility tree exposed a stable item id.
- Android activity state still retained the detail-page intent, which made receipt extraction
  deterministic without needing to drive the share sheet.

## Used in
- `AndroidDebugService.dump_activity_activities()`
- `XianyuPublishFlowService.extract_listing_receipt_from_current_detail()`
- `XianyuPrepareRunner` auto-publish mode
