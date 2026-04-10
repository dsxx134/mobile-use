from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence

from minitap.mobile_use.collectors.xianyu_collector.cli import main as collector_main_impl
from minitap.mobile_use.scenarios.xianyu_publish.auto_publish_cli import (
    main as publish_auto_main_impl,
)
from minitap.mobile_use.scenarios.xianyu_publish.prepare_cli import main as prepare_main_impl
from minitap.mobile_use.scenarios.xianyu_publish.publish_cli import main as publish_main_impl
from minitap.mobile_use.scenarios.xianyu_publish.publish_schedule_cli import (
    main as publish_schedule_main_impl,
)
from minitap.mobile_use.scenarios.xianyu_publish.review_cli import main as review_main_impl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mobile-use-xianyu",
        description="Unified operator CLI for Xianyu collector and publishing workflows.",
    )
    parser.add_argument(
        "command",
        choices=(
            "collector",
            "prepare",
            "review",
            "publish",
            "publish-auto",
            "publish-schedule",
        ),
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    collector_main: Callable[[Sequence[str] | None], int] = collector_main_impl,
    prepare_main: Callable[[Sequence[str] | None], None] = prepare_main_impl,
    review_main: Callable[[Sequence[str] | None], None] = review_main_impl,
    publish_main: Callable[[Sequence[str] | None], None] = publish_main_impl,
    publish_auto_main: Callable[[Sequence[str] | None], None] = publish_auto_main_impl,
    publish_schedule_main: Callable[[Sequence[str] | None], None] = publish_schedule_main_impl,
) -> int:
    parser = build_parser()
    try:
        args, forwarded = parser.parse_known_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if args.command == "collector":
        return int(collector_main(forwarded))
    if args.command == "prepare":
        prepare_main(forwarded)
        return 0
    if args.command == "review":
        review_main(forwarded)
        return 0
    if args.command == "publish":
        publish_main(forwarded)
        return 0
    if args.command == "publish-auto":
        publish_auto_main(forwarded)
        return 0
    if args.command == "publish-schedule":
        publish_schedule_main(forwarded)
        return 0

    parser.print_help()
    return 2
