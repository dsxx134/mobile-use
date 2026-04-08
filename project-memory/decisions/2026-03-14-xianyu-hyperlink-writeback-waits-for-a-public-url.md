# xianyu hyperlink writeback waits for a public url

Date: 2026-03-14

## Decision
- Write back `闲鱼商品ID` as soon as `DetailActivity` receipt extraction proves the item id.
- Do not write the current `fleamarket://awesome_detail?...` deep link into the Feishu
  `闲鱼商品链接` field yet.

## Why
- The current receipt source is reliable for item-id recovery because Android activity dumps expose
  the resumed detail-page intent.
- The current Feishu field type for `闲鱼商品链接` is a hyperlink field, and live verification
  returned `URLFieldConvFail` when given the app-only `fleamarket://...` deep link.

## Consequences
- Auto-publish now recovers and stores `闲鱼商品ID` in Bitable.
- The live result can still surface the raw `detail_deep_link` for debugging.
- A later batch can add a public `https://...` item URL source or a separate plain-text field if
  deep-link persistence becomes important.
