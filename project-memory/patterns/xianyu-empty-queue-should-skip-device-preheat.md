# xianyu empty queue should skip device preheat

Updated: 2026-03-15

## Pattern
- Before a live queue run opens or preheats Xianyu, probe Feishu once for a publishable row.
- If no row is available, return `stopped_reason=no_publishable_listing` immediately.
- Do not wake the tablet just to discover an empty queue.

## Why it matters
- Device preheat is the slowest and least predictable part of the live path.
- Empty-queue runs are operationally common, especially when using scheduled workers.
- Early exit keeps the device untouched and makes summary logging cleaner.

## Used in
- `prepare_first_publishable_listing_live()`
- `publish_listing_queue_live()`
