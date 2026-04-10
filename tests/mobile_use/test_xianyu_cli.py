from minitap.mobile_use.xianyu_cli import main


def test_unified_xianyu_cli_dispatches_to_collector(capsys):
    captured = {}

    def fake_collector(argv=None):
        captured["argv"] = list(argv or [])
        return 0

    exit_code = main(
        ["collector", "--db-path", "collector.db", "doctor", "show-current"],
        collector_main=fake_collector,
    )

    assert exit_code == 0
    assert captured["argv"] == ["--db-path", "collector.db", "doctor", "show-current"]
    assert capsys.readouterr().out == ""


def test_unified_xianyu_cli_dispatches_to_prepare(capsys):
    captured = {}

    def fake_prepare(argv=None):
        captured["argv"] = list(argv or [])

    exit_code = main(["prepare", "--serial", "device-1"], prepare_main=fake_prepare)

    assert exit_code == 0
    assert captured["argv"] == ["--serial", "device-1"]


def test_unified_xianyu_cli_dispatches_to_publish_auto(capsys):
    captured = {}

    def fake_publish_auto(argv=None):
        captured["argv"] = list(argv or [])

    exit_code = main(
        ["publish-auto", "--serial", "device-2"],
        publish_auto_main=fake_publish_auto,
    )

    assert exit_code == 0
    assert captured["argv"] == ["--serial", "device-2"]


def test_unified_xianyu_cli_returns_error_for_unknown_subcommand(capsys):
    exit_code = main(["unknown"])

    assert exit_code == 2
    err = capsys.readouterr().err
    assert "invalid choice" in err or "usage:" in err
