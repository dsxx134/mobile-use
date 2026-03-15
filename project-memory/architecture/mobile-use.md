# mobile-use architecture

Updated: 2026-03-15

## High-Level Structure
- Entry surfaces:
  - CLI in `minitap/mobile_use/main.py`
  - SDK in `minitap/mobile_use/sdk/agent.py`
- Core runtime:
  - LangGraph state machine in `minitap/mobile_use/graph/graph.py`
  - Node chain: planner -> orchestrator -> contextor -> cortex -> executor -> tools -> summarizer
- Device abstraction:
  - Shared protocol in `controllers/device_controller.py`
  - Android and iOS controllers selected via `controllers/controller_factory.py`
- External execution paths:
  - Local devices via ADB/UIAutomator and iOS IDB/WDA
  - BrowserStack support
  - Cloud mobile support
  - Limrun provisioning and controllers

## Current Extension Direction
- Add a repo-local Android debugging MCP that reuses existing Android stack semantics for Xianyu publishing automation.
- The new MCP lives under `minitap/mobile_use/mcp/` and wraps the existing `adbutils` + `UIAutomatorClient` behavior instead of introducing Appium or a second Android control path.
- FastMCP tools should return Pydantic output models so structured output schemas are available to MCP clients.
- `android_debug_get_screen_data` is the primary snapshot tool and now preserves both flattened elements and raw `hierarchy_xml`, plus `element_count`, so debugging clients do not need a second round-trip to inspect structure.
- `scripts/android_debug_mcp_smoke.py` is the local sanity-check entrypoint for confirming that ADB can see connected Android targets before starting the MCP server.
- The Xianyu business layer now lives under `minitap/mobile_use/scenarios/xianyu_publish/` and is intentionally split into:
  - normalized listing models/settings
  - `FeishuBitableSource` for read-only Bitable access and attachment URL resolution
  - `XianyuMediaSyncService` for local staging and Android media push
  - `XianyuFlowAnalyzer` for pure screen classification and tap-target extraction
  - `XianyuPublishFlowService` for deterministic Xianyu navigation built on `AndroidDebugService`
- `XianyuPrepareRunner` for business orchestration across Feishu source, media sync, and the deterministic flow layer
- `live_prepare.py` for the live-device orchestration glue that resolves the Android serial,
  wires authenticated Feishu downloads into media sync, preheats the Huawei tablet back to the
  portrait form, and then delegates to `XianyuPrepareRunner`
- The same runner now has an opt-in review mode that turns a successful prepare slice into a
  guarded manual-publish checkpoint instead of automatic submission.
- The same runner now also has an opt-in auto-publish mode that reuses the exact same prepare
  slice, requires a visible `submit_listing` target, then submits once and waits for
  `publish_success` before writing Bitable publish state.
- The live queue path now writes two levels of Feishu observability:
  - lightweight per-row batch metadata back onto listing rows
  - a dedicated `批次运行汇总` table for batch-level totals and readable per-item detail text
- The live runner now also has a local failure-artifact side channel:
  - capture a fresh Android screenshot through `AndroidDebugService.get_screen_data()`
  - persist `screen.png`, `hierarchy.xml`, and `activities.txt` under `.tmp/xianyu-failures/...`
  - write the resulting local paths back to the listing row in Feishu for operator triage
- The Xianyu flow currently recognizes:
  - home tab
  - publish chooser
  - draft-resume dialog
  - portrait listing form
  - selected-media preview
  - media-edit screen
  - description editor
  - sale-price keypad panel
  - shipping bottom sheet
  - expanded metadata/spec panel
  - location root chooser
  - location region picker
  - Android media permission dialog
  - album picker
  - album source menu
  - photo analysis screen after media confirmation
  - the Xianyu space `宝贝` empty-state page
- On the Huawei tablet used for development, reliable home recovery requires:
  - `am start -n com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity`
  - not just `app_start(package)`, which can reopen a non-home category page
