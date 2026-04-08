# xianyu draft resume continue needs post-tap polling

Updated: 2026-03-13

## Pattern
- After tapping `继续` on the Xianyu draft-resume dialog, the same dialog can remain visible for one or two snapshots before the portrait listing form appears.
- The deterministic flow should poll through both:
  - loading/status-only `unknown` overlays
  - repeated `draft_resume_dialog` snapshots
- Do not treat the first post-tap reappearance of the dialog as a fresh instruction to tap again.

## Why it matters
- Without polling, `advance_to_listing_form()` can double-tap `继续` or exhaust its step budget while still sitting on the dialog tail.
- Real-device probing showed this exact behavior when resuming from arbitrary in-app Xianyu pages such as detail views.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- real-device automation on `E2P6R22708000602`
