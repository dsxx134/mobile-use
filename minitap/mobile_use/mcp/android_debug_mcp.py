from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from minitap.mobile_use.mcp.android_debug_models import (
    CurrentAppResult,
    DeviceCommandResult,
    DeviceInfo,
    DeviceSelector,
    HierarchyDumpResult,
    HierarchyInput,
    InputTextInput,
    LaunchAppInput,
    LaunchAppResult,
    PushMediaInput,
    PushMediaResult,
    ScreenDataResult,
    TapInput,
    TapResult,
    TextInputResult,
    SwipeInput,
    SwipeResult,
)
from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService

mcp = FastMCP("android_debug_mcp")
service = AndroidDebugService()

READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)
WRITE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=False,
)


@mcp.tool(
    name="android_debug_list_devices",
    description="List Android devices currently visible to the local ADB server.",
    annotations=READ_ONLY,
    structured_output=True,
)
async def android_debug_list_devices() -> list[DeviceInfo]:
    return [DeviceInfo.model_validate(device) for device in service.list_devices()]


@mcp.tool(
    name="android_debug_get_current_app",
    description="Get the foreground Android package and activity for a device serial.",
    annotations=READ_ONLY,
    structured_output=True,
)
async def android_debug_get_current_app(params: DeviceSelector) -> CurrentAppResult:
    return CurrentAppResult.model_validate(service.get_current_app(params.serial))


@mcp.tool(
    name="android_debug_get_screen_data",
    description="Get a structured Android screen snapshot with screenshot base64 and elements.",
    annotations=READ_ONLY,
    structured_output=True,
)
async def android_debug_get_screen_data(params: DeviceSelector) -> ScreenDataResult:
    return ScreenDataResult.model_validate(service.get_screen_data(params.serial))


@mcp.tool(
    name="android_debug_dump_ui_hierarchy",
    description="Dump the current Android UI hierarchy XML for a device serial.",
    annotations=READ_ONLY,
    structured_output=True,
)
async def android_debug_dump_ui_hierarchy(params: HierarchyInput) -> HierarchyDumpResult:
    return HierarchyDumpResult.model_validate(service.dump_ui_hierarchy(params.serial))


@mcp.tool(
    name="android_debug_tap",
    description="Tap an Android screen coordinate, optionally using a long press.",
    annotations=WRITE,
    structured_output=True,
)
async def android_debug_tap(params: TapInput) -> TapResult:
    return TapResult.model_validate(
        service.tap(
            params.serial,
            x=params.x,
            y=params.y,
            long_press=params.long_press,
            long_press_duration_ms=params.long_press_duration_ms,
        )
    )


@mcp.tool(
    name="android_debug_swipe",
    description="Swipe between two Android screen coordinates.",
    annotations=WRITE,
    structured_output=True,
)
async def android_debug_swipe(params: SwipeInput) -> SwipeResult:
    return SwipeResult.model_validate(
        service.swipe(
            params.serial,
            start_x=params.start_x,
            start_y=params.start_y,
            end_x=params.end_x,
            end_y=params.end_y,
            duration_ms=params.duration_ms,
        )
    )


@mcp.tool(
    name="android_debug_input_text",
    description="Send text to the currently focused Android input field.",
    annotations=WRITE,
    structured_output=True,
)
async def android_debug_input_text(params: InputTextInput) -> TextInputResult:
    return TextInputResult.model_validate(service.input_text(params.serial, params.text))


@mcp.tool(
    name="android_debug_launch_app",
    description="Launch an Android app by package name.",
    annotations=WRITE,
    structured_output=True,
)
async def android_debug_launch_app(params: LaunchAppInput) -> LaunchAppResult:
    return LaunchAppResult.model_validate(service.launch_app(params.serial, params.package_name))


@mcp.tool(
    name="android_debug_press_back",
    description="Press the Android back key.",
    annotations=WRITE,
    structured_output=True,
)
async def android_debug_press_back(params: DeviceSelector) -> DeviceCommandResult:
    return DeviceCommandResult.model_validate(service.press_back(params.serial))


@mcp.tool(
    name="android_debug_press_home",
    description="Press the Android home key.",
    annotations=WRITE,
    structured_output=True,
)
async def android_debug_press_home(params: DeviceSelector) -> DeviceCommandResult:
    return DeviceCommandResult.model_validate(service.press_home(params.serial))


@mcp.tool(
    name="android_debug_push_media_to_device",
    description=(
        "Push a local media file to an Android device and optionally scan it into media DB."
    ),
    annotations=WRITE,
    structured_output=True,
)
async def android_debug_push_media_to_device(params: PushMediaInput) -> PushMediaResult:
    return PushMediaResult.model_validate(
        service.push_media_to_device(
            params.serial,
            local_path=params.local_path,
            remote_path=params.remote_path,
            scan_media=params.scan_media,
        )
    )


def main() -> None:
    mcp.run()
