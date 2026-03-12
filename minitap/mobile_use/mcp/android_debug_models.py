from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DeviceSelector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial: str = Field(..., min_length=1, description="ADB serial for the Android device")


class TapInput(DeviceSelector):
    x: int = Field(..., ge=0, description="Horizontal pixel coordinate")
    y: int = Field(..., ge=0, description="Vertical pixel coordinate")
    long_press: bool = Field(default=False, description="Use a press-and-hold gesture")
    long_press_duration_ms: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Press duration when long_press is enabled",
    )


class SwipeInput(DeviceSelector):
    start_x: int = Field(..., ge=0, description="Swipe start X coordinate")
    start_y: int = Field(..., ge=0, description="Swipe start Y coordinate")
    end_x: int = Field(..., ge=0, description="Swipe end X coordinate")
    end_y: int = Field(..., ge=0, description="Swipe end Y coordinate")
    duration_ms: int = Field(default=400, ge=1, le=10000, description="Swipe duration")


class InputTextInput(DeviceSelector):
    text: str = Field(..., min_length=1, description="Text to send to the focused field")


class LaunchAppInput(DeviceSelector):
    package_name: str = Field(..., min_length=1, description="Android package name to launch")


class PushMediaInput(DeviceSelector):
    local_path: str = Field(..., min_length=1, description="Local file path to push")
    remote_path: str = Field(..., min_length=1, description="Destination path on device")
    scan_media: bool = Field(
        default=True,
        description="Trigger Android media scanner after pushing the file",
    )


class ScreenshotInput(DeviceSelector):
    pass


class HierarchyInput(DeviceSelector):
    pass


class DeviceInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial: str | None = Field(default=None, description="ADB serial of the device")
    state: str | None = Field(default=None, description="ADB state of the device")


class CurrentAppResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial: str
    package: str | None = None
    activity: str | None = None
    raw_output: str


class ScreenDataResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial: str
    platform: str
    current_app: CurrentAppResult
    width: int
    height: int
    base64: str
    elements: list[dict[str, Any]]


class HierarchyDumpResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial: str
    hierarchy_xml: str


class DeviceCommandResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial: str
    success: bool


class TapResult(DeviceCommandResult):
    x: int
    y: int
    long_press: bool
    long_press_duration_ms: int


class SwipeResult(DeviceCommandResult):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    duration_ms: int


class TextInputResult(DeviceCommandResult):
    text: str


class LaunchAppResult(DeviceCommandResult):
    package_name: str


class PushMediaResult(DeviceCommandResult):
    local_path: str
    remote_path: str
    file_size_bytes: int
    scan_media: bool
