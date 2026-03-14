# xianyu publish success can bridge to detail

Updated: 2026-03-14

## Pattern
- Treat post-publish detail recovery as a small deterministic bridge, not an open-ended browse:
  - if the success page exposes `看看宝贝`, tap it
  - otherwise, if the success page is the reward variant, press `Back` once
- Re-run screen analysis and expect Xianyu `DetailActivity`.

## Why it matters
- Xianyu exposes at least two success skins on the Huawei tablet, but both can still lead to the
  published item detail page.
- This gives the automation a stable post-submit landing point without needing to republish or rely
  on brittle visual heuristics.

## Used in
- `XianyuPublishFlowService.advance_publish_success_to_listing_detail()`
- `XianyuPrepareRunner` auto-publish mode

