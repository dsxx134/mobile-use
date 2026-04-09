# compare session sources with one real search probe

Updated: 2026-04-09

## Pattern
- When multiple cookie/session acquisition paths exist, compare them with the same single search probe and classify each source as:
  - `unavailable`
  - `signing-only`
  - `searchable`

## Why
- This keeps diagnosis concrete and operator-friendly.
- It avoids endless argument about tokens or headers by reducing everything to the one business outcome that matters: whether `pc.search` returns usable results.
