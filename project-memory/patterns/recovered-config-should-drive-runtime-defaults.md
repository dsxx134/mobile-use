# recovered-config-should-drive-runtime-defaults

Updated: 2026-04-09

## Pattern
- When a recovered subsystem already has a persisted config shape, integrate that config into runtime defaults before adding new configuration surfaces.

## Why
- It makes reused databases immediately valuable.
- It keeps reverse-engineered semantics visible and testable.
- It avoids creating a second competing configuration model too early.
