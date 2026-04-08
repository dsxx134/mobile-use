# xianyu scrolled metadata still belongs to editor

Updated: 2026-03-14

## Pattern
- Do not treat a scrolled Xianyu editor state as `publish_chooser` just because upper-form
  controls like `添加图片` are no longer visible.
- If the page still has the `发闲置` header, metadata rows/chips, and lower editor rows such as
  `价格设置`, `发货方式`, or `选择位置`, it still belongs to `metadata_panel`.

## Why It Helps
- Real-device runs on the Huawei tablet showed that returning from `location_panel` can land on a
  scrolled editor state with:
  - metadata chips
  - lower editor rows
  - no visible add-image tile
- Misclassifying that state as `publish_chooser` blocks downstream bridges that should still work.

## Files
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- `README.md`
