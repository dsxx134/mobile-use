# bitbrowser open may need retry while browser is opening

Updated: 2026-04-09

## Pattern
- When opening a BitBrowser instance through the local API, treat `浏览器正在打开中` as a transient state and retry before declaring the browser session unavailable.

## Why
- The browser may already be spinning up even though the first `/browser/open` call returns a non-success payload.
- Without a retry, session acquisition becomes flakier than the actual browser state warrants.
