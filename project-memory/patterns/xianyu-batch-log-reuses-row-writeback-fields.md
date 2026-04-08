# xianyu batch log reuses row writeback fields

Updated: 2026-03-15

## Pattern
- Do not create a second Feishu table for the first version of queue logging.
- Instead, stamp the processed listing row with three lightweight fields:
  - `最近批次运行ID`
  - `最近批次运行时间`
  - `最近批次运行结果`
- Generate one batch id per queue run and reuse it across all processed rows in that run.
- Let existing status/result writeback methods carry the batch metadata instead of adding a
  separate queue-only writeback path.

## Why it matters
- Operators can inspect the latest worker touchpoint directly from the listing table they already
  use.
- The queue stays thin because it reuses the same source update methods already used by prepare and
  publish flows.

## Used in
- `publish_listing_queue_live()`
- `prepare_first_publishable_listing_live()`
- `XianyuPrepareRunner`
- `FeishuBitableSource.update_listing_status()`
- `FeishuBitableSource.update_publish_result()`
