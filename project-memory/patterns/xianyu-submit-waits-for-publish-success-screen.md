# xianyu submit waits for publish success screen

Updated: 2026-03-14

## Pattern
- Treat submit as a deterministic one-tap action, not an open-ended flow.
- Start only from a supported editor state with a visible `submit_listing` target.
- Tap `发布` once.
- Keep polling screen analysis until `publish_success` appears.
- If the flow never reaches `publish_success`, fail the row as `发布失败` instead of assuming the
  publish succeeded.

## Why it matters
- The review gate already proved that `listing_form` and `metadata_panel` are the only trusted
  pre-submit states on this Huawei tablet.
- A single post-tap analyzer loop is simpler and safer than trying to infer success from partial
  UI changes or optimistic delays.

## Used in
- `XianyuPublishFlowService.submit_listing_and_wait_for_result()`
- `XianyuPrepareRunner` auto-publish mode
