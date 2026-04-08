# xianyu failure artifacts write local paths back to bitable

Updated: 2026-03-18

## Pattern
- On live Xianyu prepare/publish failure, capture:
  - `screen.png`
  - `hierarchy.xml`
  - `activities.txt`
- Store them under `.tmp/xianyu-failures/<record_id>/<timestamp-stage>/`.
- Always create a run log file at `.tmp/xianyu-logs/<record_id>/<timestamp>-<stage>.log`
  and write its path back to the listing row via the single `日志路径` field.

## Why
- Keeps failure triage cheap and deterministic.
- Avoids building Feishu attachment upload just to make failures inspectable.
- Preserves the raw UI evidence that explains why the row failed.

## Update (2026-03-17)
- Bitable logging is now consolidated to the single `日志路径` field.
- Failure artifacts are still captured locally, but their paths are no longer written to the
  separate failure columns.

## Update (2026-03-18)
- The `日志路径` field now always points to the per-run `.tmp/xianyu-logs/...` file that records
  status transitions, errors, and (when available) the artifact directory for triage.
