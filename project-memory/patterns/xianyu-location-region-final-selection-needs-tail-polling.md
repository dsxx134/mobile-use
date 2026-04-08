# xianyu-location-region-final-selection-needs-tail-polling

Updated: 2026-03-14

## Context
- Project: `mobile-use`
- Area: Xianyu publish flow on the Huawei Android tablet `E2P6R22708000602`

## Pattern
- After selecting the final district inside the hierarchical `location_region_picker`, the first
  post-tap screen can still be classified as `location_region_picker` even though the listing form
  is already visible underneath.
- Treat that as a transient tail state, not an immediate failure.
- Poll until the picker overlay leaves before deciding whether the flow returned to the editor.

## Evidence
- Real-device probe path: `上海 -> 上海 -> 黄浦区`
- Intermediate behavior:
  - first `上海` tap narrows the picker to only `上海`
  - second `上海` tap expands district rows such as `黄浦区`
  - final `黄浦区` tap can leave a mixed frame where the editor is visible but the picker overlay is
    still classified as active

## Reuse
- Reapply this same post-action polling pattern whenever a Xianyu sheet or picker can linger after
  the action that logically finishes it.
- This matches earlier stabilization patterns for:
  - album confirm leaving `album_picker`
  - shipping confirm leaving `shipping_panel`
  - draft resume leaving `draft_resume_dialog`

## Boundary
- This pattern only stabilizes the transition away from the picker.
- It does not prove that location selection is visibly persisted on the form or inside the reopened
  `location_panel`.
