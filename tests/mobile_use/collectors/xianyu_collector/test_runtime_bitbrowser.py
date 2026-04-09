from pathlib import Path

from minitap.mobile_use.collectors.xianyu_collector.repository.app_config_repo import AppConfigRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.runtime import build_collector_service


def test_build_collector_service_prefers_bitbrowser_when_browser_id_env_is_set(tmp_path, monkeypatch):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_saved_cookie_string("")

    captured = {}

    class FakeSavedCookieProvider:
        def __init__(self, cookie_string: str):
            captured["saved_cookie_string"] = cookie_string

    class FakeBitBrowserBrowserSession:
        def __init__(self, **kwargs):
            captured["bitbrowser_session_kwargs"] = kwargs

    class FakeDrissionBrowserSession:
        def __init__(self, **kwargs):
            captured["drission_session_kwargs"] = kwargs

    class FakeBrowserCookieProvider:
        def __init__(self, session, url: str):
            captured["browser_provider_url"] = url
            captured["browser_provider_session"] = session

    class FakeAnonymousBootstrapCookieProvider:
        def __init__(self, **kwargs):
            captured["bootstrap_kwargs"] = kwargs

    class FakeFallbackCookieProvider:
        def __init__(self, providers):
            self.providers = list(providers)
            captured["providers"] = self.providers

    monkeypatch.setenv("XIANYU_COLLECTOR_BITBROWSER_ID", "bitbrowser-123")
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.runtime.SavedCookieProvider",
        FakeSavedCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.runtime.BitBrowserBrowserSession",
        FakeBitBrowserBrowserSession,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.runtime.DrissionBrowserSession",
        FakeDrissionBrowserSession,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.runtime.BrowserCookieProvider",
        FakeBrowserCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.runtime.AnonymousBootstrapCookieProvider",
        FakeAnonymousBootstrapCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.runtime.FallbackCookieProvider",
        FakeFallbackCookieProvider,
    )

    service = build_collector_service(Path(tmp_path / "collector.db"))

    assert captured["saved_cookie_string"] == ""
    assert captured["bitbrowser_session_kwargs"] == {
        "browser_id": "bitbrowser-123",
        "api_host": "127.0.0.1",
        "api_port": 54345,
    }
    assert "drission_session_kwargs" not in captured
    assert captured["browser_provider_url"] == "https://www.goofish.com/"
    assert len(captured["providers"]) == 3
    assert service.api_client.cookie_provider is not None
