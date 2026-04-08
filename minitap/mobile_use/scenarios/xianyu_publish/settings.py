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
    original_price_field_name: str = Field(default="原价")
    stock_field_name: str = Field(default="库存")
    category_field_name: str = Field(default="分类")
    condition_field_name: str = Field(default="成色")
    item_source_field_name: str = Field(default="商品来源")
    location_search_query_field_name: str = Field(default="预设地址")
    coin_discount_field_name: str = Field(default="闲鱼币抵扣")
    shipping_method_field_name: str = Field(default="发货方式")
    shipping_time_field_name: str = Field(default="发货时间")
    attachment_field_name: str = Field(default="商品图片")
    status_field_name: str = Field(default="发布状态")
    failure_reason_field_name: str = Field(default="日志路径")
    failure_captured_at_field_name: str = Field(default="最近失败时间")
    failure_screenshot_path_field_name: str = Field(default="最近失败截图路径")
    failure_hierarchy_path_field_name: str = Field(default="最近失败界面快照路径")
    failure_activity_dump_path_field_name: str = Field(default="最近失败活动栈路径")
    failure_current_app_field_name: str = Field(default="最近失败前台应用")
    retry_count_field_name: str | None = Field(default=None)
    retry_limit_field_name: str | None = Field(default=None)
    batch_run_id_field_name: str = Field(default="最近批次运行ID")
    batch_ran_at_field_name: str = Field(default="最近批次运行时间")
    batch_result_field_name: str = Field(default="最近批次运行结果")
    batch_summary_table_name: str = Field(default="批次运行汇总")
    batch_summary_primary_field_name: str = Field(default="文本")
    batch_summary_run_id_field_name: str = Field(default="批次运行ID")
    batch_summary_ran_at_field_name: str = Field(default="批次运行时间")
    batch_summary_requested_count_field_name: str = Field(default="请求条数")
    batch_summary_processed_count_field_name: str = Field(default="处理条数")
    batch_summary_success_count_field_name: str = Field(default="成功条数")
    batch_summary_failure_count_field_name: str = Field(default="失败条数")
    batch_summary_stop_reason_field_name: str = Field(default="停止原因")
    batch_summary_items_field_name: str = Field(default="批次明细")
    allow_publish_field_name: str | None = Field(default=None)
    auto_publish_field_name: str | None = Field(default=None)
    listing_id_field_name: str = Field(default="闲鱼商品ID")
    listing_url_field_name: str = Field(default="闲鱼商品链接")
    published_at_field_name: str = Field(default="发布时间")
    manual_review_status: str = "待人工发布"
    default_retry_limit: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
