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
