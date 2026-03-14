# xianyu-description-entry-needs-tail-polling

Updated: 2026-03-14

## Pattern
- After tapping the description tile from a scrolled `metadata_panel`, treat
  `listing_form`, `metadata_panel`, and `unknown` as transitional states and keep polling until the
  app either reaches `description_editor` or clearly lands somewhere unsupported.

## Why
- On the Huawei tablet, opening the description editor from the metadata slice is not an immediate
  transition. The first post-tap snapshot can still look like the same `metadata_panel` even though
  the editor appears one or two frames later.
- Failing on that first tail frame makes the live prepare runner mark a row as `准备失败` even
  though the app is still following the correct path.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
