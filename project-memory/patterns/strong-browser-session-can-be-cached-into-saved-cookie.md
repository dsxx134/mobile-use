# strong browser session can be cached into saved cookie

Updated: 2026-04-09

## Pattern
- When a live browser session is stronger than the saved-cookie path, provide an explicit sync step that copies the browser cookie string into saved storage so later runs can start from the stronger cookie snapshot.

## Why
- This reduces dependency on live browser connectivity for every run.
- It also makes session diagnosis clearer: after sync, `saved` should move from `unavailable` or `signing-only` to `searchable` if the copied cookie string is still fresh.
