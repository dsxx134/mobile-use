# xianyu shipping time toggle switches

Date: 2026-03-19

## Pattern
- Some listing forms omit the `发货时间/发货时效` row and instead show toggle switches for
  `24小时发货` and `48小时发货`.
- Treat these toggles as the authoritative shipping-time selector and tap the desired switch.

## Why it matters
- Without the header row, panel-based shipping-time selection never appears.
- Direct toggle selection prevents false "missing entry" errors.
