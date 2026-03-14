from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class XianyuPublishSettings(BaseSettings):
    FEISHU_APP_ID: str | None = None
    FEISHU_APP_SECRET: SecretStr | None = None
    XIANYU_BITABLE_APP_TOKEN: str | None = None
    XIANYU_BITABLE_TABLE_ID: str | None = None
    XIANYU_ANDROID_SERIAL: str | None = None
    XIANYU_ANDROID_MEDIA_DIR: str = "/sdcard/DCIM/XianyuPublish"
    xianyu_package_name: str = "com.taobao.idlefish"
    xianyu_main_activity: str = "com.taobao.idlefish.maincontainer.activity.MainActivity"
    publish_entry_text: str = "卖闲置"
    publish_option_text: str = "发闲置"
    draft_resume_action: str = "discard"
    permission_allow_text: str = "允许"
    album_source_label_text: str = "所有文件"
    preferred_album_name: str = "XianyuPublish"
    album_select_text: str = "选择"
    album_confirm_text: str = "确定"
    space_overlay_dismiss_x_ratio: float = 0.75
    space_overlay_dismiss_y_ratio: float = 0.94375
    space_publish_button_x_ratio: float = 0.6796875
    space_publish_button_y_ratio: float = 0.934375
    editor_scroll_x_ratio: float = 0.5
    editor_scroll_start_y_ratio: float = 0.82
    editor_scroll_end_y_ratio: float = 0.35
    editor_scroll_duration_ms: int = 350

    title_field_name: str = Field(default="商品标题")
    description_field_name: str = Field(default="商品描述")
    price_field_name: str = Field(default="售价")
    category_field_name: str = Field(default="分类")
    condition_field_name: str = Field(default="成色")
    item_source_field_name: str = Field(default="商品来源")
    location_search_query_field_name: str = Field(default="预设地址")
    attachment_field_name: str = Field(default="商品图片")
    status_field_name: str = Field(default="发布状态")
    failure_reason_field_name: str = Field(default="失败原因")
    allow_publish_field_name: str = Field(default="是否允许发布")
    auto_publish_field_name: str = Field(default="允许自动发布")
    listing_id_field_name: str = Field(default="闲鱼商品ID")
    listing_url_field_name: str = Field(default="闲鱼商品链接")
    published_at_field_name: str = Field(default="发布时间")
    manual_review_status: str = "待人工发布"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
