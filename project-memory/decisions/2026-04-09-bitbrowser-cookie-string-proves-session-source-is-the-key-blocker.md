# bitbrowser cookie string proves session source is the key blocker

Date: 2026-04-09

## Decision
- Treat the collector's remaining live-search blocker as a session-source / session-quality problem rather than a signing-algorithm problem.

## Evidence
- Anonymous bootstrap alone could obtain `_m_h5_tk`, but live search still returned `RGV587_ERROR::SM`.
- Local Chrome / DrissionPage profiles could also obtain `_m_h5_tk`, yet live search still returned `RGV587_ERROR::SM`.
- When a full cookie string copied from the user's logged-in BitBrowser session was written into a copied collector DB and reused by the local collector CLI, `collect keyword --keyword gemini --pages 1` succeeded with `saved=30`.

## Consequence
- Future work should prioritize reusable session acquisition from BitBrowser (or an equivalent strong web session source) before further low-level signing tweaks.