- Deterministic media selection is safer when the flow switches the picker from `所有文件` to a dedicated source folder such as `XianyuPublish`.
- On the Huawei tablet, that dedicated source strategy only stays correct when the automation first clears `/sdcard/DCIM/XianyuPublish`, then pushes the current listing into `/sdcard/DCIM/XianyuPublish/{record_id}`, and finally switches the picker source by that visible `{record_id}` folder name rather than by the static root label `XianyuPublish`.
- The post-confirm destination is currently a `photo_analysis` screen rather than the final listing form, so form filling must build on top of that state instead of assuming the form appears immediately.
- The flow service now tolerates brief blank/loading snapshots after tapping `选择` and `确定` by polling until the next meaningful screen appears.
- On the Huawei tablet, tapping `确定` can leave the app in a transient album-picker tail state that still shows `预览 (1)` and `确定`; `select_cover_image()` now treats that as transitional and waits until the flow leaves the picker.
- `photo_analysis` is a stable downstream state, not just a loading gap. With recognizable product photos it can surface computed price ranges and a detected-item count such as `1个宝贝`, but the final listing form transition is still unresolved.
- On the Huawei tablet, the space-analysis flow includes visual-only controls that are not exposed through the accessibility tree:
  - dismissing the initial analysis overlay
  - tapping the `发宝贝` button on the `宝贝` empty-state page
- The flow service now contains a deterministic bridge from `photo_analysis` into the standard publish chooser by:
  - dismissing the overlay with a ratio tap
  - opening the `宝贝` tab via accessibility target
  - tapping the visual `发宝贝` button with a ratio tap
- The preferred publish path on the Huawei tablet is now portrait-first:
  - disable auto-rotate
  - set `user_rotation=0`
  - open Xianyu home
  - tap `卖闲置`
  - tap `发闲置`
  - if a draft-resume dialog appears, tap `继续`
  - land on the standard portrait listing form
- After tapping draft `继续`, the flow must still tolerate a brief tail where the same dialog is
  visible again before the listing form appears.
- On the real portrait listing form, several actionable controls are surfaced via `content-desc`
  rather than plain `text`, including:
  - `发布, 发布`
  - `添加图片`
  - `描述, 描述一下宝贝的品牌型号、货品来源…`
  - `价格设置`
  - `发货方式`
- The flow service now has a direct bridge from the portrait listing form into the album picker by
  tapping `添加图片` and waiting through the short loading gap or permission dialog until the picker
  becomes stable.
- The flow service now also has a direct description path from the portrait listing form:
  - tap the large description tile
  - enter a dedicated `description_editor` state
  - input text
  - return to the portrait listing form
- On the Huawei tablet, `input_text()` can already collapse the description editor back to
  `listing_form`; the flow must check for that state before tapping any stale `完成` coordinates.
- The flow service now also has a direct sale-price path from the portrait listing form:
  - tap the `价格设置` row
  - enter a dedicated `price_panel` bottom sheet
  - clear the previous value with `删除`
  - tap keypad digits and `.`
  - tap `确定`
  - return to the portrait listing form
- On this Huawei tablet, sale-price entry is driven by the bottom-sheet keypad, not by IME text
  input. Real-device verification showed that tapping `399.9` through the keypad returns to the
  form and renders the row as `¥399.90`.
- The flow service now also has a direct mail-shipping path from the portrait listing form:
  - tap the `发货方式` row
  - enter a dedicated `shipping_panel` bottom sheet
  - select a verified mail mode through the left-side radio icons
  - tap `确定`
  - return to the portrait listing form
- On this Huawei tablet, the multiline `邮寄` text block is descriptive but not the true tap target.
  The actual deterministic targets are the radio-icon `ImageView` elements aligned with:
  - `包邮`
  - `不包邮-按距离付费`
  - `不包邮-固定邮费`
  - `无需邮寄`
- After `shipping_confirm`, the app can briefly stay on `shipping_panel` or collapse into a
  status-only `unknown` overlay that only exposes system texts like `正在充电...` before the form
  returns. The flow now polls through both states.
- `买家自提` is visible in the panel but is not yet treated as deterministic because the visible
  target did not reliably change the selected mode during real-device probing.
- The flow service now also has a deterministic location-entry bridge from the portrait listing form:
  - tap the `选择位置` row
  - enter the root `location_panel`
  - tap the full `请选择宝贝所在地` row
  - enter the hierarchical `location_region_picker`
- The root `location_panel` also exposes a dedicated location-search path:
  - tap `搜索地址`
  - enter a focused `android.widget.EditText` search screen
  - use direct `EditText.set_text()` instead of the existing FastInputIME `send_keys()` path
  - tap a visible search result row
  - return to the next Xianyu screen
