# xianyu-flow-starts-with-screen-analysis

Updated: 2026-03-12

## Rule
- Keep Xianyu business automation in two layers:
  - a pure screen analyzer that turns raw Android snapshots into a named screen plus tappable targets
  - a flow service that only consumes those named screens and targets

## Why
- It keeps the business flow testable without a live device.
- UI heuristics can evolve without rewriting action sequencing.
- Debugging becomes simpler because "recognition wrong" and "tap order wrong" are separated failures.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
