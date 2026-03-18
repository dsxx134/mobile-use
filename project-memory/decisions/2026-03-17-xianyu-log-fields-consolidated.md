# xianyu log fields consolidated to a single column

Date: 2026-03-17

## Decision
- Consolidate Xianyu failure logging to the single `日志路径` field on the listing row.
- Stop writing per-artifact columns (`最近失败时间`, `最近失败截图路径`, `最近失败界面快照路径`,
  `最近失败活动栈路径`, `最近失败前台应用`) during status and publish updates.

## Why
- The listing table had too many log-related columns for operators to scan quickly.
- The team prefers a single log field in the listing table and local artifact storage for detail.

## Consequences
- Failure artifacts remain captured locally under `.tmp/xianyu-failures/...`.
- Bitable writeback is now concise and focused on status, retry count, and the single log field.

## Update (2026-03-18)
- The consolidated log field is now named `日志路径` in the live table.

## Supersedes
- Partially supersedes `2026-03-15-xianyu-failure-evidence-stays-local-with-path-writeback.md`.