- `ListingDraft` and the Feishu mapping layer now also expose an optional preset search field,
  defaulted to the Bitable column name `预设地址`.
- `XianyuPrepareRunner` can call the existing location-search helper when that optional field is
  present, but this is still treated as best-effort rather than proven persisted state.
- The current user-side Feishu integration now has a dedicated Bitable app for Xianyu debug use,
  named `闲鱼自动发布联调`, with a single `商品发布` table that mirrors the scenario field names.
- The worktree-local `.env` now stores that dedicated app token and table id so local scripts can
  resolve the correct Bitable target without committing tokens into git.
- `XianyuPrepareRunner` now closes the loop into Feishu Bitable by writing:
  - `准备中` immediately after a record is selected
  - `已就绪` when the portrait form is prepared again
  - `准备失败` plus `失败原因` if any downstream device step raises
- This writeback currently describes prepare-runner state, not final Xianyu publish state.
- The live Feishu integration differs from the earlier test-only assumptions in two important ways:
  - Bitable record filters work through `POST /bitable/v1/apps/{app}/tables/{table}/records/search`
    with a JSON `filter` body; the older `GET /records?filter=...` path returned `InvalidFilter`
    against the real table.
  - Attachment downloads are currently driven by the `url` already present in each attachment item,
    and the file request must carry a tenant bearer token. The old
    `/drive/v1/medias/batch_get_tmp_download_url` path returned `404` in the live environment.
- Real Feishu text fields for this table arrive as arrays like `[{text: ..., type: ...}]`, so the
  source layer must flatten those arrays before handing values to the runner.
- On the current Huawei tablet, `fill_description()` and `fill_price()` can both settle on
  `metadata_panel` instead of the upper `listing_form`; downstream metadata steps must treat either
  state as a valid editor continuation.
- The current runner keeps `商品来源` and `预设地址` as best-effort operations when their controls
  are off-screen in the current editor slice, instead of failing the entire prepare run.
- On the Huawei tablet, a top-slice `metadata_panel` can hide lower rows such as `选择位置` even
  though the same editor continues below the fold. The flow now uses a portrait-oriented upward
  swipe inside the editor to reveal those lower rows before opening the location flow.
- The live prepare entrypoint now retries the initial `advance_to_listing_form()` preheat once
  before surfacing a startup failure, because the Huawei tablet can occasionally stop on a
  transient `unknown` state even though a second preheat attempt succeeds.
- Opening the description editor from a scrolled `metadata_panel` is also a two-phase transition on
  this tablet: the first post-tap frame can still look like `metadata_panel`, so the flow now uses
  a dedicated post-description-entry poll instead of treating that tail frame as a hard failure.
- Review mode is intentionally narrow: it only accepts `listing_form` or `metadata_panel` as the
  final editor state and requires the visible `submit_listing` target before the row can be marked
  `待人工发布`.
- Auto-publish mode builds on that same narrow gate. It is only allowed when:
  - the row still passes `是否允许发布`
  - the row also has `允许自动发布=true`
  - the final editor slice still exposes a visible `发布` target
- The analyzer also now has a basic `publish_success` screen shape for future post-submit work,
  keyed off visible success text plus either:
  - the classic `看看宝贝` and `继续发布` actions
  - or the Huawei-tablet reward variant with `再发一件`
- The analyzer now also recognizes Xianyu item detail pages when the app is on
  `com.taobao.idlefish.detail.DetailActivity` and the screen exposes the characteristic
  `返回 / 搜索按钮 / 分享按钮` header controls.
- The flow service now also has a hierarchical `set_location_region_path()` helper for the verified
  Huawei-tablet path `上海 -> 上海 -> 黄浦区`. The first `上海` tap narrows the picker, the second
  `上海` tap expands districts, and the final district tap can leave a transient
  `location_region_picker` tail over the editor before the UI settles.
- The portrait listing form also exposes a metadata/spec entry row such as `分类/ISBN码/成色`
  or richer variants like `分类/盒袋状态/盒卡状态/等\n款式`.
- On the Huawei tablet, tapping that row does not reopen the old publish chooser; it expands into
  a stable `metadata_panel` that still shows the main `发闲置` header plus chip-like choice rows.
