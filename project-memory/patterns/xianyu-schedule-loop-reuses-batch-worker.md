# xianyu schedule loop reuses batch worker

Updated: 2026-03-15

## Pattern
- Do not create a second publish path for scheduled operation.
- Build scheduled execution as a thin outer loop around `publish_listing_queue_live()`.
- Keep stop policy outside the inner batch worker:
  - `max_runs`
  - `stop_when_idle`
  - `stop_on_batch_error`

## Why
- The batch worker already owns the real publish behavior, retry guard, and summary writeback.
- Reusing it avoids divergence between ad-hoc batch runs and long-lived scheduled runs.
- The outer loop becomes easy to test with mocked batch results.
