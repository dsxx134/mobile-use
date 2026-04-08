# xianyu retry budget is enforced before runner

Date: 2026-03-14

## Decision
- Track retry state in Feishu Bitable with two explicit fields:
  - `失败重试次数`
  - `失败重试上限`
- Enforce retry exhaustion in `FeishuBitableSource` before a row becomes a `ListingDraft`.
- Do not add server-side Feishu field-comparison logic for this budget in the first version.

## Why
- The existing Bitable search path is already stable with a small set of static predicates.
- Client-side exhaustion checks are easier to verify than relying on field-to-field comparisons in
  the remote filter syntax.
- The selection layer is the right place to keep exhausted rows out of both single-item and queue
  publish flows.

## Consequences
- Rows that operators manually reset to `待发布` still respect their retry budget.
- Failure handlers must increment retry count on `准备失败` and `发布失败`.
- Successful auto-publish writeback resets retry count to `0`.
- The default retry limit remains local configuration (`3`) when the row does not define one.
