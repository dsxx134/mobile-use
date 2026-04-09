# saved cookie freshness comes from m-h5-tk expiry suffix

Date: 2026-04-09

## Decision
- Add `doctor freshness` and derive saved-cookie freshness directly from the `_m_h5_tk` expiry suffix.

## Rule
- `fresh`: remaining TTL > 30 minutes
- `stale`: 0 < remaining TTL <= 30 minutes
- `expired`: remaining TTL <= 0
- `missing-signing-token`: no `_m_h5_tk`
- `unknown-expiry-format`: `_m_h5_tk` does not end with a numeric expiry suffix

## Why
- The saved-cookie path is now operational again after `sync-cookie-from-bitbrowser`, so operators need a quick way to judge whether that cached session is still worth trusting.
- `_m_h5_tk` already carries the best locally available expiration hint; no extra upstream call is needed.

## Consequence
- Operators can now separate two questions:
  - "能不能搜" via `doctor compare` / `doctor session`
  - "这个 saved cookie 还新不新" via `doctor freshness`
