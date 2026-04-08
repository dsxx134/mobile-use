# xianyu auto publish requires explicit row opt-in

Date: 2026-03-14

## Decision
- Automatic Xianyu submission is not enabled by default after a successful prepare run.
- A row must explicitly opt in through the Bitable checkbox field `允许自动发布`.
- The runner should still require the same guarded pre-submit checks as review mode:
  - final screen is `listing_form` or `metadata_panel`
  - a visible `submit_listing` target is present

## Why
- Real-device publish is materially riskier than prepare-only or manual-review mode.
- The project already proved that location writeback and some editor transitions can still be
  best-effort, so a second explicit business-level gate is warranted even after the row is already
  marked `是否允许发布`.
- Reusing the review gate keeps the submit step deterministic instead of introducing a new
  free-form publish branch.

## Consequences
- Live automation can safely support both:
  - `待人工发布` review mode
  - controlled `已发布 / 发布失败` auto-publish mode
- Operators must intentionally enable auto-publish per listing instead of assuming prepare success
  implies submission is allowed.
