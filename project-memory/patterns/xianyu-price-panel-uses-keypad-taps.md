# xianyu price panel uses keypad taps

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, tapping `价格设置` from the portrait `发闲置` form opens a dedicated bottom-sheet `price_panel`.
- Sale price entry on that panel should use the exposed keypad targets plus `删除` and `确定`, not `input_text()`.
- After confirming, the flow should wait until `listing_form` is visible again before touching the next field.

## Why it matters
- The price panel is more deterministic than IME-based text entry because the keypad, delete, and confirm controls are all present in the accessibility tree.
- Real-device verification showed normal decimal semantics: tapping `399.9` and then `确定` returned to the form with the row rendered as `¥399.90`.
- Reusing the same keypad path avoids the editor-side focus changes and FastInputIME warm-up behavior seen on text fields.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- real-device automation on `E2P6R22708000602`
