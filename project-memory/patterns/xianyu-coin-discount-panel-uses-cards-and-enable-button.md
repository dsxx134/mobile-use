# xianyu coin discount panel uses cards and an enable button

Date: 2026-03-18

## Context
The coin-discount sheet (`设置闲鱼币抵扣`) renders the discount choices as visual cards instead of
text rows. The UI hierarchy does not expose the card labels as `text` or `content-desc`.

## Pattern
- Use the `android.widget.HorizontalScrollView` bounds as the card area.
- Tap the card area by index (left/middle/right) to choose `30% / 20% / 10%`.
- Always tap the `开启抵扣` button to apply the choice; do not rely on an implicit confirm.
- The listing-form row can render as a single line like `闲鱼币抵扣 允许买家使用闲鱼币支付30%`.
  Parse the percentage from that line when verifying the selection.

## Applied In
- `XianyuPublishFlowService.set_coin_discount()`
- `XianyuFlowAnalyzer.detect_screen()` adds `coin_discount_cards` and `coin_discount_enable`.
