from __future__ import annotations

import argparse
from pathlib import Path

from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig
from minitap.mobile_use.collectors.xianyu_collector.models import GatherConditionConfig
from minitap.mobile_use.collectors.xianyu_collector.repository.app_config_repo import AppConfigRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.goods_repo import GoodsRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.runtime import build_collector_service
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xianyu-collector")
    parser.add_argument("--db-path", required=True)

    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("config")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)

    set_proxy_parser = config_subparsers.add_parser("set-proxy")
    set_proxy_parser.add_argument("--proxy-url", default="")
    set_proxy_parser.add_argument("--enabled", action="store_true")

    set_cookie_parser = config_subparsers.add_parser("set-cookie")
    set_cookie_parser.add_argument("--cookie-string", required=True)

    db_parser = subparsers.add_parser("db")
    db_subparsers = db_parser.add_subparsers(dest="db_command", required=True)
    db_subparsers.add_parser("list-item-ids")

    collect_parser = subparsers.add_parser("collect")
    collect_subparsers = collect_parser.add_subparsers(dest="collect_command", required=True)

    collect_manual_parser = collect_subparsers.add_parser("manual")
    collect_manual_parser.add_argument("--item-url", action="append", required=True)
    collect_manual_parser.add_argument("--multi-spec-enabled", action="store_true")

    collect_keyword_parser = collect_subparsers.add_parser("keyword")
    collect_keyword_parser.add_argument("--keyword", action="append", required=True)
    collect_keyword_parser.add_argument("--pages", type=int, default=1)
    collect_keyword_parser.add_argument("--multi-spec-enabled", action="store_true")

    collect_shop_parser = collect_subparsers.add_parser("shop")
    collect_shop_parser.add_argument("--shop-url", action="append", required=True)
    collect_shop_parser.add_argument("--pages", type=int, default=1)
    collect_shop_parser.add_argument("--multi-spec-enabled", action="store_true")

    return parser


def main(argv: list[str] | None = None, service_factory=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    database = CollectorDatabase(Path(args.db_path))
    database.initialize()
    config_repo = AppConfigRepository(database)
    goods_repo = GoodsRepository(database)

    if args.command == "config" and args.config_command == "set-proxy":
        config_repo.save_gather_config(
            ProxyConfig(
                is_open_proxy=args.enabled,
                proxy_url=args.proxy_url,
            )
        )
        print("proxy config saved")
        return 0

    if args.command == "config" and args.config_command == "set-cookie":
        config_repo.save_saved_cookie_string(args.cookie_string)
        print("cookie string saved")
        return 0

    if args.command == "db" and args.db_command == "list-item-ids":
        for item_id in goods_repo.list_goods_item_ids():
            print(item_id)
        return 0

    if args.command == "collect":
        factory = service_factory or build_collector_service
        service = factory(Path(args.db_path))
        proxy_config = getattr(service, "default_proxy_config", None)
        gather_conditions = getattr(service, "default_gather_conditions", None)
        if gather_conditions is None:
            gather_conditions = config_repo.load_gather_conditions()
        filter_config = (
            gather_conditions.to_filter_config()
            if isinstance(gather_conditions, GatherConditionConfig)
            else FilterConfig()
        )
        multi_spec_enabled = args.multi_spec_enabled or (
            gather_conditions.is_kai_qi_duo_gui_ge_cai_ji
            if isinstance(gather_conditions, GatherConditionConfig)
            else False
        )
        if args.collect_command == "manual":
            summary = service.collect_manual(
                urls=args.item_url,
                filter_config=filter_config,
                multi_spec_enabled=multi_spec_enabled,
                proxy_config=proxy_config,
            )
        elif args.collect_command == "keyword":
            summary = service.collect_keyword(
                keywords=args.keyword,
                pages=args.pages,
                filter_config=filter_config,
                multi_spec_enabled=multi_spec_enabled,
                proxy_config=proxy_config,
                per_keyword_success_limit=(
                    gather_conditions.keyword_collect_limit
                    if isinstance(gather_conditions, GatherConditionConfig)
                    else None
                ),
            )
        else:
            summary = service.collect_shop(
                shop_urls=args.shop_url,
                pages=args.pages,
                filter_config=filter_config,
                multi_spec_enabled=multi_spec_enabled,
                proxy_config=proxy_config,
                recent_publish_filter=(
                    gather_conditions.shop_recent_publish_filter
                    if isinstance(gather_conditions, GatherConditionConfig)
                    else None
                ),
            )
        print(
            f"saved={summary.saved} filtered={summary.filtered} "
            f"duplicates={summary.duplicates} errors={summary.errors}"
        )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
