import argparse
from pathlib import Path

from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    build_live_prepare_components,
    format_live_batch_result,
    publish_listing_queue_live,
)
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Process a controlled batch of auto-publishable Xianyu listings from Feishu."
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
    parser.add_argument(
        "--max-items",
        type=int,
        default=1,
        help="Maximum number of publishable listings to process in this batch.",
    )
    parser.add_argument(
        "--cooldown-seconds",
        type=float,
        default=3.0,
        help="Seconds to wait between processed listings.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop the batch immediately after the first failed listing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = XianyuPublishSettings()
    components = build_live_prepare_components(settings)
    result = publish_listing_queue_live(
        settings=settings,
        serial=args.serial,
        staging_root=args.staging_root,
        preheat_max_steps=args.preheat_max_steps,
        max_items=args.max_items,
        cooldown_seconds=args.cooldown_seconds,
        stop_on_error=args.stop_on_error,
        components=components,
    )
    print(format_live_batch_result(result))


if __name__ == "__main__":
    main()
