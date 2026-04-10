# unified-operator-clis-should-dispatch-not-reimplement

Updated: 2026-04-10

## Pattern
- When multiple stable CLIs already exist for adjacent workflows, build the unified operator command as a thin dispatcher that forwards argv to those CLIs rather than duplicating their argument parsing or business logic.

## Why
- This keeps one source of truth for each specialized workflow.
- It lowers regression risk because existing tests and semantics stay attached to the original CLIs.
