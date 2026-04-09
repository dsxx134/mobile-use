# bitbrowser-logged-in-cookie-string-can-unblock-live-collector-search

Updated: 2026-04-09

## Pattern
- A collector request path that still fails with `RGV587_ERROR::SM` under bootstrap or weak browser cookies may immediately start working when supplied with a full cookie string from a genuinely logged-in BitBrowser session.

## Why
- This is strong evidence that the missing ingredient is not just `_m_h5_tk`, but the broader authenticated web session state carried by cookies such as `unb`, `sgcookie`, `tracknick`, and related Taobao/Goofish session cookies.
