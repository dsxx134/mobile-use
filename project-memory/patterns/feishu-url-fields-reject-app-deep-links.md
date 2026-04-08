# feishu url fields reject app deep links

Updated: 2026-03-14

## Pattern
- Treat Feishu hyperlink fields as `http://` or `https://` destinations only.
- Do not write `fleamarket://...` or other app-only deep links into a Bitable URL field.

## Why it matters
- Live verification against the Xianyu debug Bitable returned `URLFieldConvFail` when the current
  `闲鱼商品链接` field received a `fleamarket://awesome_detail?...` value.
- The runner should keep the publish writeback stable instead of failing the whole post-publish
  update on a field-type mismatch.

## Used in
- `FeishuBitableSource.update_publish_result()` call sites that now keep `listing_url=None` until a
  public URL source is available
