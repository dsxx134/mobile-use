from minitap.mobile_use.collectors.xianyu_collector.session.saved_cookie_provider import SavedCookieProvider


def test_saved_cookie_provider_parses_cookie_string_with_standard_parser():
    provider = SavedCookieProvider(
        "cna=abc; _m_h5_tk=token123_777; _m_h5_tk_enc=enc999; other=value"
    )

    assert provider.get_cookie_string() == (
        "cna=abc; _m_h5_tk=token123_777; _m_h5_tk_enc=enc999; other=value"
    )
    assert provider.get_cookie_dict() == {
        "cna": "abc",
        "_m_h5_tk": "token123_777",
        "_m_h5_tk_enc": "enc999",
        "other": "value",
    }
