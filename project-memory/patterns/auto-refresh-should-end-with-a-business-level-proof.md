# auto-refresh should end with a business-level proof

Updated: 2026-04-09

## Pattern
- When adding automatic session repair, don't stop at a low-level freshness signal. Verify that the repaired path also restores the business outcome the operator actually cares about.

## Why
- Fresh TTL alone is not enough.
- In this collector, the meaningful end-state is that `saved` becomes `searchable` again, not just that `_m_h5_tk` has time left.
