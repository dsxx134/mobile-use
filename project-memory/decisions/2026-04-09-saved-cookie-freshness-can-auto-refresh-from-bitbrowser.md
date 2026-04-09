# saved cookie freshness can auto-refresh from bitbrowser

Date: 2026-04-09

## Decision
- Extend `doctor freshness` with `--refresh-from-bitbrowser-if-needed`.

## Behavior
- If saved cookie is already `fresh`, do not touch BitBrowser and report `refresh=not-needed`.
- If saved cookie is not `fresh` and BitBrowser config is available, pull a fresh cookie string from BitBrowser, overwrite `cookices_str`, and re-run the freshness check.

## Why
- The operator usually cares less about the abstract freshness verdict than about whether the tool can repair stale saved state automatically.
- We already had the primitives:
  - saved-cookie freshness diagnosis
  - bitbrowser sync into saved cookie
- The smallest useful next step was to connect them.

## Consequence
- `doctor freshness` is now both a diagnosis tool and a low-noise self-healing path for the saved-cookie layer.
