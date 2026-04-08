# Xianyu Price Panel Original Price + Stock

Date: 2026-03-19

## Goal
Extend the Xianyu publish flow to optionally fill `原价` and `库存` on the price panel.
Both values come from Feishu Bitable fields and should be skipped when empty.

## Approach (Recommended)
- Reuse the price panel entry point (`价格设置`) and existing numeric keypad logic.
- Add two selectable targets in `price_panel` analysis:
  - `original_price_entry` anchored on `原价设置`
  - `stock_entry` anchored on `库存设置`
- When a value is provided, click the entry row, clear existing input via the delete key,
  then input the new value using the same keypad mapping.

## Data Mapping
- New settings:
  - `original_price_field_name` defaults to `原价`
  - `stock_field_name` defaults to `库存`
- New ListingDraft fields (optional):
  - `original_price` (float-compatible, allow decimal)
  - `stock` (integer only)

## Flow Integration
- Keep `fill_price` for `售价` as-is (always required).
- Add `fill_original_price` and `fill_stock` (or a unified helper) that:
  - Run only when the field has a value.
  - Force clear then retype.
  - Return to the same `price_panel` between fields.
- After processing, use existing `price_confirm` to return to editor.

## Validation & Errors
- `stock` must be integer-only; any decimal or invalid value raises a runtime error,
  writes to `日志路径`, and stops the run.
- `original_price` uses the same normalization rules as `售价`.
- Empty fields are no-ops.

## Tests
- Screen analysis detects `original_price_entry` and `stock_entry` on `price_panel`.
- Filling original price and stock uses keypad targets and clears before typing.
- Invalid stock input raises.

