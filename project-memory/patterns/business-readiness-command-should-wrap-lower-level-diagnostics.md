# business-readiness-command-should-wrap-lower-level-diagnostics

Updated: 2026-04-09

## Pattern
- Once low-level diagnostic primitives are stable, expose a higher-level command that answers the business question directly instead of forcing operators to mentally compose multiple subcommands.

## Why
- Here the low-level pieces were:
  - freshness diagnosis
  - BitBrowser sync
  - searchability probe
- The operator-facing question is simpler: "make saved usable for collection now, and tell me whether it worked."
