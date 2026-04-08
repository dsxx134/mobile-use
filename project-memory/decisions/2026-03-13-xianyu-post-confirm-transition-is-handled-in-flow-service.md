# xianyu post confirm transition is handled in flow service

Date: 2026-03-13

## Decision
- Handle the Xianyu post-confirm stabilization bug in `XianyuPublishFlowService` instead of changing `XianyuFlowAnalyzer`.
- Keep analyzer output declarative and fix the transition timing with a dedicated post-confirm polling helper in the flow service.

## Rationale
- The root cause is timing: after `album_confirm`, the app can still expose a valid-looking `album_picker` snapshot even though the flow is not done transitioning.
- The analyzer is already correctly identifying the screen it sees; the service was the layer returning too early.
- Polling in the flow service keeps screen classification simple and makes the bug fix easy to test with fake Android snapshots.

## Consequences
- `select_cover_image()` now waits until the flow leaves `album_picker` after confirm.
- The method raises a clear error if the app never leaves the lingering picker tail state.
- Future work that continues from `photo_analysis` can rely on a more stable downstream handoff.
