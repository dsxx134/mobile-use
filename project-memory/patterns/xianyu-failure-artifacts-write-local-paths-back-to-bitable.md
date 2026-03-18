# xianyu failure artifacts write local paths back to bitable

Updated: 2026-03-17

## Pattern
- On live Xianyu prepare/publish failure, capture:
  - `screen.png`
  - `hierarchy.xml`
  - `activities.txt`
- Store them under `.tmp/xianyu-failures/<record_id>/<timestamp-stage>/`.
- Write the local paths back to the listing row in these text fields:
  - `最近失败时间`
  - `最近失败截图路径`
  - `最近失败界面快照路径`
  - `最近失败活动栈路径`
  - `最近失败前台应用`

## Why
- Keeps failure triage cheap and deterministic.
- Avoids building Feishu attachment upload just to make failures inspectable.
- Preserves the raw UI evidence that explains why the row failed.

## Update (2026-03-17)
- Bitable logging is now consolidated to the single `失败原因` field.
- Failure artifacts are still captured locally, but their paths are no longer written to the
  separate failure columns.
