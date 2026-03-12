# mobile-use architecture

Updated: 2026-03-12

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
  - Android media permission dialog
  - album picker
- On the Huawei tablet used for development, reliable home recovery requires:
  - `am start -n com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity`
  - not just `app_start(package)`, which can reopen a non-home category page
- `scripts/xianyu_publish_flow_smoke.py` is the quickest way to inspect the current Xianyu screen classification on a connected Android device.
- The next layer should still consume `ListingDraft` directly and stay isolated from raw Feishu record payloads.
