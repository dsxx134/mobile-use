# collector profiles store stable config not volatile sessions

Date: 2026-04-09

## Decision
- Add minimal collector profiles with `save-profile`, `load-profile`, and `list-profiles`.
- Profiles intentionally store only stable operator configuration, not volatile session state.

## Stored Fields
- proxy config
- BitBrowser runtime config
- gather conditions
- selected gather type
- gather type inputs
- region list string

## Excluded
- saved cookie string (`cookices_str`)

## Why
- Profiles should be reusable setup snapshots, not stale session containers.
- Session state already has its own dedicated lifecycle through:
  - `sync-cookie-from-bitbrowser`
  - `doctor freshness`
  - `doctor ensure-searchable`

## Consequence
- Operators can switch stable collector setups quickly without dragging old cookies across contexts.
