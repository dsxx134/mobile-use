# xianyu image selection can return directly to listing form

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, selecting an image from the dedicated `XianyuPublish` album does not always lead to `photo_analysis`.
- The app can instead go through:
  - `selected_media_preview` with a `下一步 (1)` button
  - `media_edit_screen` with tools like `裁剪` and a `完成` button
- After tapping `完成`, the flow can return directly to `listing_form`.

## Why it matters
- Treating `photo_analysis` as the only post-image path breaks the business runner on current app behavior.
- Supporting both branches lets `XianyuPrepareRunner` continue filling description and price whether the app returns directly to the form or detours through the older analysis path.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`
- real-device automation on `E2P6R22708000602`
