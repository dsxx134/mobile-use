# collector profiles can be exported as json

Date: 2026-04-09

## Decision
- Add `export-profile` and `import-profile` to move stable collector setups across machines or DB files.

## Format
- JSON with:
  - `format_version`
  - `name`
  - `profile`

## Why
- Profiles became valuable enough that keeping them trapped inside one local DB was too limiting.
- JSON is the smallest interoperable format for manual inspection and transfer.

## Consequence
- Operators can now:
  - export a stable setup to a file
  - delete or recreate local DB state
  - import that setup back with optional rename/overwrite
