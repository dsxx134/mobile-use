# xianyu photo analysis needs recognizable product images

Updated: 2026-03-13

## Pattern
- Blank placeholders, banners, or non-product-like test images tend to keep Xianyu `photo_analysis` in a `0个宝贝` branch.
- Real product-like images can surface a detected-item branch with a price estimate and an item count such as `1个宝贝`.
- Use a dedicated probe album with recognizable product photos when exploring the transition beyond `photo_analysis`.

## Why it matters
- The automation path beyond `photo_analysis` depends on whether Xianyu detects a product at all.
- Debugging with synthetic images can lead to false conclusions that no downstream branch exists.

## Applies to
- real-device exploration on the Huawei tablet
- future smoke or fixture design for Xianyu publish automation
