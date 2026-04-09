# xianyu collector persists bitbrowser runtime config

Date: 2026-04-09

## Decision
- Persist BitBrowser runtime settings inside the collector DB so the common live-search path no longer depends on ad-hoc CLI flags or shell environment variables.

## Stored Shape
- `gradeConfig["bitbrowser_runtime"] = { browser_id, api_host, api_port }`

## Why
- BitBrowser became the strongest proven session source for real Goofish search.
- Requiring `--bitbrowser-id` on every run was workable but not ergonomic.
- The collector already persists other operator-facing runtime defaults in `gradeConfig`, so the smallest consistent extension was to store BitBrowser runtime settings there too.

## Consequence
- Runtime selection order is now:
  - explicit CLI/env override
  - saved `bitbrowser_runtime` config
  - fallback to non-BitBrowser browser session / anonymous bootstrap
- Operators can save the browser once and then run `doctor session` or `collect keyword` against the same DB without repeating the browser id.
