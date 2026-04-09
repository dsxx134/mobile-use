# xianyu collector can compare session sources side by side

Date: 2026-04-09

## Decision
- Add `doctor compare` to the collector CLI so the operator can probe the main session sources side by side with one keyword and zero data writes.

## Sources
- `saved`
- `bitbrowser`
- `bootstrap`

## Why
- After BitBrowser was proven to work, the remaining operational question was no longer "能不能采" but "到底是哪条会话链能采，哪条只是能签名".
- Running the same search probe across multiple sources gives a direct answer without mixing collection writes into diagnosis.

## Consequence
- The current live ranking is now explicit on this machine:
  - `saved` -> unavailable when there is no stored signing cookie
  - `bitbrowser` -> searchable
  - `bootstrap` -> signing-only with `RGV587`
