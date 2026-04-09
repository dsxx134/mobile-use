# bitbrowser local api can feed collector browser cookies

Updated: 2026-04-09

## Pattern
- When Goofish search is blocked by weak session quality, use the BitBrowser local API (`/browser/open`) plus CDP `Network.getCookies` against the active logged-in page target instead of manually copying cookie strings.

## Why
- The BitBrowser instance already holds the stronger web session that the page itself uses successfully.
- Reusing that session through the collector's browser-cookie abstraction avoids brittle one-off DB edits while keeping the collector's normal fallback chain intact.
