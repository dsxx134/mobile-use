from __future__ import annotations

import argparse
import os
from contextlib import contextmanager
from pathlib import Path

from minitap.mobile_use.collectors.xianyu_collector.api.client import GoofishApiError
from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig
from minitap.mobile_use.collectors.xianyu_collector.models import BitBrowserConfig, GatherConditionConfig
from minitap.mobile_use.collectors.xianyu_collector.repository.app_config_repo import AppConfigRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.goods_repo import GoodsRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.runtime import build_collector_service
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xianyu-collector")
    parser.add_argument("--db-path", required=True)
    parser.add_argument("--bitbrowser-id")
    parser.add_argument("--bitbrowser-api-host")
    parser.add_argument("--bitbrowser-api-port", type=int)

    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("config")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)

    set_proxy_parser = config_subparsers.add_parser("set-proxy")
    set_proxy_parser.add_argument("--proxy-url", default="")
    set_proxy_parser.add_argument("--enabled", action="store_true")

    set_cookie_parser = config_subparsers.add_parser("set-cookie")
    set_cookie_parser.add_argument("--cookie-string", required=True)

    set_bitbrowser_parser = config_subparsers.add_parser("set-bitbrowser")
    set_bitbrowser_parser.add_argument("--browser-id", required=True)
    set_bitbrowser_parser.add_argument("--api-host", default="127.0.0.1")
    set_bitbrowser_parser.add_argument("--api-port", type=int, default=54345)

    db_parser = subparsers.add_parser("db")
    db_subparsers = db_parser.add_subparsers(dest="db_command", required=True)
    db_subparsers.add_parser("list-item-ids")

    doctor_parser = subparsers.add_parser("doctor")
    doctor_subparsers = doctor_parser.add_subparsers(dest="doctor_command", required=True)
    doctor_session_parser = doctor_subparsers.add_parser("session")
    doctor_session_parser.add_argument("--keyword", default="gemini")

    collect_parser = subparsers.add_parser("collect")
    collect_subparsers = collect_parser.add_subparsers(dest="collect_command", required=True)

    collect_manual_parser = collect_subparsers.add_parser("manual")
    collect_manual_parser.add_argument("--item-url", action="append")
    collect_manual_parser.add_argument("--multi-spec-enabled", action="store_true")

    collect_keyword_parser = collect_subparsers.add_parser("keyword")
    collect_keyword_parser.add_argument("--keyword", action="append")
    collect_keyword_parser.add_argument("--pages", type=int, default=1)
    collect_keyword_parser.add_argument("--multi-spec-enabled", action="store_true")

    collect_shop_parser = collect_subparsers.add_parser("shop")
    collect_shop_parser.add_argument("--shop-url", action="append")
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

    if args.command == "config" and args.config_command == "set-bitbrowser":
        config_repo.save_bitbrowser_config(
            BitBrowserConfig(
                browser_id=args.browser_id,
                api_host=args.api_host,
                api_port=args.api_port,
            )
        )
        print("bitbrowser config saved")
        return 0

    if args.command == "db" and args.db_command == "list-item-ids":
        for item_id in goods_repo.list_goods_item_ids():
            print(item_id)
        return 0

    if args.command == "doctor" and args.doctor_command == "session":
        factory = service_factory or build_collector_service
        with _collector_runtime_env(args):
            service = factory(Path(args.db_path))
        cookie_provider = service.api_client.cookie_provider
        cookies = dict(cookie_provider.get_cookie_dict())
        cookie_source = _cookie_source_name(cookie_provider)
        try:
            item_ids = service.api_client.search_items(
                page=1,
                keyword=args.keyword,
                proxy_config=getattr(service, "default_proxy_config", None),
            )
        except GoofishApiError as exc:
            print(
                "session=signing-only "
                f"cookie_source={cookie_source} "
                f"cookie_keys={','.join(sorted(cookies.keys()))} "
                f"reason={exc}"
            )
            return 2
        print(
            "session=searchable "
            f"cookie_source={cookie_source} "
            f"cookie_keys={','.join(sorted(cookies.keys()))} "
            f"item_count={len(item_ids)} "
            f"keyword={args.keyword}"
        )
        return 0

    if args.command == "collect":
        factory = service_factory or build_collector_service
        with _collector_runtime_env(args):
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
            urls = args.item_url or _load_saved_lines(config_repo, 1)
            if not urls:
                parser.error("manual collection requires --item-url or saved gather_type_1 input")
            try:
                summary = service.collect_manual(
                    urls=urls,
                    filter_config=filter_config,
                    multi_spec_enabled=multi_spec_enabled,
                    proxy_config=proxy_config,
                )
            except GoofishApiError as exc:
                print(f"collector error: {exc}")
                return 2
        elif args.collect_command == "keyword":
            keywords = args.keyword or _load_saved_lines(config_repo, 0)
            if not keywords:
                parser.error("keyword collection requires --keyword or saved gather_type_0 input")
            try:
                summary = service.collect_keyword(
                    keywords=keywords,
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
            except GoofishApiError as exc:
                print(f"collector error: {exc}")
                return 2
        else:
            shop_urls = args.shop_url or _load_saved_lines(config_repo, 2)
            if not shop_urls:
                parser.error("shop collection requires --shop-url or saved gather_type_2 input")
            try:
                summary = service.collect_shop(
                    shop_urls=shop_urls,
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
            except GoofishApiError as exc:
                print(f"collector error: {exc}")
                return 2
        print(
            f"saved={summary.saved} filtered={summary.filtered} "
            f"duplicates={summary.duplicates} errors={summary.errors}"
        )
        return 0

    parser.print_help()
    return 1


def _load_saved_lines(config_repo: AppConfigRepository, gather_type: int) -> list[str]:
    raw = config_repo.load_gather_type_input(gather_type)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _cookie_source_name(cookie_provider) -> str:
    active_provider = getattr(cookie_provider, "_active_provider", None)
    if active_provider is not None:
        session = getattr(active_provider, "session", None)
        if session is not None:
            return type(session).__name__
        return type(active_provider).__name__
    return type(cookie_provider).__name__


@contextmanager
def _collector_runtime_env(args):
    overrides = {}
    if getattr(args, "bitbrowser_id", None):
        overrides["XIANYU_COLLECTOR_BITBROWSER_ID"] = args.bitbrowser_id
    if getattr(args, "bitbrowser_api_host", None):
        overrides["XIANYU_COLLECTOR_BITBROWSER_API_HOST"] = args.bitbrowser_api_host
    if getattr(args, "bitbrowser_api_port", None) is not None:
        overrides["XIANYU_COLLECTOR_BITBROWSER_API_PORT"] = str(args.bitbrowser_api_port)

    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            os.environ[key] = value
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


if __name__ == "__main__":
    raise SystemExit(main())
