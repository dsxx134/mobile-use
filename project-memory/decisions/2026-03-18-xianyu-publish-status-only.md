# xianyu publish gating uses status only

Date: 2026-03-18

## Decision
- Remove `是否允许发布` and `允许自动发布` from the Feishu listing table.
- Gate publishing exclusively by setting `发布状态` to `待发布` (now a single-select field).

## Why
- The publish checkboxes were always checked by default and added noise without control value.
- Operators prefer one clear control: flip `发布状态` to `待发布` when they want a run.

## Consequences
- The pending-record filter now uses only `发布状态=待发布` plus `商品图片` non-empty.
- `allow_auto_publish` defaults to `True` unless the optional field is explicitly configured.
- Teams that still want the legacy flags can reintroduce the columns and set field names in
  `XianyuPublishSettings`.
