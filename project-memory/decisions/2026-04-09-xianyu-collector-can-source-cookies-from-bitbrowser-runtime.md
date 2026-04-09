# xianyu collector can source cookies from bitbrowser runtime

Date: 2026-04-09

## Decision
- Allow the Xianyu collector runtime to prefer a logged-in BitBrowser instance as its browser-cookie source whenever a browser id is provided through environment variables.

## Why
- Live BitBrowser evidence showed that the decisive gap was session quality, not signing math.
- Manually copying the BitBrowser cookie string into a DB proved the collector could immediately collect `gemini` results, but that path was operationally clumsy.
- The collector already had a browser-cookie abstraction, so the smallest durable change was to add a BitBrowser-backed `BrowserSession` implementation and let runtime select it before weaker browser/anonymous sources.

## Consequence
- Operators can now run live collection with:
  - `XIANYU_COLLECTOR_BITBROWSER_ID`
  - or the existing BitBrowser-style `BIT_BROWSER_ID`
- Runtime cookie acquisition order is now:
  - saved cookie string
  - BitBrowser session when configured
  - Drission browser session otherwise
  - anonymous bootstrap as last resort
