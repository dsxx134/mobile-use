# collector-cli-can-fallback-to-saved-gather-inputs

Updated: 2026-04-09

## Pattern
- When the recovered collector has persisted `gather_type_{n}` text inputs, the CLI can use those values as defaults when explicit command-line inputs are omitted.

## Why
- This preserves the old tool's \"remember my last input per collection mode\" behavior without introducing a separate UI layer first.
- It also makes live debugging easier because a copied legacy DB can drive CLI runs immediately.
