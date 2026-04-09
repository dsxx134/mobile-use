# profiles can carry default collect parameters

Date: 2026-04-09

## Decision
- Add stable run defaults for the collector and include them in profiles.

## Stored Defaults
- `ensure_searchable_default`
- `keyword_pages_default`
- `shop_pages_default`

## Why
- Profiles were already capturing stable collector intent, but common run-time choices still had to be repeated manually.
- These defaults are stable enough to belong with the rest of the operator's preferred setup.

## Consequence
- `collect keyword` and `collect shop` can now inherit page defaults when `--pages` is omitted.
- `collect ...` can also inherit `ensure_searchable_default` when `--ensure-searchable/--no-ensure-searchable` is omitted.
- Loading a profile now restores not just connectivity/filter config, but also the default collection posture.
