# default-run-parameters-belong-with-stable-operator-config

Updated: 2026-04-09

## Pattern
- If a run parameter is repeatedly chosen the same way by the operator and is safe to reuse across sessions, store it alongside the rest of the stable collector configuration and let explicit CLI flags override it.

## Why
- This keeps the CLI concise for routine runs while preserving explicit escape hatches for one-off deviations.
