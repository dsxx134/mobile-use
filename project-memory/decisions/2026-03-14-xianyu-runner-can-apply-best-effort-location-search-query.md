# xianyu runner can apply best effort location search query

Date: 2026-03-14

## Decision
- Allow `XianyuPrepareRunner` to consume an optional Bitable field named `预设地址`.
- When present, the runner calls the existing location-search helper instead of waiting for a fully
  proven location-persistence flow.

## Why
- The user explicitly prefers a simpler business workflow:
  - avoid the multi-layer `去选择` region flow
  - keep one preset address in Bitable
  - apply it through `搜索地址`
- Real-device probing proved that:
  - the search UI is reachable
  - focused `EditText.set_text()` surfaces result rows
  - tapping a visible result returns to the editor
- Real-device probing still did not prove a visible persisted location after the return.

## Consequence
- This runner behavior is intentionally best-effort.
- The automation now supports a practical business path for prefilled addresses without pretending
  that visible persistence has been solved.
- Documentation must keep stating that the form row still shows `选择位置` and the reopened
  `location_panel` still shows `请选择宝贝所在地` after the helper returns.

## Supersedes
- This partially supersedes `2026-03-14-xianyu-location-stays-out-of-runner-until-writeback-is-visible.md`
  for the specific case of preset address search queries.
