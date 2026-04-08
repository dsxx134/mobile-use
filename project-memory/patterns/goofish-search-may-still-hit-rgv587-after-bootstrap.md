# goofish-search-may-still-hit-rgv587-after-bootstrap

Updated: 2026-04-09

## Pattern
- Anonymous bootstrap can successfully obtain `_m_h5_tk` / `_m_h5_tk_enc`, but the search API may still return `RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!` with a mini-login redirect payload.

## Why it matters
- This means "has signing token" is not the same as "has a usable authenticated collector session".
- Live collector tests should inspect `ret` and not silently treat these responses as empty search results.
