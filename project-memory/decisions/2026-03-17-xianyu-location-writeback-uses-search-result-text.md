# xianyu location writeback uses search result text

Date: 2026-03-17

## Decision
- Treat the tapped location-search result text as the authoritative location value even when the
  editor still shows `选择位置`.
- Normalize the selected result into a single-line value and write it back to the Bitable
  `预设地址` field during prepare completion.
- Allow `require_location_written_on_editor()` to accept a supplied `selected_location` value as
  proof of clearance.

## Why
- Real-device UI dumps show the location panel exposes stable, selectable search results, but the
  listing form does not reliably render a location confirmation row in accessibility text.
- The location-search result is the most reliable, user-aligned value available to confirm what
  was selected.
- Writing the normalized value back to `预设地址` preserves the selected address for later runs.

## Consequences
- Location panel detection no longer requires the `请选择宝贝所在地` row, because some builds omit it.
- Publish/review gating continues to enforce location clearance, but the captured search result
  now satisfies the gate when the form still renders `选择位置`.

## Supersedes
- Partially supersedes `2026-03-14-xianyu-location-stays-out-of-runner-until-writeback-is-visible.md`.
- Updates the gate behavior described in
  `2026-03-15-xianyu-review-and-auto-publish-now-require-location-clearance.md`.
