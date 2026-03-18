import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Sequence

from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    XianyuLiveBatchPublishResult,
    format_live_batch_result,
    publish_listing_queue_live,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish Xianyu listings from Feishu with structured JSON output."
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
        "--preheat-attempts",
        type=int,
        default=2,
        help="Retry attempts for the preheat step before failing.",
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
    return parser


def run_publish_cli(
    argv: Sequence[str] | None = None,
    *,
    publish_queue_fn: Callable[..., XianyuLiveBatchPublishResult] = publish_listing_queue_live,
) -> tuple[str, int]:
    parser = _build_parser()
    args = parser.parse_args(argv)

    result = publish_queue_fn(
        serial=args.serial,
        staging_root=args.staging_root,
        preheat_max_steps=args.preheat_max_steps,
        preheat_attempts=args.preheat_attempts,
        max_items=args.max_items,
        cooldown_seconds=args.cooldown_seconds,
        stop_on_error=args.stop_on_error,
    )
    output = format_live_batch_result(result)
    exit_code = 2 if result.failure_count > 0 else 0
    return output, exit_code


def main(argv: Sequence[str] | None = None) -> None:
    output, exit_code = run_publish_cli(argv)
    print(output)
    raise SystemExit(exit_code)
