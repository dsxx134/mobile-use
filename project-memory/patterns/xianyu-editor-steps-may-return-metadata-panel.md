# xianyu-editor-steps-may-return-metadata-panel

Updated: 2026-03-14

## Pattern
- Treat both `listing_form` and `metadata_panel` as valid editor states after returning from
  subflows like description entry and price entry.
- When optional lower-section fields such as `商品来源` or `预设地址` are off-screen, keep those
  operations best-effort instead of failing the whole prepare run.

## Why
- On the Huawei tablet, finishing description or price entry can land the app on a scrolled
  `metadata_panel` rather than the upper `listing_form`.
- The current `商品来源` chips and location row are not always visible in the same editor slice
  reached by the live prepare runner.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
