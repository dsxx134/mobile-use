# exported-profile-format-should-be-human-readable-and-versioned

Updated: 2026-04-09

## Pattern
- When exporting operator configuration, prefer a human-readable JSON envelope with an explicit format version instead of dumping raw internal storage blobs.

## Why
- It makes the file easy to inspect, diff, and repair manually.
- A version field leaves room for future migration logic without changing the outer contract.
