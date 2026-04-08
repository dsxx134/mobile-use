# xianyu location region picker uses clickable region row

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, the portrait `发闲置` form exposes a `选择位置` row that opens a root `location_panel`.
- The stable bridge into hierarchical region selection is the full clickable `请选择宝贝所在地` row, not the smaller `去选择` label below it.
- That bridge leads into a `location_region_picker` screen with headers like `所在地`, `返回`, and `获取当前位置`.

## Why it matters
- Using the full row is more robust and matches the real-device accessibility tree.
- Final location writeback is not yet deterministic, so the current supported boundary is entering the region picker, not asserting that a chosen region persists on the listing form.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- real-device automation on `E2P6R22708000602`
