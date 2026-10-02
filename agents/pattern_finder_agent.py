from typing import Any


class PatternFinderAgent:
    """Identify patterns across multiple clinical studies."""

    def analyze(
        self,
        studies: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Find recurring conditions, interventions, and statuses."""

        if not studies:
            return {
                "agent": "pattern_finder",
                "total_studies": 0,
                "conditions": {},
                "interventions": {},
                "statuses": {},
            }

        conditions: dict[str, int] = {}
        interventions: dict[str, int] = {}
        statuses: dict[str, int] = {}

        for study in studies:
            status = study.get("status", "UNKNOWN")
            statuses[status] = statuses.get(status, 0) + 1

            for condition in study.get("conditions", []):
                conditions[condition] = conditions.get(condition, 0) + 1

            for intervention in study.get("interventions", []):
                interventions[intervention] = interventions.get(intervention, 0) + 1

        return {
            "agent": "pattern_finder",
            "total_studies": len(studies),
            "conditions": conditions,
            "interventions": interventions,
            "statuses": statuses,
        }