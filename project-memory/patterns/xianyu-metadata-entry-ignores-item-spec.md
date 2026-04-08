# xianyu metadata entry ignores item spec

Date: 2026-03-19

## Pattern
- The metadata-entry target should be drawn from the `分类` row (including `更多信息` variants),
  and must ignore any `商品规格` row even if it is marked `非必填`.

## Why it matters
- `商品规格` opens a separate spec editor and is not part of the metadata selection flow.
- Accidentally tapping it blocks the publish pipeline with an unwanted spec requirement.
