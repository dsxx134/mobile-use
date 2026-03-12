from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FeishuAttachment(BaseModel):
    model_config = ConfigDict(extra="ignore")

    file_token: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    size: int | None = Field(default=None, ge=0)
    tmp_url: str | None = None
    url: str | None = None
    file_type: str | None = None


class ListingDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    attachments: list[FeishuAttachment]
    local_image_paths: list[Path] = Field(default_factory=list)

    @field_validator("attachments")
    @classmethod
    def validate_attachments(cls, attachments: list[FeishuAttachment]) -> list[FeishuAttachment]:
        if not attachments:
            raise ValueError("ListingDraft requires at least one attachment")
        return attachments


class ListingStatusFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pending_status: str = Field(default="待发布")
    allow_publish: bool = True


class TapTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    text: str | None = None
    bounds: str | None = None


class XianyuScreenAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    screen_name: str
    current_package: str | None = None
    current_activity: str | None = None
    visible_texts: list[str] = Field(default_factory=list)
    targets: dict[str, TapTarget] = Field(default_factory=dict)
