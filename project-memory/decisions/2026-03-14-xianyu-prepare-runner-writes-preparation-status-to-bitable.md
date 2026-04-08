# xianyu prepare runner writes preparation status to bitable

Date: 2026-03-14

## Decision
- `XianyuPrepareRunner` should own Bitable writeback for its own lifecycle and use:
  - `准备中` when a row has been selected and device work is about to start
  - `已就绪` when the editor has been prepared again
  - `准备失败` plus `失败原因` when any step raises

## Context
- The runner already owns the deterministic business slice from `待发布` queue row to prepared
  Xianyu form.
- Without writeback, the Feishu table has no reliable breadcrumb for whether a row was picked,
  completed the prepare slice, or failed mid-flow.
- Final publish submission is not yet automated, so these states must describe preparation state
  rather than claim listing publication.

## Consequences
- The Bitable queue now reflects the real status of the current automation slice.
- Operators can safely inspect failures and selectively reset rows back to `待发布`.
- The naming stays honest about current scope and does not overclaim a final publish outcome.
