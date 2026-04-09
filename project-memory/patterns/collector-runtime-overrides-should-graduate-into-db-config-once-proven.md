# collector runtime overrides should graduate into db config once proven

Updated: 2026-04-09

## Pattern
- When a runtime override starts as a CLI/env escape hatch but becomes part of the stable operator workflow, move it into the collector DB config and keep CLI/env only as highest-priority overrides.

## Why
- This keeps one-off experiments cheap at first.
- Once a session source or runtime knob is proven operationally important, persisting it in DB removes repetitive command noise while preserving emergency override capability.
