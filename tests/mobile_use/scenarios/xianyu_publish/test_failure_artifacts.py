from datetime import UTC, datetime
import base64

from minitap.mobile_use.scenarios.xianyu_publish.failure_artifacts import (
    XianyuFailureArtifactRecorder,
)


def test_failure_artifact_recorder_writes_debug_files(tmp_path):
    android_service = type(
        "FakeAndroidService",
        (),
        {
            "get_screen_data": lambda self, serial: {
                "serial": serial,
                "base64": base64.b64encode(b"png-bytes").decode("utf-8"),
                "hierarchy_xml": "<hierarchy />",
                "current_app": {
                    "package": "com.taobao.idlefish",
                    "activity": "com.taobao.idlefish.maincontainer.activity.MainActivity",
                },
                "width": 1600,
                "height": 2560,
                "element_count": 0,
                "elements": [],
            },
            "dump_activity_activities": lambda self, serial: {
                "serial": serial,
                "raw_output": "ACTIVITY com.taobao.idlefish/.MainActivity",
            },
        },
    )()
    recorder = XianyuFailureArtifactRecorder(
        android_service=android_service,
        root=tmp_path,
        now_fn=lambda: datetime(2026, 3, 15, 4, 30, 0, tzinfo=UTC),
    )

    artifacts = recorder.capture(
        serial="device-1",
        record_id="recA",
        stage="prepare",
        error_message="price panel missing",
    )

    assert artifacts.captured_at == "2026-03-15T04:30:00+00:00"
    assert artifacts.current_app == (
        "com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity"
    )
    assert artifacts.screenshot_path is not None
    assert artifacts.hierarchy_path is not None
    assert artifacts.activity_dump_path is not None
    assert artifacts.artifact_dir.endswith("recA\\20260315T043000p0000-prepare")
    assert (tmp_path / "recA" / "20260315T043000p0000-prepare" / "screen.png").read_bytes() == (
        b"png-bytes"
    )
    assert (
        tmp_path / "recA" / "20260315T043000p0000-prepare" / "hierarchy.xml"
    ).read_text(encoding="utf-8") == "<hierarchy />"
    assert (
        tmp_path / "recA" / "20260315T043000p0000-prepare" / "activities.txt"
    ).read_text(encoding="utf-8") == "ACTIVITY com.taobao.idlefish/.MainActivity"
