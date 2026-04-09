# ensure-searchable is the shortest preflight path

Date: 2026-04-09

## Decision
- Treat `doctor ensure-searchable` as the default preflight command before running collection when session uncertainty exists.

## Why
- It answers the business question directly: whether the saved-cookie lane is usable for real search right now.
- It already wraps the necessary repair behavior:
  - detect saved failure
  - refresh from BitBrowser when possible
  - re-prove searchability of `saved`

## Consequence
- Operators no longer need to manually choose among `freshness`, `sync-cookie-from-bitbrowser`, and `compare` in the common case.
- Those lower-level commands remain as diagnostics, while `ensure-searchable` becomes the operational default.
