# show-current exposes stable config snapshot

Date: 2026-04-10

## Decision
- Add `config show-current` as a low-noise JSON snapshot of the collector's stable configuration state.

## Included
- proxy config
- BitBrowser config
- gather conditions
- run defaults
- selected gather type
- remembered gather inputs
- region list string
- known profile names

## Excluded
- volatile session material such as saved cookie contents

## Why
- At this point the collector has enough moving parts that operators need a single command to inspect the current stable setup before exporting profiles or running collection.
