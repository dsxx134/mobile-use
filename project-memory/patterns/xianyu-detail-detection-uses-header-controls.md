# xianyu detail detection uses header controls

Updated: 2026-03-14

## Pattern
- Recognize Xianyu item detail pages by combining:
  - activity `com.taobao.idlefish.detail.DetailActivity`
  - visible `返回`
  - visible `搜索按钮`
  - visible `分享按钮`

## Why it matters
- The detail hierarchy is otherwise noisy and product-specific, but the header controls are stable
  enough to use as a deterministic screen signature.
- This keeps detail detection narrow and avoids conflating unrelated FlutterBoost pages with item
  detail.

## Used in
- `XianyuFlowAnalyzer.detect_screen()`
