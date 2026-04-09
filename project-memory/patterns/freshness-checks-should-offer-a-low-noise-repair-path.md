# freshness checks should offer a low-noise repair path

Updated: 2026-04-09

## Pattern
- When a freshness diagnostic already has a known safe repair path, expose that repair as an opt-in flag on the same command instead of forcing the operator to manually chain multiple commands.

## Why
- It preserves observability because the diagnosis still runs first.
- It reduces operator friction by collapsing:
  - diagnose stale saved cookie
  - sync from stronger session source
  - re-check freshness
  into one command.
