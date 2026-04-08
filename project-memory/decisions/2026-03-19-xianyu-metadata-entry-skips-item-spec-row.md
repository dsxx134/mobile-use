# xianyu metadata entry skips item spec row

Date: 2026-03-19

## Decision
- The listing-form metadata entry must never point at the `商品规格` row.

## Why
- The runner only needs the category/metadata panel, while `商品规格` opens a separate spec
  editor that should not be triggered by automation.

## Consequences
- `_find_metadata_entry_target()` now ignores any element containing `商品规格` and only matches
  rows that include `分类` plus `更多信息/非必填` indicators.
