# xianyu retry budget is filtered client-side

Updated: 2026-03-14

## Pattern
- Keep the Feishu search filter limited to simple row predicates:
  - `是否允许发布=true`
  - `发布状态=待发布`
  - `商品图片` is not empty
- Store retry state on the row itself:
  - `失败重试次数`
  - `失败重试上限`
- After rows are fetched, skip any row where `失败重试次数 >= 失败重试上限`.
- When the row does not define `失败重试上限`, fall back to the local default retry limit.

## Why it matters
- Feishu Bitable search is reliable for static predicates, but field-to-field retry-budget
  comparisons are simpler and safer in application code.
- This keeps the queue behavior deterministic even if an operator manually resets a failed row back
  to `待发布`.

## Used in
- `FeishuBitableSource.pick_first_publishable_record()`
- `XianyuPrepareRunner`
- `publish_listing_queue_live()`
