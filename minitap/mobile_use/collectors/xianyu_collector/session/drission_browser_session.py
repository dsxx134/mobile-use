from __future__ import annotations

import time
from typing import Any, Callable


class DrissionBrowserSession:
    def __init__(
        self,
        *,
        local_port: str = "9222",
        browser_path_resolver: Callable[[], str] | None = None,
        options_factory: Callable[[], Any] | None = None,
        chromium_factory: Callable[[Any], Any] | None = None,
        sleep: Callable[[float], None] | None = None,
        max_wait_cycles: int = 20,
    ):
        self.local_port = local_port
        self.browser_path_resolver = browser_path_resolver or self._default_browser_path_resolver
        self.options_factory = options_factory or self._default_options_factory
        self.chromium_factory = chromium_factory or self._default_chromium_factory
        self.sleep = sleep or time.sleep
        self.max_wait_cycles = max_wait_cycles

    def get_cookie_string(self, url: str) -> str:
        options = self.options_factory()
        browser_path = self.browser_path_resolver()
        if browser_path and hasattr(options, "set_browser_path"):
            options.set_browser_path(browser_path)
        if self.local_port and hasattr(options, "set_local_port"):
            options.set_local_port(self.local_port)

        browser = self.chromium_factory(options)
        tab = browser.latest_tab
        tab.get(url)

        try:
            for _ in range(self.max_wait_cycles):
                jar = tab.cookies()
                if jar.as_dict().get("_m_h5_tk"):
                    return jar.as_str()
                self.sleep(1)
            raise RuntimeError("browser session did not return _m_h5_tk in time")
        finally:
            try:
                tab.browser.quit()
            except Exception:
                pass

    @staticmethod
    def _default_options_factory() -> Any:
        from DrissionPage import ChromiumOptions

        return ChromiumOptions()

    @staticmethod
    def _default_chromium_factory(options: Any) -> Any:
        from DrissionPage import Chromium

        return Chromium(options)

    @staticmethod
    def _default_browser_path_resolver() -> str:
        return ""
