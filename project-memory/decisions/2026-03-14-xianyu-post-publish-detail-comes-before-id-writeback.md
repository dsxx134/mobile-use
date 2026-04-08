# xianyu post publish detail comes before id writeback

Date: 2026-03-14

## Decision
- Add deterministic recovery from publish-success screens into Xianyu item detail before trying to
  populate `闲鱼商品ID / 闲鱼商品链接`.
- Keep Bitable writeback unchanged for now: `已发布 + 发布时间`, with item id/link left empty until
  a stable extraction source is proven.

## Why
- Real-device probing confirmed that successful publishes can land on two different success skins,
  and both can lead into a recognizable detail page.
- The detail bridge is deterministic enough to ship now, while a trustworthy id/link source is
  still not exposed through the current success or detail hierarchies.

## Consequences
- Auto-publish results now expose a best-effort `detail_screen_name` for downstream debugging.
- The next batch should focus on extracting a durable listing identifier from `DetailActivity`
  rather than broadening success-screen heuristics again.
