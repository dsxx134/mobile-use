# browser-page-itself-can-show-session-expired-on-goofish-search

Updated: 2026-04-09

## Pattern
- A real browser page on `https://www.goofish.com/search?...` can itself emit network calls that return `FAIL_SYS_SESSION_EXPIRED` and the main search request can still return `RGV587_ERROR::SM` with a mini-login redirect.

## Why
- This proves the blocker is not necessarily in the collector's handcrafted request path.
- If the browser page itself is already in a weak or expired web session state, reproducing the exact API call outside the page will not fix search by itself.
