# unified xianyu cli wraps collector and publish surfaces

Date: 2026-04-10

## Decision
- Add a unified operator entrypoint `mobile-use-xianyu` that dispatches to the existing collector and publish-oriented CLIs.

## Scope
- `collector`
- `prepare`
- `review`
- `publish`
- `publish-auto`
- `publish-schedule`

## Why
- The repo now exposes enough separate Xianyu commands that operators benefit from one discoverable top-level surface.
- The underlying collector and publish CLIs were already stable, so a thin dispatcher is lower risk than building another orchestration layer.

## Consequence
- The unified command becomes the ergonomic shell-facing entrypoint.
- Subcommands continue to reuse the existing specialized CLIs and their tests.
