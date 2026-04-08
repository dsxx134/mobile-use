import argparse
from pathlib import Path

from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    build_live_prepare_components,
    format_live_queue_schedule_result,
    run_publish_queue_schedule_live,
)
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the live Xianyu batch worker on a fixed interval "
            "for scheduler-friendly production use."
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
        help="Maximum number of publishable listings to process in each batch.",
    )
    parser.add_argument(
        "--cooldown-seconds",
        type=float,
        default=3.0,
        help="Seconds to wait between processed listings inside one batch.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop the current batch immediately after the first failed listing.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=300.0,
        help="Seconds to wait between batch runs.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=0,
        help="Maximum number of batch runs. Use 0 to run until a stop condition is met externally.",
    )
    parser.add_argument(
        "--stop-when-idle",
        action="store_true",
        help="Stop the schedule loop when the queue reports no publishable listing.",
    )
    parser.add_argument(
        "--stop-on-batch-error",
        action="store_true",
        help="Stop the schedule loop after any batch that contains at least one failure.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = XianyuPublishSettings()
    components = build_live_prepare_components(settings)
    result = run_publish_queue_schedule_live(
        settings=settings,
        serial=args.serial,
        staging_root=args.staging_root,
        preheat_max_steps=args.preheat_max_steps,
        max_items=args.max_items,
        cooldown_seconds=args.cooldown_seconds,
        stop_on_error=args.stop_on_error,
        interval_seconds=args.interval_seconds,
        max_runs=args.max_runs,
        stop_when_idle=args.stop_when_idle,
        stop_on_batch_error=args.stop_on_batch_error,
        components=components,
    )
    print(format_live_queue_schedule_result(result))


if __name__ == "__main__":
    main()
