# profiles-should-capture-intent-not-ephemera

Updated: 2026-04-09

## Pattern
- When adding profiles around an automation workflow, store durable intent/configuration and exclude volatile session artifacts unless the whole point of the profile is session replay.

## Why
- Durable config is portable and safe to reuse.
- Volatile session data ages quickly and creates confusing restores if mixed into the same snapshot abstraction.
