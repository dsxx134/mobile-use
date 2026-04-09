# xianyu collector can refresh saved cookie from bitbrowser

Date: 2026-04-09

## Decision
- Add `config sync-cookie-from-bitbrowser` so the collector can copy the current BitBrowser session cookie string into `gradeConfig["cookices_str"]`.

## Why
- BitBrowser is the strongest proven live session source, but keeping it as the only online source is unnecessarily brittle.
- The collector already knows how to use a saved cookie string first, and a full cookie string copied from BitBrowser was previously proven to make saved-cookie search succeed.
- This command turns that proof into a repeatable operator action.

## Consequence
- The saved-cookie path can now be actively refreshed instead of being treated as stale legacy state.
- A practical workflow is now:
  1. `config set-bitbrowser`
  2. `config sync-cookie-from-bitbrowser`
  3. use `saved` as the first session source
