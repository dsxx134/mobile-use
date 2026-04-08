# xianyu mcp will live in a separate thin-wrapper repo

Date: 2026-03-15

## Decision
- Do not keep the final Xianyu MCP product inside `mobile-use`.
- Keep `mobile-use` as the execution core.
- Build a separate repository under the user's GitHub account as a thin wrapper around this core.
- That future repo should contain two MCP services:
  - `xianyu_publish_mcp`
  - `xianyu_debug_mcp`

## Why
- The current repo contains reusable execution internals, not a clean end-user MCP surface.
- A separate wrapper repo makes the MCP product easier to distribute, document, version, and plug
  into other agents without exposing internal implementation details.
- Splitting publish and debug servers reduces accidental use of low-level tap/screen tools during
  normal production publishing, while still keeping full debugging power available for self-use.

## Consequences
- `mobile-use` remains the place where Xianyu execution capabilities are implemented and tested.
- The wrapper repo will mostly define MCP schemas, service wiring, packaging, and operator-facing
  documentation.
- Scheduling is not part of the MCP design; it stays outside and is driven by the caller.
