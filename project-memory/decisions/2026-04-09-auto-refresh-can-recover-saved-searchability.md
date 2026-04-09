# auto-refresh can recover saved searchability

Date: 2026-04-09

## Decision
- Treat `doctor freshness --refresh-from-bitbrowser-if-needed` as the first-line recovery action when the saved-cookie path is missing, stale, or expired.

## Why
- A fresh BitBrowser session can now be copied into `cookices_str` automatically.
- Live validation showed that after auto-refresh:
  - `doctor freshness` reports `status=fresh`
  - `doctor compare` immediately shows `source=saved status=searchable`

## Consequence
- The operator no longer needs to manually chain:
  - `sync-cookie-from-bitbrowser`
  - `doctor freshness`
  - `doctor compare`
- The preferred low-noise recovery command is now the single auto-refresh freshness check.
