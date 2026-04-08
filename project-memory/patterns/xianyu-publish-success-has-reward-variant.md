# xianyu publish success has reward variant

Updated: 2026-03-14

## Pattern
- Do not assume Xianyu publish success only appears as `看看宝贝` plus `继续发布`.
- Also treat the reward-style result page as `publish_success` when it shows:
  - visible `发布成功`
  - reward copy such as `100闲鱼币`
  - a follow-up action like `再发一件`

## Why it matters
- A real Huawei-tablet auto-publish run reached a genuine success page but was misclassified as
  `unknown` because that skin does not expose `看看宝贝`.
- Recognizing both success skins prevents successful listings from being written back as
  `发布失败`.

## Used in
- `XianyuFlowAnalyzer.detect_screen()`
- `XianyuPublishFlowService.submit_listing_and_wait_for_result()`
