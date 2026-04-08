# xianyu public url writeback uses detail share copy link

Date: 2026-03-14

## Decision
- Recover the public `闲鱼商品链接` from the detail-page share sheet instead of trying to derive it
  from `DetailActivity` intent data.
- Keep the existing activity-dump receipt extraction for `闲鱼商品ID` and raw app deep link.

## Why
- Real-device probing showed that the detail-page share sheet exposes a deterministic `复制链接`
  action.
- The clipboard after `复制链接` contains a Feishu-compatible public `https://m.tb.cn/...` short
  link, which is more useful for external writeback than the app-only `fleamarket://...` deep
  link.

## Consequences
- Auto-publish can now best-effort populate both `闲鱼商品ID` and `闲鱼商品链接`.
- The post-publish flow now includes one additional UI step on the detail page:
  `分享按钮 -> 复制链接 -> 剪贴板 -> Back`.
