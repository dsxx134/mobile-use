# profile overwrite requires explicit opt-in

Date: 2026-04-09

## Decision
- `save-profile` must reject overwriting an existing profile name unless the operator passes `--overwrite`.

## Why
- Profiles now represent stable collector setups, so silent overwrite is too risky.
- Requiring an explicit override keeps accidental drift from wiping a known-good setup.

## Consequence
- Default save is safe and conservative.
- Replacement remains available, but only as an intentional action.
