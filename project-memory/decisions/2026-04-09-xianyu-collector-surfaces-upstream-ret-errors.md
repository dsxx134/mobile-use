# xianyu collector surfaces upstream ret errors

Date: 2026-04-09

## Decision
- The collector API layer should treat upstream `ret` failures and login-redirect payloads as explicit errors instead of silently returning empty search results.

## Applied behavior
- `RGV587` / `被挤爆啦` now raises a burst-style collector exception.
- `系统错误请稍候再试` now raises a retryable system exception.
- `passport.goofish.com` redirect payloads without a stronger `ret` signal now raise a login-redirect exception.
- CLI catches these collector exceptions, prints a clear `collector error: ...` message, and returns exit code `2`.

## Why
- Real live tests proved that the old collector path can receive HTTP 200 + JSON while still being blocked by upstream session or anti-bot checks.
- Treating those responses as empty results hides the actual failure mode and wastes debugging time.
