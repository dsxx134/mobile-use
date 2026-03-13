# mobile-use architecture

Updated: 2026-03-13

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
- The Xianyu flow currently recognizes:
  - home tab
  - publish chooser
  - portrait listing form
  - description editor
  - Android media permission dialog
  - album picker
  - album source menu
  - photo analysis screen after media confirmation
  - the Xianyu space `宝贝` empty-state page
- On the Huawei tablet used for development, reliable home recovery requires:
  - `am start -n com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity`
  - not just `app_start(package)`, which can reopen a non-home category page
- Deterministic media selection is safer when the flow switches the picker from `所有文件` to a dedicated source folder such as `XianyuPublish`.
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
  - land on the standard portrait listing form
- On the real portrait listing form, several actionable controls are surfaced via `content-desc`
  rather than plain `text`, including:
  - `发布, 发布`
  - `添加图片`
  - `描述, 描述一下宝贝的品牌型号、货品来源…`
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
- On a fresh Android session, the first UIAutomator FastInputIME use can trigger one-time
  `com.github.uiautomator/.AdbKeyboard` installation and temporarily switch foreground away from
  Xianyu. After that warm-up, subsequent text entry stays in-app.
- The landscape space-analysis path remains supported for investigation and fallback, but it is no longer the default route for entering the form.
- `scripts/xianyu_publish_flow_smoke.py` is the quickest way to inspect the current Xianyu screen classification on a connected Android device.
- The next layer should still consume `ListingDraft` directly and stay isolated from raw Feishu record payloads.
