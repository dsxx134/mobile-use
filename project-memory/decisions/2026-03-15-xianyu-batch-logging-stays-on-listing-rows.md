# xianyu batch logging stays on listing rows

Date: 2026-03-15

## Decision
- Implement the first batch-log layer by writing batch metadata back onto each processed listing
  row instead of creating a separate Feishu log table.
- Use three explicit row fields:
  - `最近批次运行ID`
  - `最近批次运行时间`
  - `最近批次运行结果`

## Why
- The current operation loop is still centered on one listing table.
- Row-level batch metadata is enough to answer the immediate operator questions:
  - which worker run touched this row last
  - when it happened
  - what the latest queue-visible result was
- Reusing the existing status/result writeback path keeps queue logging small and low-risk.

## Consequences
- Queue runs have one shared batch id and timestamp per execution.
- Processed rows can be grouped by batch id directly in Feishu.
- Unprocessed rows naturally have no batch stamp for that run.
- If a future dedicated operations dashboard is needed, it can be added later without undoing this
  row-level traceability.
