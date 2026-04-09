# preflight-commands-should-end-at-ready-to-run

Updated: 2026-04-09

## Pattern
- A preflight command should stop as close as possible to the operator's next irreversible action. In this collector, that means ending at "saved is ready to search" rather than merely reporting lower-level state.

## Why
- This reduces decision overhead before a live run.
- Diagnostics remain available separately, but the default preflight path should culminate in a yes/no readiness answer.
