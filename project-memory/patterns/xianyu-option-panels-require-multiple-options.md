# xianyu option panels require multiple options

Date: 2026-03-18

## Context
Xianyu listing-form rows like `闲鱼币抵扣\n30%` and `发货时间\n24小时发货` appear as two-line
labels. The bottom-sheet option panels for these fields also include the header text plus multiple
option rows. Without an extra guard, the analyzer can misclassify the listing form as a panel.

## Pattern
- Treat coin-discount or shipping-time screens as option panels only when at least two distinct
  options are visible.
- This avoids misclassifying the listing-form row (which only shows the currently selected option).

## Applied In
- `XianyuFlowAnalyzer.detect_screen()` for `coin_discount_panel` and `shipping_time_panel`.
