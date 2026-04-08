# xianyu batch worker stops on limit empty queue or error

Updated: 2026-03-14

## Pattern
- Drive the queue with three explicit stop reasons:
  - `limit_reached`
  - `no_publishable_listing`
  - `stopped_on_error`
- Between processed items, optionally sleep for a configurable cooldown.
- When `stop_on_error` is disabled, record the failed item and keep going.

## Why it matters
- Operators need predictable batch boundaries on a real sale account.
- A structured stop reason is easier to inspect than inferring behavior from logs or missing rows.

## Used in
- `publish_listing_queue_live()`
- `scripts/xianyu_publish_queue_live.py`
