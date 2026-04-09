# xianyu collector exposes bitbrowser and session doctor in cli

Date: 2026-04-09

## Decision
- Expose BitBrowser session selection directly in the collector CLI with `--bitbrowser-id`, `--bitbrowser-api-host`, and `--bitbrowser-api-port`.
- Add a non-mutating `doctor session` CLI command that classifies the current session as either:
  - `searchable`
  - or `signing-only`

## Why
- The runtime already knew how to consume BitBrowser once the right env vars were present, but that was too implicit for repeatable operator use.
- Live debugging needed a low-noise command that answers the concrete question: "当前这套 cookie 只是能签名，还是已经能真实搜索？"
- The most reliable diagnosis path is to issue a single real `pc.search` request without writing any collected rows.

## Consequence
- Operators no longer need to export env vars manually for the common BitBrowser path.
- Session triage is now explicit:
  - success prints the resolved cookie source plus item count
  - upstream block prints `session=signing-only` plus the upstream reason
