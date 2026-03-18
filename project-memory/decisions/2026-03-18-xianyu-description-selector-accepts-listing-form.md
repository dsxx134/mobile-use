# xianyu description selector accepts listing form

Date: 2026-03-18

## Decision
- When description text is set via selector-based UIAutomator calls, accept a return to
  `listing_form` or `metadata_panel` as success if the description text is visibly present.

## Why
- On the Huawei tablet, tapping the description entry can occasionally no-op and stay on
  `listing_form`, yet direct selector input can still inject the text and surface it immediately.
- Requiring a `description_editor` transition caused prepare runs to fail even though the text was
  written correctly.

## Consequences
- The description helper now short-circuits after selector input when text is visible on the
  listing form.
- This reduces flaky failures without weakening the text-visibility check.
