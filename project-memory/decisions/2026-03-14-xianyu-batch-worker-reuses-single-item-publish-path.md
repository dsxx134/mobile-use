# xianyu batch worker reuses single item publish path

Date: 2026-03-14

## Decision
- Build queue publishing as a thin live-layer loop around
  `prepare_first_publishable_listing_live(..., auto_publish_after_prepare=True)`.
- Do not introduce a second orchestration path for batch mode.

## Why
- The single-item path already contains the hard-won preheat, prepare, publish, receipt, and
  Feishu writeback logic.
- Reusing that path keeps queue mode small, easier to verify, and less likely to diverge from the
  already validated publish flow.

## Consequences
- Batch mode inherits the same gating and writeback behavior as the single-item live runner.
- Future publish fixes only need to land in the single-item path to benefit both entrypoints.
