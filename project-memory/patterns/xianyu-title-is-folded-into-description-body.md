# xianyu title is folded into description body

Updated: 2026-03-13

## Pattern
- On the Huawei tablet's portrait `发闲置` form, the accessibility tree does not currently expose a separate title input.
- The deterministic business workaround is to fold `ListingDraft.title` into the prepared body text:
  - first line = title
  - blank line
  - original description
- If the original description already starts with the exact title, do not duplicate it.

## Why it matters
- The Bitable source still provides a distinct `商品标题` field, so the automation needs a deterministic place to preserve it.
- Keeping the merge logic pure and reusable lets the runner produce stable body text without baking UI assumptions into Feishu parsing.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`
- real-device automation on `E2P6R22708000602`
