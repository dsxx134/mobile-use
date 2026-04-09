# proxy-source-can-fail-with-whitelist-json-error

Updated: 2026-04-09

## Pattern
- Some legacy proxy sources return JSON business errors instead of `host:port` lines, for example a whitelist failure such as `{"code":10101,"msg":"...未匹配到对应白名单用户名!"}`.

## Why
- Treating this as a generic `invalid proxy format` loses the actual operational cause.
- The collector should surface the upstream proxy-service message directly when possible.
