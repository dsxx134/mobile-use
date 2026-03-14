import argparse
from pathlib import Path

from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    format_live_prepare_result,
    prepare_first_publishable_listing_live,
)
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare and review one publishable Xianyu listing from Feishu "
            "without submitting it."
        )
    )
    parser.add_argument(
        "--serial",
        help="Android device serial. Falls back to XIANYU_ANDROID_SERIAL when omitted.",
    )
    parser.add_argument(
        "--staging-root",
        type=Path,
        help="Local directory used to stage downloaded listing media before adb push.",
    )
    parser.add_argument(
        "--preheat-max-steps",
        type=int,
        default=10,
        help="Maximum steps used to preheat Xianyu back to the portrait listing form.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = XianyuPublishSettings()
    result = prepare_first_publishable_listing_live(
        settings=settings,
        serial=args.serial,
        staging_root=args.staging_root,
        preheat_max_steps=args.preheat_max_steps,
        review_after_prepare=True,
    )
    print(format_live_prepare_result(result))


if __name__ == "__main__":
    main()
