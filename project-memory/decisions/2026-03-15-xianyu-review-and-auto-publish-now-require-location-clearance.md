# xianyu review and auto publish now require location clearance

Date: 2026-03-15

## Decision
- Keep `预设地址 -> 搜索地址` as the business path for automation-driven location entry.
- Add an explicit editor-side location clearance check before:
  - review mode marks a row `待人工发布`
  - auto-publish continues to the final submit
  - a preset-address run is considered prepared successfully after location search

## Why
- The user explicitly raised the requirement that `所在地址` must be written, not just attempted.
- The current Xianyu UI still contains cases where location search returns to the editor while the
  lower row still shows `选择位置`.
- That makes address entry too risky to keep as a silent best-effort step for publish-facing paths.

## Consequence
- `XianyuPublishFlowService.require_location_written_on_editor()` now treats a visible
  `location_entry` target as proof that location is still unset.
- Review and auto-publish paths fail early if the editor still exposes `选择位置`.
- A prepare-only run can still stop on `metadata_panel`, but any publish-facing path must clear the
  location gate first.

## Supersedes
- This partially supersedes
  `2026-03-14-xianyu-runner-can-apply-best-effort-location-search-query.md`
  by narrowing that best-effort behavior to non-publish-facing prepare runs.
