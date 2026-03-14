# xianyu-location-search-needs-focused-edittext-set-text

Updated: 2026-03-14

## Context
- Project: `mobile-use`
- Area: Xianyu publish flow on the Huawei Android tablet `E2P6R22708000602`

## Pattern
- The Xianyu `搜索地址` screen exposes a focused `android.widget.EditText` with
  `hint="搜索地址"`.
- On this screen, the existing FastInputIME `send_keys()` path can no-op even though the field is
  focused.
- Using direct `EditText.set_text()` on the focused field surfaces visible result rows.
- Those result rows can still appear one or two snapshots after the text is set, so callers should
  poll inside the same search screen instead of expecting an immediate selectable result.

## Evidence
- Real-device probe:
  - tap `选择位置`
  - tap `搜索地址`
  - `send_keys("上海虹桥站")` does not surface results
  - `focused_edit_text.set_text("上海虹桥站")` surfaces rows like:
    - `上海虹桥站\n新虹街道申贵路1500号`
    - `上海虹桥站P9地下停车场\n华漕镇申虹路...`

## Reuse
- Prefer a dedicated focused-EditText helper for Xianyu search-style pages instead of changing the
  global text-entry path.
- Reuse the same approach when:
  - the field is focused
  - the screen exposes a real `EditText`
  - FastInputIME input does not change the UI state

## Boundary
- This pattern only unlocks the search UI and visible result rows.
- Tapping a result row still does not prove visible location writeback on the editor or inside the
  reopened `location_panel`.
