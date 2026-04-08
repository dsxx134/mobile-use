# vendor-recovered-subsystems-under-mobile-use-collectors

Updated: 2026-04-09

## Pattern
- When bringing a recovered or reverse-engineered subsystem into `mobile-use`, vendor it as a self-contained package under `minitap/mobile_use/collectors/` first.
- Rewrite imports and tests to the new namespace, but preserve the subsystem's internal layering.

## Why
- Keeps the recovered code testable without immediately coupling it to unrelated mobile automation abstractions.
- Makes it easy to expose a dedicated CLI or future MCP wrapper.
- Preserves a clean seam for later refactors once runtime parity is proven.
