from __future__ import annotations

from dataclasses import dataclass


APP_KEY = "34839810"
JSV = "2.7.2"
TIMEOUT = "20000"


@dataclass(frozen=True, slots=True)
class EndpointSpec:
    url: str
    api: str
    version: str
    spm_cnt: str | None = None
    spm_pre: str | None = None
    value_type: str | None = None


SEARCH_ENDPOINT = EndpointSpec(
    url="https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/",
    api="mtop.taobao.idlemtopsearch.pc.search",
    version="1.0",
    spm_cnt="a21ybx.search.0.0",
    spm_pre="a21ybx.home.searchInput.0",
)

DETAIL_ENDPOINT = EndpointSpec(
    url="https://h5api.m.goofish.com/h5/mtop.taobao.idle.pc.detail/1.0/",
    api="mtop.taobao.idle.pc.detail",
    version="1.0",
)

SHOP_LIST_ENDPOINT = EndpointSpec(
    url="https://h5api.m.goofish.com/h5/mtop.idle.web.xyh.item.list/1.0/",
    api="mtop.idle.web.xyh.item.list",
    version="1.0",
    spm_cnt="a21ybx.personal.0.0",
    spm_pre="a21ybx.item.itemHeader.1.51ad3da6JLc44p",
)

USER_HEAD_ENDPOINT = EndpointSpec(
    url="https://h5api.m.goofish.com/h5/mtop.idle.web.user.page.head/1.0/",
    api="mtop.idle.web.user.page.head",
    version="1.0",
    spm_cnt="a21ybx.personal.0.0",
    spm_pre="a21ybx.item.itemHeader.1.51ad3da6JLc44p",
)

MULTI_SPEC_ENDPOINT = EndpointSpec(
    url="https://h5api.m.goofish.com/h5/mtop.taobao.idle.trade.order.render/7.0/",
    api="mtop.taobao.idle.trade.order.render",
    version="7.0",
    spm_cnt="a21ybx.create-order.0.0",
    value_type="string",
)
