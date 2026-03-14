# xianyu submit can fail with location required dialog

Updated: 2026-03-14

## Pattern
- Do not treat every post-submit non-success state as a generic `unknown` publish failure.
- On the current Huawei tablet, Xianyu can block submission with a modal that says:
  - `无法发布宝贝`
  - `系统无法定位您所在的行政区，请点击宝贝图片下方位置图标，手动选择行政区。`
- Recognize that modal explicitly and surface its message as the publish failure reason.

## Why it matters
- The auto-publish chain already reaches the final `发布` tap, so the next useful debugging layer is
  accurate post-submit diagnosis, not more pre-submit guesswork.
- Writing the exact modal text back to Bitable makes it obvious that the remaining blocker is
  stable administrative-region writeback, not submit-button visibility, category selection, or a
  missing success-screen detector.

## Used in
- `XianyuFlowAnalyzer.detect_screen()`
- `XianyuPublishFlowService.submit_listing_and_wait_for_result()`
