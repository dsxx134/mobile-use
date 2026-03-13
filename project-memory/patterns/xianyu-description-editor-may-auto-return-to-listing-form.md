# xianyu description editor may auto return to listing form

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, entering the Xianyu description editor from the portrait `发闲置` form is deterministic.
- After `input_text()` runs, the app can already collapse back to `listing_form` without needing an extra tap on `完成`.
- The flow should always re-analyze the screen immediately after text input before reusing any `description_done` coordinates.

## Why it matters
- Reusing stale `完成` coordinates after the editor already closed can hit a different control on the restored form.
- In real-device verification, that stale tap opened `价格设置`, which looked like a random regression until the post-input state was inspected.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- real-device automation on `E2P6R22708000602`
