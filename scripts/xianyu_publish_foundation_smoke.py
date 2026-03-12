import json

from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def main() -> None:
    settings = XianyuPublishSettings()
    print(
        json.dumps(
            {
                "app_token": settings.XIANYU_BITABLE_APP_TOKEN,
                "table_id": settings.XIANYU_BITABLE_TABLE_ID,
                "android_media_dir": settings.XIANYU_ANDROID_MEDIA_DIR,
                "attachment_field_name": settings.attachment_field_name,
                "status_field_name": settings.status_field_name,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
