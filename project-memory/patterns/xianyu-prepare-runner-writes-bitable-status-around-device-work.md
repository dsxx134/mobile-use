# xianyu-prepare-runner-writes-bitable-status-around-device-work

Updated: 2026-03-14

## Pattern
- As soon as `XianyuPrepareRunner` selects a Bitable record, write `发布状态=准备中`.
- If the deterministic device flow returns to a prepared editor state, write `发布状态=已就绪`
  and clear `失败原因`.
- If any downstream device step raises, write `发布状态=准备失败` and persist the exception
  string into `失败原因`, then re-raise.

## Why
- Prevents the same row from being silently re-picked as `待发布` on the next run.
- Gives the operator a visible business-layer breadcrumb even before final publish submission is
  automated.
- Keeps the current responsibility narrow: the writeback describes prepare-runner state rather than
  the final Xianyu publish outcome.

## Reuse
- Apply the same pattern to later business runners that coordinate Feishu queue rows with a
  deterministic UI automation slice.
