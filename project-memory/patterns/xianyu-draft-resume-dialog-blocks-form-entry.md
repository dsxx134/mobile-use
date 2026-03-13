# xianyu draft resume dialog blocks form entry

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, tapping `发闲置` can surface a blocking draft-resume dialog instead of opening the portrait listing form directly.
- The dialog exposes `放弃` and `继续`; the deterministic recovery path is to tap `继续`.
- `advance_to_listing_form()` should treat this dialog as a first-class screen rather than falling back to blind home recovery.

## Why it matters
- Without this branch, the flow loops back to home and fails to reach the form whenever Xianyu has an unfinished draft.
- Real-device probing confirmed the exact path: `home -> publish_chooser -> draft_resume_dialog -> listing_form`.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- real-device automation on `E2P6R22708000602`
