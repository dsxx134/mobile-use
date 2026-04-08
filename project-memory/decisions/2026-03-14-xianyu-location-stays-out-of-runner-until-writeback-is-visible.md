# xianyu location stays out of runner until writeback is visible

Date: 2026-03-14

## Decision
- Do not wire Xianyu location selection into `XianyuPrepareRunner` yet.
- Keep location support in the flow layer only until real-device probing shows a stable, visible
  writeback after the selection finishes.

## Why
- The Huawei tablet now has a deterministic bridge into `location_panel` and the hierarchical
  `location_region_picker`.
- The verified region path `上海 -> 上海 -> 黄浦区` also now survives the final picker tail and can
  return to the editor.
- But reopening `location_panel` still shows `请选择宝贝所在地`, and the listing form row still shows
  `选择位置` after both:
  - tapping a district path like `上海 -> 上海 -> 黄浦区`
  - tapping a common-address row like `上海虹桥站`

## Consequence
- Location remains a documented boundary, not a promised prepared-field output.
- Future work should focus on finding the actual persisted confirmation surface or the missing final
  action before the runner starts applying Bitable location data.
