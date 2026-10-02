from typing import Any


class BrokenPromisesAgent:

    def analyze(self, studies: list[dict[str, Any]]) -> dict[str, Any]:
        if not studies:
            return {
                "agent": "broken_promises",
                "total_studies": 0,
                "findings": [],
            }

        study = studies[0]

        nct_id = study.get("nct_id", "")
        planned_outcome = study.get("primary_outcome", "")

        raw_data = study.get("raw_data", {})

        protocol = raw_data.get("protocolSection", {})
        results = raw_data.get("resultsSection", {})

        # Get all reported outcome measures from the results section
        outcome_measures = results.get("outcomeMeasuresModule", {}).get(
            "outcomeMeasures", []
        )

        reported_outcomes = []

        for outcome in outcome_measures:
            title = outcome.get("title", "")

            if title:
                reported_outcomes.append(title)

        # Compare the planned primary outcome with reported outcomes
        matched_outcome = None

        planned_lower = planned_outcome.strip().lower()

        for reported in reported_outcomes:
            if reported.strip().lower() == planned_lower:
                matched_outcome = reported
                break

        outcome_missing = bool(planned_outcome) and matched_outcome is None

        return {
            "agent": "broken_promises",
            "nct_id": nct_id,
            "planned_outcome": planned_outcome,
            "reported_outcome": matched_outcome or "",
            "outcome_missing": outcome_missing,
            "reported_outcomes": reported_outcomes,
        }