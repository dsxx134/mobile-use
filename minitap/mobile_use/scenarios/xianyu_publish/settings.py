from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class XianyuPublishSettings(BaseSettings):
    FEISHU_APP_ID: str | None = None
    FEISHU_APP_SECRET: SecretStr | None = None
    XIANYU_BITABLE_APP_TOKEN: str | None = None
    XIANYU_BITABLE_TABLE_ID: str | None = None
    XIANYU_ANDROID_MEDIA_DIR: str = "/sdcard/DCIM/XianyuPublish"

    title_field_name: str = Field(default="商品标题")
    description_field_name: str = Field(default="商品描述")
    price_field_name: str = Field(default="售价")
    attachment_field_name: str = Field(default="商品图片")
    status_field_name: str = Field(default="发布状态")
    allow_publish_field_name: str = Field(default="是否允许发布")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
