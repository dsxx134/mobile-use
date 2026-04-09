# ensure-searchable prioritizes business readiness over ttl

Date: 2026-04-09

## Decision
- Add `doctor ensure-searchable` as the primary business-readiness command for the saved-cookie lane.

## Behavior
- Probe whether `saved` is already searchable.
- If yes, keep it and report `repair=not-needed`.
- If not, and BitBrowser config exists, refresh from BitBrowser, overwrite `cookices_str`, and probe `saved` again.

## Why
- The operator usually wants one answer: "现在 saved 这条链能不能直接采？"
- Freshness and compare remain useful diagnostics, but neither is the fastest route to that final operational answer.

## Consequence
- `doctor ensure-searchable` becomes the shortest path to restore business readiness for saved cookies.
