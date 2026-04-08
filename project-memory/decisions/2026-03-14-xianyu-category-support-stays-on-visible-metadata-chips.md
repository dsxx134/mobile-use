# xianyu category support stays on visible metadata chips

Date: 2026-03-14

## Decision
- Scope the first deterministic Xianyu category implementation to the category chips already visible
  on `metadata_panel`, instead of trying to automate a deeper category tree or search flow.

## Why
- Real-device probing on the Huawei tablet showed that visible category chips behave exactly like
  the verified `成色` and `商品来源` chips:
  - taps stay on `metadata_panel`
  - the selected chip flips from `可选...` to `已选中...`
- This gives the project a deterministic next slice with low additional complexity.
- A deeper category tree would require a new screen model and a much larger behavior surface.

## Consequences
- `ListingDraft.category` now maps to a visible chip label from Bitable.
- `XianyuPrepareRunner` can apply category when the desired value is visible on the current panel.
- Categories not present as visible chips still remain unsupported for now.
