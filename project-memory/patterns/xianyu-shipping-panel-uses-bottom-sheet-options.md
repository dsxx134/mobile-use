# xianyu shipping panel uses bottom-sheet options

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, tapping `发货方式` from the portrait `发闲置` form opens a `shipping_panel` bottom sheet.
- The multiline `邮寄` block is descriptive text, not the true deterministic tap target.
- The reliable selectable controls are the left-side radio-icon `ImageView` elements aligned with the mail modes:
  - `包邮`
  - `不包邮-按距离付费`
  - `不包邮-固定邮费`
  - `无需邮寄`

## Why it matters
- Tapping the text rows can leave the mode unchanged, even though the panel looks correct.
- Real-device probing showed that tapping the radio-icon column successfully changed `无需邮寄` and `包邮`, while the visible `买家自提` text target did not prove reliable.
- After `确定`, the app can briefly expose either a stale `shipping_panel` or a status-only `unknown` overlay before returning to `listing_form`.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- real-device automation on `E2P6R22708000602`
