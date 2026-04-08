# xianyu optional form fields for coin discount and shipping time

Date: 2026-03-18

## Decision
- Add optional Feishu fields for `闲鱼币抵扣`, `发货方式`, and `发货时间`.
- Only apply these fields in the runner when the Bitable cells are non-empty.
- Treat coin-discount and shipping-time sheets as option panels only when multiple options are visible,
  so the listing-form rows are not misclassified as panels.
- Treat the `发货时间` row as best-effort when it is absent for the current category, and allow the
  label variant `发货时效` when reading or parsing the listing-form row.
- Support the alternate UI where only `24小时发货/48小时发货` toggles are present (no
  `发货时间` header), selecting the desired toggle directly on the listing form.

## Why
- The operator wants these fields to be controllable but optional; empty cells should not trigger UI
  changes.
- The listing form renders rows like `闲鱼币抵扣\n30%` and `发货时间\n24小时发货`, which look like
  a two-line option panel and can be misclassified without extra guards.

## Consequences
- `ListingDraft` now carries `coin_discount`, `shipping_method`, and `shipping_time` as optional
  fields with Feishu mappings in `XianyuPublishSettings`.
- The flow adds new panel handlers (`coin_discount_panel`, `shipping_time_panel`) and skips them
  entirely when the fields are unset.
- Panel detection requires at least two options, preventing listing-form false positives.
- The flow will scroll the listing form or metadata panel to reveal `发货时间/发货时效` when needed,
  and the runner logs a skip if the row is still missing.
- The flow now detects the shipping-time toggle switches and can apply the desired option without
  opening a bottom-sheet panel.
