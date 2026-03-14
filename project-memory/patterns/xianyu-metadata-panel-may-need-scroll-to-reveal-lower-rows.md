# xianyu metadata panel may need scroll to reveal lower rows

Updated: 2026-03-14

## Pattern
- If the current editor state is `metadata_panel` but lower-row targets such as `选择位置` are
  missing, do not fail immediately.
- Perform a portrait-oriented upward swipe inside the editor:
  - x ratio `0.5`
  - start y ratio `0.82`
  - end y ratio `0.35`
  - duration `350ms`
- Re-run screen analysis after the swipe and retry the lower-row lookup.

## Why it matters
- On the Huawei tablet, the upper and lower editor slices are still the same `metadata_panel`, but
  the accessibility tree only exposes the lower action rows after scrolling.
- Without this reveal step, location search can be silently skipped and later submit behavior is
  misleading.

## Used in
- `XianyuPublishFlowService._reveal_metadata_target()`
- `XianyuPublishFlowService.advance_listing_form_to_location_panel()`