- A scrolled editor state can still be the same `metadata_panel` even when upper-form controls
  like `添加图片` or the large description tile are out of view, as long as metadata chips plus
  lower rows such as `价格设置`, `发货方式`, or `选择位置` remain visible.
- The flow service now supports deterministic metadata selection from that page for:
  - currently visible `分类` chips on the panel, such as `家居摆件` or `生活百科`
  - `成色`: `全新`, `几乎全新`, `轻微使用痕迹`, `明显使用痕迹`
  - `商品来源`: `盒机转赠`, `盒机直发`, `淘宝转卖`, `闲置`
- These metadata selections do not currently require a confirm button; real-device probing showed
  the page stays on `metadata_panel` and the chip text flips from `可选...` to `已选中...`.
- When those lower rows are visible inside `metadata_panel`, the existing bridges for
  `价格设置`, `发货方式`, and `选择位置` can now start from that state directly.
- Category support is intentionally scoped to the chips already visible on the metadata panel.
  This branch does not yet traverse a deeper category tree or category search flow.
- Final location persistence is still unresolved on this app/device pair. Real-device probes showed
  that tapping a common address, a search result, or a district row can return to the listing form
  without a stable, visible location confirmation in either the form row or the reopened
  `location_panel`. The flow can now survive the picker tail and drive the search UI, but the
  runner still does not treat location as a deterministic writeback even when driven from the new
  `预设地址` field.
- A later live auto-publish pass proved that at least one previously observed submit failure was
  actually a success-screen recognition gap rather than a location blocker: after the metadata
  scroll fix, the live tablet stayed on a reward-style `publish_success` page that the analyzer now
  classifies correctly.
- The batch-summary table is now optimized for operator review, not replay:
  - `批次明细` is stored as multi-line text instead of raw JSON
  - each line summarizes one processed row as `record_id | 成败 | 关键信息`
  - the formatter includes any available `商品ID`, public link, screen names, and failure reason
- Scheduled production execution is now a thin wrapper around the existing batch worker, not a
  second publish implementation:
  - `run_publish_queue_schedule_live()` repeatedly calls `publish_listing_queue_live()`
  - each inner run still owns its own batch id and summary row
  - outer-loop stop policy is controlled by `max_runs`, `stop_when_idle`, and
    `stop_on_batch_error`
- The current repo is now explicitly treated as the Xianyu execution core rather than the final
  public MCP product surface.
- Planned productization shape:
  - keep `mobile-use` responsible for device automation, Feishu integration, and deterministic
    Xianyu publish flows
  - create a separate thin-wrapper repo that imports this core
  - expose two MCP servers from that new repo:
    - `xianyu_publish_mcp` for queue/prepare/publish/batch business operations
    - `xianyu_debug_mcp` for screen/hierarchy/current-app/tap/swipe/failure-artifact debug
      operations
- Scheduling is intentionally not part of that future MCP contract; it will be owned by the caller
  such as an external agent trigger or automation platform.
- Post-publish receipt extraction now uses Android system state rather than UI text:
  - while the app is on `com.taobao.idlefish.detail.DetailActivity`
  - call `adb shell dumpsys activity activities`
  - parse the resumed detail `Intent { dat=fleamarket://awesome_detail?...itemId=... }`
- This source is good enough to recover `闲鱼商品ID` and the raw app deep link after a successful
  publish.
- Public share-link extraction now uses the detail-page share sheet rather than activity state:
  - tap `分享按钮`
  - wait for the transparency share sheet
  - tap `复制链接`
  - read the device clipboard and extract the first `https://...` URL
  - press `Back` once to return to `listing_detail`
- The Feishu Bitable `Url` field for `闲鱼商品链接` accepts a `{text, link}` object, not the bare
  string form previously used in the source layer.
- Queue-style publishing is intentionally implemented as a thin live-layer loop on top of the
  existing single-item publish entrypoint, not as a second publish engine:
  - resolve and preheat one listing
  - auto-publish it
  - sleep for a configurable cooldown
  - repeat until `max_items`, no candidates, or optional stop-on-error
