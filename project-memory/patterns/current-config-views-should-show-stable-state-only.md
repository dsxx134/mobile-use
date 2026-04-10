# current-config-views-should-show-stable-state-only

Updated: 2026-04-10

## Pattern
- A "show current config" command should focus on durable operator-facing state and avoid dumping volatile or sensitive session contents by default.

## Why
- Stable config is what operators need to review, diff, and copy across environments.
- Session contents have separate diagnostics and would add noise or leakage to routine config inspection.
