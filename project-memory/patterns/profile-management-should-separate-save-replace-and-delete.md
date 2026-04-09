# profile-management-should-separate-save-replace-and-delete

Updated: 2026-04-09

## Pattern
- Treat profile lifecycle operations as distinct actions:
  - save new profile
  - replace existing profile only with explicit opt-in
  - delete profile explicitly

## Why
- This keeps operator intent visible in the command line and reduces accidental configuration loss.
