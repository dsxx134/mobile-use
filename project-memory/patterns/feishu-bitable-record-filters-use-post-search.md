# feishu-bitable-record-filters-use-post-search

Updated: 2026-03-14

## Pattern
- Query filtered Bitable rows through
  `POST /bitable/v1/apps/{app_token}/tables/{table_id}/records/search`
  with a JSON body that includes `page_size` and `filter`.
- For `isNotEmpty` conditions, include `value: []` in the filter condition.

## Why
- The live Xianyu table returned `InvalidFilter` when the same logic used
  `GET /records?filter=...`.
- The `records/search` endpoint accepted the real filter shape and returned the publishable row.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py`
