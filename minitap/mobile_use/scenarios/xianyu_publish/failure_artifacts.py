import base64
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService


class XianyuFailureArtifacts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    captured_at: str
    artifact_dir: str
    screenshot_path: str | None = None
    hierarchy_path: str | None = None
    activity_dump_path: str | None = None
    current_app: str | None = None


class XianyuFailureArtifactRecorder:
    def __init__(
        self,
        *,
        android_service: AndroidDebugService | None = None,
        root: Path | None = None,
        now_fn: Any | None = None,
    ) -> None:
        self._android = android_service or AndroidDebugService()
        self._root = (root or Path(".tmp") / "xianyu-failures").resolve()
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def capture(
        self,
        *,
        serial: str,
        record_id: str,
        stage: str,
        error_message: str,
    ) -> XianyuFailureArtifacts:
        captured_at = self._now_fn().isoformat()
        timestamp = (
            captured_at.replace(":", "")
            .replace("-", "")
            .replace("+", "p")
            .replace(".", "")
        )
        artifact_dir = self._root / record_id / f"{timestamp}-{stage}"
        artifact_dir.mkdir(parents=True, exist_ok=True)

        screen_data = self._android.get_screen_data(serial)
        activity_dump = self._android.dump_activity_activities(serial)

        screenshot_path = artifact_dir / "screen.png"
        screenshot_path.write_bytes(base64.b64decode(screen_data["base64"]))

        hierarchy_path = artifact_dir / "hierarchy.xml"
        hierarchy_path.write_text(str(screen_data["hierarchy_xml"]), encoding="utf-8")

        activity_dump_path = artifact_dir / "activities.txt"
        activity_dump_path.write_text(str(activity_dump["raw_output"]), encoding="utf-8")

        current_app = screen_data.get("current_app") or {}
        current_app_value = self._format_current_app(current_app)

        summary_path = artifact_dir / "summary.txt"
        summary_path.write_text(
            "\n".join(
                [
                    f"captured_at={captured_at}",
                    f"serial={serial}",
                    f"record_id={record_id}",
                    f"stage={stage}",
                    f"error={error_message}",
                    f"current_app={current_app_value or ''}",
                ]
            ),
            encoding="utf-8",
        )

        return XianyuFailureArtifacts(
            captured_at=captured_at,
            artifact_dir=str(artifact_dir),
            screenshot_path=str(screenshot_path),
            hierarchy_path=str(hierarchy_path),
            activity_dump_path=str(activity_dump_path),
            current_app=current_app_value,
        )

    def _format_current_app(self, current_app: dict[str, Any]) -> str | None:
        package = current_app.get("package")
        activity = current_app.get("activity")
        if not package and not activity:
            return None
        if package and activity:
            return f"{package}/{activity}"
        return str(package or activity)
