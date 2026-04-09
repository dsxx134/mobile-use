# collect can preflight saved searchability

Date: 2026-04-09

## Decision
- Allow `collect manual|keyword|shop` to opt into a saved-cookie preflight via `--ensure-searchable`.

## Behavior
- Before collection starts, the command runs the same saved-cookie readiness logic used by `doctor ensure-searchable`.
- If preflight cannot make `saved` searchable, collection stops before any collection-side API work.
- If preflight succeeds, collection continues with the now-ready saved-cookie path.

## Why
- At this point the preflight path is stable enough that operators should not need a separate manual doctor step in the common case.
- Folding it into `collect` removes an extra decision and keeps the CLI low-noise for routine runs.

## Consequence
- The recommended happy path now becomes:
  - `collect ... --ensure-searchable`
- The standalone doctor commands remain useful for diagnosis and debugging.
