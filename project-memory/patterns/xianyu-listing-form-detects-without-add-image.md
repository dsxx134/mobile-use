# xianyu listing form detects without add image

Date: 2026-03-19

## Pattern
- The listing-form detector should still classify `listing_form` when the image tile is
  off-screen and `添加图片` is not visible, as long as the description entry plus
  `价格设置/发货方式` rows are visible.

## Why it matters
- The editor is scrollable; after filling data, the image area may be scrolled away.
- Misclassifying this scrolled state as `publish_chooser` blocks location or other steps.
