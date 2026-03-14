# feishu url fields use text link objects

Updated: 2026-03-14

## Pattern
- Write Feishu Bitable `Url` fields as:
  - `{\"text\": url, \"link\": url}`
- Do not send a bare string when updating a `type=15 / ui_type=Url` field.

## Why it matters
- Live probing against the Xianyu debug table showed that the `闲鱼商品链接` field accepted the
  `{text, link}` object form after rejecting plain string writes with `URLFieldConvFail`.

## Used in
- `FeishuBitableSource.update_publish_result()`
