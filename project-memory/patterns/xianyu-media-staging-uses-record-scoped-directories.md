# xianyu-media-staging-uses-record-scoped-directories

Updated: 2026-03-12

## Rule
- Stage downloaded listing media under a directory named after the Bitable `record_id`.
- Prefix staged filenames with a stable index like `01_`, `02_`, then push them to a matching Android subdirectory.

## Why
- Keeps per-listing assets isolated and reproducible.
- Prevents filename collisions when multiple listings reuse generic names like `1.jpg`.
- Makes later publish-state debugging easier because local and remote image order stay aligned.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/media_sync.py`
