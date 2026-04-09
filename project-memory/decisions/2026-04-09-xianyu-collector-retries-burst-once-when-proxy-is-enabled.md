# xianyu collector retries burst once when proxy is enabled

Date: 2026-04-09

## Decision
- When the collector receives a burst-style upstream response (`RGV587` / `被挤爆啦`) and proxy mode is enabled, clear the cached proxy and retry the same request once.

## Why
- This matches the most important branch of the original tool's search behavior without copying its full recursive retry loop yet.
- It is the smallest safe step toward old parity and keeps failure handling observable in tests.
