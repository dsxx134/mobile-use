# xianyu listing form opens album picker

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, the portrait `发闲置` form can reopen media selection directly by tapping the `添加图片` tile.
- The first stable downstream state is the existing album picker, sometimes after a brief blank or loading snapshot.
- The bridge should tolerate either:
  - a short `unknown` loading gap inside Xianyu
  - or the Android media permission dialog before the picker appears

## Why it matters
- This gives the portrait-first publish flow a deterministic way to attach listing photos without routing back through the older chooser logic.
- It also lets the business flow reuse the existing album-source switching and image-selection helpers instead of inventing a second upload path.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- real-device automation on `E2P6R22708000602`
