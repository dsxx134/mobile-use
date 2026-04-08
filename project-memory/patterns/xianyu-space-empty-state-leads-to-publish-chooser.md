# xianyu space empty state leads to publish chooser

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, after dismissing the initial Xianyu space analysis overlay, tapping the `宝贝` tab can land on an empty-state page with `这里空空如也～`.
- That page exposes a visual `发宝贝` button even when the accessibility tree does not expose a dedicated tappable node for it.
- Tapping `发宝贝` opens the standard Xianyu publish chooser in the right pane.

## Why it matters
- This is the first deterministic bridge out of the space-analysis flow and back into the normal publishing flow.
- It provides a reliable recovery path even when the app routes selected images through `闲鱼空间` instead of directly opening a final listing form.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- future retries that need to escape `photo_analysis` without restarting the whole app
