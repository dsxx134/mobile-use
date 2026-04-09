import json

import pytest

from minitap.mobile_use.collectors.xianyu_collector.session.bitbrowser_browser_session import (
    BitBrowserBrowserSession,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class FakeRequests:
    def __init__(self, *, open_payload, targets_payload):
        self.open_payload = open_payload
        self.targets_payload = targets_payload
        self.post_calls = []
        self.get_calls = []

    def post(self, url, json=None, timeout=None):
        self.post_calls.append((url, json, timeout))
        return FakeResponse(self.open_payload)

    def get(self, url, timeout=None):
        self.get_calls.append((url, timeout))
        return FakeResponse(self.targets_payload)


class SequencedOpenRequests(FakeRequests):
    def __init__(self, *, open_payloads, targets_payload):
        self.open_payloads = list(open_payloads)
        self.targets_payload = targets_payload
        self.post_calls = []
        self.get_calls = []

    def post(self, url, json=None, timeout=None):
        self.post_calls.append((url, json, timeout))
        return FakeResponse(self.open_payloads[len(self.post_calls) - 1])


class FakeSocket:
    def __init__(self, cookie_batches):
        self.cookie_batches = list(cookie_batches)
        self.closed = False
        self.sent_messages = []

    def send(self, raw_message: str):
        self.sent_messages.append(json.loads(raw_message))

    def recv(self) -> str:
        last_message = self.sent_messages[-1]
        current_batch = self.cookie_batches.pop(0)
        return json.dumps({"id": last_message["id"], "result": {"cookies": current_batch}})

    def close(self):
        self.closed = True


def test_bitbrowser_browser_session_opens_browser_and_returns_cookie_string():
    fake_requests = FakeRequests(
        open_payload={"success": True, "data": {"http": "127.0.0.1:58682"}},
        targets_payload=[
            {"type": "service_worker", "url": "https://www.goofish.com/worker.js"},
            {
                "type": "page",
                "url": "https://www.goofish.com/search?q=gemini",
                "webSocketDebuggerUrl": "ws://debugger/page-1",
            },
        ],
    )
    fake_socket = FakeSocket(
        [[{"name": "cookie2", "value": "abc"}, {"name": "_m_h5_tk", "value": "token"}]]
    )

    session = BitBrowserBrowserSession(
        browser_id="browser-123",
        requests_module=fake_requests,
        websocket_factory=lambda url: fake_socket,
        sleep=lambda _seconds: None,
        max_wait_cycles=1,
    )

    cookie_string = session.get_cookie_string("https://www.goofish.com/")

    assert cookie_string == "cookie2=abc; _m_h5_tk=token"
    assert fake_requests.post_calls == [
        ("http://127.0.0.1:54345/browser/open", {"id": "browser-123"}, 10)
    ]
    assert fake_requests.get_calls == [("http://127.0.0.1:58682/json", 10)]
    assert fake_socket.closed is True


def test_bitbrowser_browser_session_waits_until_m_h5_tk_is_available():
    fake_requests = FakeRequests(
        open_payload={"success": True, "data": {"http": "127.0.0.1:58682"}},
        targets_payload=[
            {
                "type": "page",
                "url": "https://www.goofish.com/",
                "webSocketDebuggerUrl": "ws://debugger/page-1",
            }
        ],
    )
    fake_socket = FakeSocket(
        [
            [{"name": "cookie2", "value": "abc"}],
            [{"name": "cookie2", "value": "abc"}, {"name": "_m_h5_tk", "value": "token"}],
        ]
    )

    session = BitBrowserBrowserSession(
        browser_id="browser-123",
        requests_module=fake_requests,
        websocket_factory=lambda url: fake_socket,
        sleep=lambda _seconds: None,
        max_wait_cycles=2,
    )

    cookie_string = session.get_cookie_string("https://www.goofish.com/")

    assert cookie_string == "cookie2=abc; _m_h5_tk=token"
    assert len(fake_socket.sent_messages) == 2


def test_bitbrowser_browser_session_raises_when_browser_open_fails():
    fake_requests = FakeRequests(
        open_payload={"success": False, "message": "browser offline"},
        targets_payload=[],
    )

    session = BitBrowserBrowserSession(
        browser_id="browser-123",
        requests_module=fake_requests,
        websocket_factory=lambda _url: None,
        sleep=lambda _seconds: None,
        max_wait_cycles=1,
    )

    with pytest.raises(RuntimeError, match="browser offline"):
        session.get_cookie_string("https://www.goofish.com/")


def test_bitbrowser_browser_session_retries_when_browser_is_still_opening():
    fake_requests = SequencedOpenRequests(
        open_payloads=[
            {"success": False, "msg": "浏览器正在打开中"},
            {"success": True, "data": {"http": "127.0.0.1:58682"}},
        ],
        targets_payload=[
            {
                "type": "page",
                "url": "https://www.goofish.com/",
                "webSocketDebuggerUrl": "ws://debugger/page-1",
            }
        ],
    )
    fake_socket = FakeSocket(
        [[{"name": "_m_h5_tk", "value": "token"}, {"name": "unb", "value": "123"}]]
    )

    session = BitBrowserBrowserSession(
        browser_id="browser-123",
        requests_module=fake_requests,
        websocket_factory=lambda url: fake_socket,
        sleep=lambda _seconds: None,
        max_wait_cycles=1,
        max_open_attempts=2,
    )

    cookie_string = session.get_cookie_string("https://www.goofish.com/")

    assert cookie_string == "_m_h5_tk=token; unb=123"
    assert len(fake_requests.post_calls) == 2
