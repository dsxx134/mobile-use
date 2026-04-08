# xianyu batch summary uses a dedicated table

Date: 2026-03-15

## Decision
- Keep row-level batch traces on the listing table, but store queue-level summaries in a second
  Bitable table named `批次运行汇总`.
- Use one row per worker execution with batch id/time, counts, stop reason, and serialized item
  details.

## Why
- Listing rows answer "what happened to this item last?"
- Batch summaries answer "what happened in this run overall?"
- Separating the two views keeps the main item table readable while still giving operators a
  compact batch audit trail.

## Consequences
- The live queue script must build shared Feishu-backed components so it has a source object
  available for the final summary append.
- The linked Feishu app now needs both:
  - the item table
  - the summary table
- Summary writeback is treated as best effort and reported in the batch JSON result.
