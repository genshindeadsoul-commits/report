from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.db import get_client

TABLE = "student_reports"


class ReportNotFoundError(Exception):
    pass


class ReportSnapshotService:
    """
    Manages the creation and retrieval of report card snapshots, backed by
    the `student_reports` table (see supabase/migrations/04_student_reports.sql).

    A "snapshot" here is the row's report_payload + version at the moment
    it was generated: publishing/locking doesn't mutate the calculated
    numbers, it just changes status/timestamps, so a published report
    stays stable even if the underlying input is edited later in a new row.
    """

    def create_snapshot(self, report_id: str, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        client = get_client()
        existing = client.table(TABLE).select("version").eq("id", report_id).execute()
        if not existing.data:
            raise ReportNotFoundError(f"No report found with id {report_id}")

        next_version = existing.data[0]["version"] + 1
        result = (
            client.table(TABLE)
            .update({
                "report_payload": payload,
                "version": next_version,
                "status": "generated",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            .eq("id", report_id)
            .execute()
        )
        if not result.data:
            raise ReportNotFoundError(f"Failed to update report {report_id}")

        return {
            "snapshot_id": report_id,
            "version": next_version,
            "created_at": result.data[0]["updated_at"],
        }

    def get_snapshot(self, report_id: str, version: Optional[int] = None) -> Dict[str, Any]:
        client = get_client()
        result = client.table(TABLE).select("*").eq("id", report_id).execute()
        if not result.data:
            raise ReportNotFoundError(f"No report found with id {report_id}")

        row = result.data[0]
        return {
            "version": version or row["version"],
            "payload": row["report_payload"],
            "status": row["status"],
        }

    def publish_report(self, report_id: str) -> Dict[str, Any]:
        client = get_client()
        result = (
            client.table(TABLE)
            .update({"status": "published", "published_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", report_id)
            .execute()
        )
        if not result.data:
            raise ReportNotFoundError(f"No report found with id {report_id}")
        return {"status": "published", "report_id": report_id}

    def lock_report(self, report_id: str) -> Dict[str, Any]:
        client = get_client()
        result = (
            client.table(TABLE)
            .update({"status": "locked", "locked_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", report_id)
            .execute()
        )
        if not result.data:
            raise ReportNotFoundError(f"No report found with id {report_id}")
        return {"status": "locked", "report_id": report_id}
