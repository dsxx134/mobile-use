# xianyu coin discount entry may need scroll

Date: 2026-03-19

## Pattern
- The `闲鱼币抵扣` row can be off-screen in a scrolled listing form; scroll the editor before
  attempting to open the coin-discount panel.

## Why it matters
- Without scrolling, the flow fails to locate `coin_discount_entry` and cannot apply the setting.
