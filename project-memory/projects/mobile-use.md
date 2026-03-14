# mobile-use

Updated: 2026-03-14
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
- Xianyu publish flow batch 11 completed on `feat/android-debug-mcp`: post-`继续` draft-resume polling, a deterministic `XianyuPrepareRunner`, and a business-layer decision to fold `ListingDraft.title` into the description body because the portrait form does not expose a separate title field on this Huawei tablet.
- Xianyu publish flow batch 12 completed on `feat/android-debug-mcp`: stale home/chooser wait handling, selected-media preview and media-edit recognition, and real-device verification that the prepare runner can now return to `listing_form` after image selection on the Huawei tablet.
- Xianyu publish flow batch 13 completed on `feat/android-debug-mcp`: metadata/spec-panel recognition, deterministic `成色` and `商品来源` chip selection, optional Feishu mapping for those fields, and real-device verification that the metadata page is distinct from `publish_chooser`.
- Xianyu publish flow batch 14 completed on `feat/android-debug-mcp`: visible metadata-panel category chip extraction, optional Feishu `分类` mapping, prepare-runner category application, and real-device verification that `set_item_category('生活百科')` flips the selected category chip while staying on `metadata_panel`.
- Xianyu publish flow batch 15 completed on `feat/android-debug-mcp`: scrolled metadata-editor recovery, lower-row target extraction inside `metadata_panel`, and real-device verification that `选择位置` still opens `location_panel` from that state while top-level region selection remains hierarchical.
- Xianyu publish flow batch 16 completed on `feat/android-debug-mcp`: hierarchical location-region path helper, post-district tail polling for `location_region_picker`, and real-device verification that `上海 -> 上海 -> 黄浦区` returns through a transient picker tail before settling back to the editor.
- Xianyu publish flow batch 17 completed on `feat/android-debug-mcp`: dedicated location-search-screen recognition, focused-EditText address entry through `set_text()`, visible result-row selection, and real-device verification that `搜索地址 -> 上海虹桥站` returns to the editor even though visible location writeback is still unresolved.
- Xianyu publish flow batch 18 completed on `feat/android-debug-mcp`: optional Bitable `预设地址` mapping, runner integration for best-effort `搜索地址` application, and preservation of the boundary that visible location writeback remains unresolved after the helper returns.
- Xianyu publish flow batch 19 completed on `feat/android-debug-mcp`: a dedicated Feishu Bitable app named `闲鱼自动发布联调` was created under the user's account, seeded with the Xianyu field set plus one safe test row, the worktree `.env` was populated with the app/table tokens, and `XianyuPrepareRunner` now writes `准备中 / 已就绪 / 准备失败` plus `失败原因` back to Bitable.
- Xianyu publish flow batch 20 completed on `feat/android-debug-mcp`: live Feishu compatibility fixes switched record lookup to `POST /records/search`, switched attachment downloads to record URLs plus bearer auth, normalized Feishu text-array fields, treated `metadata_panel` as a valid post-description/post-price editor state, downgraded `商品来源/预设地址` to best-effort when those controls are off-screen, and achieved a real Feishu-backed prepare run ending on `metadata_panel` with the row written back as `已就绪`.
- Xianyu publish flow batch 21 completed on `feat/android-debug-mcp`: the verified live Feishu-backed prepare path is now codified in `scripts/xianyu_prepare_runner_live.py`, Android serial selection can come from `XIANYU_ANDROID_SERIAL`, the live preheat retries once against Huawei-tablet startup flakiness, description entry now polls through a `metadata_panel` tail after tapping from the scrolled editor slice, and a fresh real-device script run again ended on `metadata_panel` with the row written back as `已就绪`.
- Xianyu publish flow batch 22 completed on `feat/android-debug-mcp`: a non-submitting review mode now checks that the final editor is still `listing_form` or `metadata_panel` and that a visible `发布` target remains, writes the row back as `待人工发布`, adds future-facing Bitable fields (`允许自动发布 / 闲鱼商品ID / 闲鱼商品链接 / 发布时间`), introduces `scripts/xianyu_publish_review_live.py`, adds a basic `publish_success` analyzer shape, and was real-device verified on `E2P6R22708000602` with the Feishu row `recvdOzzR38eVi` ending in `待人工发布`.

## Operational Rule
- Important milestones should be committed and pushed to GitHub instead of remaining only local.
- Use only repositories under the user's GitHub account as active remotes for this project.
- Default push target is personal `origin`; if a writable repo is needed, create or reuse one under `dsxx134`.
- Do not add or sync the original repository unless the user explicitly asks for it.
