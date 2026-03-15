# xianyu mcp separates publish and debug services

Updated: 2026-03-15

## Pattern
- When productizing the Xianyu automation stack into MCP, use one repo with two MCP servers:
  - `xianyu_publish_mcp` for business operations
  - `xianyu_debug_mcp` for low-level inspection and control

## Why
- Business tools and debug tools have different safety profiles.
- Separating them keeps the normal agent path cleaner and lowers the chance of production misuse.
- For self-use, both services can still ship from the same repo and share the same underlying core.

## Notes
- This pattern assumes the real execution core still lives elsewhere, and the MCP repo is only a
  thin wrapper.
- Scheduling remains external to the MCP layer.
