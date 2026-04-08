# xianyu post confirm needs album picker tail polling

Updated: 2026-03-13

## Pattern
- After tapping `确定` in the Xianyu media picker, Huawei tablet runs can remain on an album-picker tail state that still shows `预览 (1)` and `确定`.
- Treat that lingering picker as transitional, not as a successful post-confirm result.
- Keep polling until the flow leaves `album_picker` and reaches a downstream screen such as `photo_analysis`.
- If it never leaves the picker within the poll budget, raise a clear error instead of silently returning the wrong screen.

## Why it matters
- Returning the lingering picker snapshot makes `select_cover_image()` look successful while the app is still transitioning.
- Real-device behavior differs from the fake snapshots that jump directly from confirm to the next screen.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- any future Xianyu media-confirm flow that waits for downstream state after `album_confirm`
