import pytest

from minitap.mobile_use.collectors.xianyu_collector.signing.mtop_signer import MissingTokenError, MtopSigner


def test_signer_uses_m_h5_tk_prefix_before_underscore():
    signer = MtopSigner(time_provider=lambda: 1710000000.123)

    sign, timestamp = signer.sign(
        cookies={"_m_h5_tk": "abc123_999999"},
        payload={"data": '{"itemId":"555"}'},
    )

    assert sign == "6383bf15c4dcad7e4780fc7690cfe7cc"
    assert timestamp == 1710000000123


def test_signer_falls_back_to_tfstk_when_m_h5_tk_is_missing():
    signer = MtopSigner(time_provider=lambda: 1710000000.123)

    sign, timestamp = signer.sign(
        cookies={"tfstk": "token456"},
        payload={"data": '{"pageNumber":1,"keyword":"test"}'},
    )

    assert sign == "153c43336cfa85767b623da296d36fbb"
    assert timestamp == 1710000000123


def test_signer_raises_when_no_supported_token_exists():
    signer = MtopSigner(time_provider=lambda: 1710000000.123)

    with pytest.raises(MissingTokenError, match="missing signing token"):
        signer.sign(cookies={}, payload={"data": "{}"})
