# xianyu collector lives as an isolated subpackage

Date: 2026-04-09

## Decision
- Integrate the recovered Xianyu collection capability into `mobile-use` as a separate vendored package under `minitap/mobile_use/collectors/xianyu_collector/`.
- Keep the collector isolated from `scenarios/xianyu_publish/` instead of merging the two codepaths immediately.

## Context
- The recovered collector is API-driven and centered on cookies, MTOP signing, filtering, and SQLite persistence.
- The existing `mobile-use` Xianyu stack is device-automation-first and centered on publish flows.
- Forcing both into one abstraction too early would couple an API collector to an Android UI runner and make validation harder.

## Consequences
- Collector tests can evolve independently from publish-flow tests.
- The collector can expose its own CLI entrypoint without affecting the publish stack.
- Any later MCP or orchestration layer should call the collector package as a distinct subsystem.
