# xianyu category selection uses visible chips

Updated: 2026-03-14

## Pattern
- On the Huawei tablet, the first deterministic category implementation should only target category
  chips already visible on `metadata_panel`.
- Treat category selection exactly like other chip-based metadata:
  - tap a `可选<类目>, <类目>` chip
  - stay on `metadata_panel`
  - verify success by observing `已选中<类目>, <类目>`

## Why It Helps
- This avoids over-modeling the deeper Xianyu category system before the current visible path is
  fully reliable.
- The selected-chip text is a much better success signal than timing or assumptions.

## Files
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`
