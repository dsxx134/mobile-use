# xianyu metadata panel uses chip selection

Updated: 2026-03-14

## Pattern
- For the Huawei tablet portrait `发闲置` flow, treat the expanded metadata/spec page as a stable
  `metadata_panel` with direct chip targets rather than a modal that needs confirm/cancel handling.
- Use the chip text itself as both the tap target and the verification signal:
  - unselected chips expose `可选<值>, <值>`
  - selected chips expose `已选中<值>, <值>`

## Applied To
- `成色`
- `商品来源`

## Why It Helps
- The page remains inside the main Xianyu publish flow and keeps the standard `发闲置` header, so
  header-based heuristics alone are not enough.
- Verifying the `已选中...` chip is more reliable than assuming the tap succeeded from timing alone.

## Files
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
