from typing import Any


class TimelineAgent:
    """Analyze the timeline of a clinical trial."""

    def analyze(
        self,
        study: dict[str, Any],
        memory: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Extract important timeline information from a study."""

        memory = memory or []

        return {
            "agent": "timeline",
            "nct_id": study.get("nct_id"),
            "start_date": study.get("start_date"),
            "completion_date": study.get("completion_date"),
            "status": study.get("status"),
            "results_posted": study.get("results_posted", False),
            "related_memory_count": len(memory),
            "related_memory": memory,
        }