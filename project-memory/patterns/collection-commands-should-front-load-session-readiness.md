# collection-commands-should-front-load-session-readiness

Updated: 2026-04-09

## Pattern
- Once a session-readiness preflight becomes reliable, collection commands should be able to invoke it before starting business work rather than requiring a separate operator step.

## Why
- This keeps the failure boundary clean:
  - either readiness succeeds and collection starts
  - or readiness fails and collection aborts before any misleading partial work begins
