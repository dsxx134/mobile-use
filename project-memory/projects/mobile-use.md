# mobile-use

Updated: 2026-03-13
Repo: `D:\github\mobile-use`
Status: Active

## Summary
- Python package and CLI for natural-language mobile automation.
- Core execution model is a LangGraph multi-agent pipeline with device controllers and tool execution.
- Current business extension target is Xianyu publishing automation driven by Feishu Bitable.

## Current Milestones
- Repository assessment completed on 2026-03-12.
- Android debugging prerequisites validated on Windows for tablet serial `E2P6R22708000602`.
- Project-local worktree created at `D:\github\mobile-use\.worktrees\android-debug-mcp`.
- Android Debug MCP implementation plan created at `docs/plans/2026-03-12-android-debug-mcp.md`.
- Personal GitHub repo created at `https://github.com/dsxx134/mobile-use` and set as default `origin`.
- Local `main` and `feat/android-debug-mcp` branches pushed to personal `origin` on 2026-03-12.
- Original repository remote removed locally to prevent accidental sync.
- Android Debug MCP batch 1 completed on `feat/android-debug-mcp`: package scaffold, service tests, and FastMCP tool wrappers with structured outputs.
- Android Debug MCP batch 2 completed on `feat/android-debug-mcp`: snapshot ergonomics, smoke script, README usage notes, and full batch verification.
- Smoke script on 2026-03-12 detected two local Android targets: `E2P6R22708000602` and `emulator-5564`.
- Xianyu publish foundation batch 1 completed on `feat/android-debug-mcp`: scenario models/settings, Feishu Bitable source, media staging, Android media push, and foundation smoke script.
- Xianyu publish flow batch 1 completed on `feat/android-debug-mcp`: screen analyzer, explicit-home recovery, deterministic navigation from Xianyu home to album picker, cover-image selection, and flow smoke script.
- Xianyu publish flow batch 2 completed on `feat/android-debug-mcp`: deterministic album-source switching, `photo_analysis` screen recognition, and wait/retry handling for post-select and post-confirm loading gaps.
- Xianyu publish flow batch 3 completed on `feat/android-debug-mcp`: post-confirm album-picker stabilization, real-device verification that `select_cover_image()` now reaches `photo_analysis`, and confirmation that recognizable product images can surface a detected-item branch like `1个宝贝`.
- Xianyu publish flow batch 4 completed on `feat/android-debug-mcp`: `space_items_empty` recognition plus a real-device-verified bridge from `photo_analysis` back into the standard publish chooser through `宝贝 -> 发宝贝`.
- Xianyu publish flow batch 5 completed on `feat/android-debug-mcp`: portrait-mode publish-form recognition, orientation enforcement on the Huawei tablet, and a real-device-verified `advance_to_listing_form()` path that lands directly on the standard Xianyu listing form after tapping `发闲置`.
- Xianyu publish flow batch 6 completed on `feat/android-debug-mcp`: richer portrait-form target extraction from `content-desc`, a deterministic `advance_listing_form_to_album_picker()` bridge, and real-device verification that tapping `添加图片` from the portrait form opens the album picker.
- Xianyu publish flow batch 7 completed on `feat/android-debug-mcp`: `description_editor` recognition, deterministic description entry/fill helpers, and real-device verification that `fill_description()` now returns to `listing_form` on the warmed Huawei tablet.
- Xianyu publish flow batch 8 completed on `feat/android-debug-mcp`: `price_panel` recognition, deterministic sale-price keypad entry from the portrait form, and real-device verification that `fill_price()` returns to `listing_form` with the updated price row.
- Xianyu publish flow batch 9 completed on `feat/android-debug-mcp`: `shipping_panel` recognition, deterministic mail-shipping selection from the portrait form, and real-device verification that `set_shipping_method()` can switch `无需邮寄 -> 包邮` while returning to `listing_form`.
- Xianyu publish flow batch 10 completed on `feat/android-debug-mcp`: draft-resume dialog recovery after tapping `发闲置`, location-chooser and region-picker recognition, and real-device verification that the flow reaches `location_region_picker` from the portrait listing form.

## Operational Rule
- Important milestones should be committed and pushed to GitHub instead of remaining only local.
- Use only repositories under the user's GitHub account as active remotes for this project.
- Default push target is personal `origin`; if a writable repo is needed, create or reuse one under `dsxx134`.
- Do not add or sync the original repository unless the user explicitly asks for it.
