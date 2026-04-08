# drission-auto-port-can-bootstrap-browser-cookies-without-9222

Updated: 2026-04-09

## Pattern
- `DrissionPage.ChromiumOptions.auto_port()` can launch a debuggable Chrome instance and retrieve `_m_h5_tk` without requiring an already-running browser on `9222`.

## Why
- This is closer to the old tool's `reset_cookies()` path than a hard dependency on a pre-opened remote-debugging browser.
- It removes one environment-specific blind spot when debugging collector session acquisition.
