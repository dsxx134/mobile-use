# fastmcp-structured-output-needs-models

Updated: 2026-03-12

## Rule
- When using FastMCP with `structured_output=True`, do not return bare `dict` annotations.
- Use Pydantic output models, or typed collections of models, for tool return types.

## Why
- FastMCP rejects plain `dict` return annotations for structured output registration.
- Pydantic output models generate usable `output_schema` metadata for MCP clients.

## Applied In
- `minitap/mobile_use/mcp/android_debug_mcp.py`
