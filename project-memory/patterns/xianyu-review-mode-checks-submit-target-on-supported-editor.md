# xianyu-review-mode-checks-submit-target-on-supported-editor

Updated: 2026-03-14

## Pattern
- Treat review mode as a narrow pre-submit guard:
  - accept only `listing_form` or `metadata_panel`
  - require a visible `submit_listing` target
  - stop there and write the row back as `待人工发布`

## Why
- The prepare slice already proved media, body text, and price entry through deterministic actions.
- The missing safety question before any auto-submit is whether the app still shows a valid editor
- state with a real `发布` target the user could inspect.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
- `scripts/xianyu_publish_review_live.py`
