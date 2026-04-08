# xianyu batch summary writeback is best effort

Updated: 2026-03-15

## Pattern
- After a queue run completes, attempt one summary-row append into the `批次运行汇总` table.
- Do not let summary writeback failures overturn the actual publish result.
- Surface the outcome in the returned batch payload:
  - `summary_logged`
  - `summary_log_error`

## Why it matters
- Publishing rows is the primary business action; summary logging is observability.
- Operators still need visibility when the summary write path is broken, but a logging failure
  should not pretend the publish run itself failed.

## Used in
- `publish_listing_queue_live()`
- `scripts/xianyu_publish_queue_live.py`
