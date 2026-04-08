# android-debug-snapshot-should-preserve-hierarchy

Updated: 2026-03-12

## Rule
- Android debug screen snapshots should include both flattened `elements` and raw `hierarchy_xml`.
- Include `element_count` in the snapshot so clients can quickly reason about page density without scanning the whole list.

## Why
- Flat elements are convenient for quick inspection and LLM consumption.
- Raw hierarchy XML is still needed for debugging selector edge cases and UI parser mismatches.
- Returning both in one snapshot avoids an extra MCP call during troubleshooting.

## Applied In
- `minitap/mobile_use/mcp/android_debug_service.py`
- `minitap/mobile_use/mcp/android_debug_models.py`
- `minitap/mobile_use/mcp/android_debug_mcp.py`
