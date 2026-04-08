from __future__ import annotations

from pathlib import Path

from minitap.mobile_use.collectors.xianyu_collector.api.client import GoofishApiClient
from minitap.mobile_use.collectors.xianyu_collector.domain.filter_engine import FilterEngine
from minitap.mobile_use.collectors.xianyu_collector.domain.item_normalizer import ItemNormalizer
from minitap.mobile_use.collectors.xianyu_collector.models import GatherConditionConfig
from minitap.mobile_use.collectors.xianyu_collector.repository.app_config_repo import AppConfigRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.goods_repo import GoodsRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.services.collector_service import CollectorService
from minitap.mobile_use.collectors.xianyu_collector.session.saved_cookie_provider import SavedCookieProvider
from minitap.mobile_use.collectors.xianyu_collector.signing.mtop_signer import MtopSigner
from minitap.mobile_use.collectors.xianyu_collector.transport.http_client import CollectorHttpClient
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_provider import HttpProxyProvider
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_state import ProxyState


def build_collector_service(db_path: Path | str) -> CollectorService:
    database = CollectorDatabase(Path(db_path))
    database.initialize()

    app_config_repo = AppConfigRepository(database)
    goods_repo = GoodsRepository(database)

    cookie_provider = SavedCookieProvider(app_config_repo.load_saved_cookie_string())
    proxy_state = ProxyState(HttpProxyProvider())
    transport = CollectorHttpClient(proxy_state=proxy_state)
    signer = MtopSigner()
    api_client = GoofishApiClient(
        transport=transport,
        cookie_provider=cookie_provider,
        signer=signer,
    )

    service = CollectorService(
        api_client=api_client,
        goods_repo=goods_repo,
        item_normalizer=ItemNormalizer(),
        filter_engine=FilterEngine(),
    )
    service.default_proxy_config = app_config_repo.load_gather_config()
    service.default_gather_conditions = app_config_repo.load_gather_conditions()
    service.default_selected_gather_type = app_config_repo.load_selected_gather_type()
    return service
