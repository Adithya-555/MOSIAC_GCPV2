from typing import Any


class TrackRecordAgent:
    """Analyze the historical track record of a clinical study."""

    def analyze(
        self,
        studies: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Summarize study history and outcomes."""
        if not studies:
            return {
                "agent": "track_record",
                "total_studies": 0,
                "completed_studies": 0,
                "terminated_studies": 0,
                "statuses": {},
            }

        statuses: dict[str, int] = {}

        for study in studies:
            status = study.get("status", "UNKNOWN")
            statuses[status] = statuses.get(status, 0) + 1

        completed = statuses.get("COMPLETED", 0)
        terminated = statuses.get("TERMINATED", 0)

        return {
            "agent": "track_record",
            "total_studies": len(studies),
            "completed_studies": completed,
            "terminated_studies": terminated,
            "statuses": statuses,
        }