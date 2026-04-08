# xianyu public url comes from share copy link

Updated: 2026-03-14

## Pattern
- When the app is already on `listing_detail`:
  - tap `分享按钮`
  - wait for the share-sheet transparency activity
  - tap `复制链接`
  - read the clipboard
  - extract the first `https://...` URL
  - press `Back` once to restore `listing_detail`

## Why it matters
- The activity dump only exposes the internal `fleamarket://...` deep link.
- The share sheet provides a public short URL that can be written back to Feishu and opened outside
  the app.

## Used in
- `XianyuPublishFlowService.copy_public_listing_url_from_current_detail()`
- `XianyuPrepareRunner` auto-publish mode