- Retry budgeting is now layered alongside that queue without introducing server-side Feishu
  comparison logic:
  - store `失败重试次数` and `失败重试上限` on the Bitable row
  - keep the base Feishu search filter simple (`是否允许发布 / 待发布 / 商品图片非空`)
  - skip exhausted rows in `FeishuBitableSource` before constructing `ListingDraft`
  - increment retry count when prepare/review/auto-publish fails
  - reset retry count to `0` only after a successful auto-publish writeback
- Batch logging now reuses the same row-centric writeback channel instead of introducing a second
  Feishu table:
  - queue start generates one `batch_run_id` and `batch_ran_at`
  - the queue passes both values through `prepare_first_publishable_listing_live()`
  - `XianyuPrepareRunner` stamps them on every row status/result writeback
  - the row keeps the latest `最近批次运行ID / 最近批次运行时间 / 最近批次运行结果`
- Queue summary logging now adds a second, coarser layer on top of that row stamping:
  - the live queue script builds shared Feishu-backed components
  - after the queue result is computed, the source best-effort appends one row into
    `批次运行汇总`
  - that row stores batch id/time, counts, stop reason, and serialized item details
  - summary writeback failures do not invalidate the publish run; they surface as
    `summary_logged=False` plus `summary_log_error`
  - before any device preheat, the live queue now probes Feishu once for candidate rows and exits
    early with `no_publishable_listing` when the queue is empty
- Post-publish navigation is now split into two deterministic branches:
  - classic success page: tap `看看宝贝`
  - reward-style success page: press `Back` once
  Both branches can settle on `DetailActivity`, which gives the flow a stable post-publish landing
  page even though item-id/link extraction is still unresolved.
- Real-device probing also showed that selecting a top-level region like `上海` narrows the same
  hierarchical picker rather than completing location selection in one tap.
- Because this portrait `发闲置` form does not currently expose a separate title field through the
  accessibility tree, the business runner treats `ListingDraft.title` as the first line of the
  body text and appends `ListingDraft.description` below it when needed.
- `XianyuPrepareRunner` is the current deterministic vertical slice:
  - pick the first publishable record from Bitable
  - resolve and download attachment media
  - push media to the device
  - attach the first image through the existing album flow
  - if the app returns `selected_media_preview`, tap `下一步 (1)`
  - if the app returns `media_edit_screen`, tap `完成`
  - if the app returns `photo_analysis`, bridge back into the form
  - fill the merged body text
  - fill the sale price
  - optionally apply a visible category chip
  - optionally apply `成色`
  - optionally apply `商品来源`
- The runner intentionally stops at a prepared portrait listing form or metadata panel and does not
  yet own category, stable location persistence, shipping values from Feishu, or final publish
  submission.
- On a fresh Android session, the first UIAutomator FastInputIME use can trigger one-time
  `com.github.uiautomator/.AdbKeyboard` installation and temporarily switch foreground away from
  Xianyu. After that warm-up, subsequent text entry stays in-app.
- The landscape space-analysis path remains supported for investigation and fallback, but it is no longer the default route for entering the form.
- `scripts/xianyu_publish_flow_smoke.py` is the quickest way to inspect the current Xianyu screen classification on a connected Android device.
- `scripts/xianyu_prepare_runner_live.py` is now the canonical way to run the verified live
  Feishu-backed prepare slice end-to-end against the Huawei tablet.
- `scripts/xianyu_publish_review_live.py` is now the canonical way to run the same slice in
  non-submitting review mode and write the row back as `待人工发布`.
- `scripts/xianyu_publish_auto_live.py` is now the canonical way to run the same slice in
  controlled auto-publish mode and write back `发布中 / 已发布 / 发布失败`.
- On the current Huawei tablet, blank description entry is most reliable when the flow writes
  directly into the first child under the `描述...` container; this bypasses the flaky
  FastInputIME and clipboard paths that often no-op or paste stale text.
- The current live runner now fills `价格` before `描述`, because direct description writeback can
  immediately expand the screen into a metadata-rich editor slice where the lower `价格设置` row is
  no longer visible.
- Real-device auto-publish now reaches the final submit tap, and the next deterministic blocker is
  an in-app modal: `无法发布宝贝 / 系统无法定位您所在的行政区...`. This dialog is now treated as an
  explicit post-submit failure signal rather than an `unknown` screen.
- The next layer should still consume `ListingDraft` directly and stay isolated from raw Feishu record payloads.
