# chrome-profiles-may-still-only-yield-minimal-goofish-cookies

Updated: 2026-04-09

## Pattern
- Even when iterating local Chrome profiles with `DrissionPage` and the system user data path, the Goofish page may still only expose a minimal cookie set such as `_m_h5_tk`, `cookie2`, and `_tb_token_`.

## Why
- This means the blocker may not be "we failed to open the right Chrome profile"; the profile itself may simply not hold a stronger authenticated Goofish/Taobao session for web search.
- If live requests still hit `RGV587` after this step, look beyond the port/profile assumption.
