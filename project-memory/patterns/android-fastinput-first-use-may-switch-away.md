# android fastinput first use may switch away

Updated: 2026-03-13

## Pattern
- `UIAutomatorClient.send_text()` uses `set_fastinput_ime(True)` and `send_keys(...)`.
- On a fresh Android session, the first call can trigger one-time installation/setup of
  `com.github.uiautomator/.AdbKeyboard`.
- During that warm-up, foreground focus can leave the target app and move to package installer or
  Huawei App Market risk-check UI.

## Why it matters
- A naive `input_text()` wrapper can report success even though the automation context has left the
  business app.
- After the one-time warm-up finishes, subsequent FastInputIME text entry stays in-app and becomes
  usable for deterministic flows.

## Applies to
- `minitap/mobile_use/clients/ui_automator_client.py`
- `minitap/mobile_use/mcp/android_debug_service.py`
- Android flows that rely on FastInputIME-backed text entry
