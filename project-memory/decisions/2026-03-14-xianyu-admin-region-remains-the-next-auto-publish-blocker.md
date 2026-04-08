# xianyu admin region remains the next auto publish blocker

Date: 2026-03-14

## Decision
- Keep `预设地址 -> 搜索地址` as a best-effort helper, but do not treat it as sufficient proof that
  Xianyu location is publish-ready.
- Treat the new live post-submit modal about missing administrative region as the primary blocker
  for the next batch of work.
- Do not broaden auto-publish heuristics past this point until the location row or submit path
  shows deterministic administrative-region writeback.

## Why
- Real-device auto-publish now reaches the actual `发布` tap and surfaces a precise in-app failure
  dialog instead of an ambiguous `unknown` result.
- That dialog proves the remaining issue is not generic submit instability; it is specifically the
  missing administrative-region selection that Xianyu enforces at publish time.

## Consequences
- Feishu rows now get a much more useful `发布失败` reason for this class of submit failure.
- The next implementation slice should focus on making location writeback visible and durable,
  rather than expanding other metadata automation first.
