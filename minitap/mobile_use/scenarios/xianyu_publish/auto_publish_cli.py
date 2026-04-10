import argparse
from collections.abc import Callable, Sequence
from pathlib import Path

from minitap.mobile_use.scenarios.xianyu_publish.live_prepare import (
    format_live_prepare_result,
    prepare_first_publishable_listing_live,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mobile-use-xianyu-publish-auto",
        description="Prepare and auto-publish one Xianyu listing from Feishu when the listing is allowed."
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
    return parser


def run_auto_publish_cli(
    argv: Sequence[str] | None = None,
    *,
    prepare_fn: Callable[..., object] = prepare_first_publishable_listing_live,
) -> str:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = prepare_fn(
        serial=args.serial,
        staging_root=args.staging_root,
        preheat_max_steps=args.preheat_max_steps,
        preheat_attempts=args.preheat_attempts,
        review_after_prepare=False,
        auto_publish_after_prepare=True,
    )
    return format_live_prepare_result(result)


def main(argv: Sequence[str] | None = None) -> None:
    print(run_auto_publish_cli(argv))
