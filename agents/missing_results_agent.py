from typing import Any


class MissingResultsAgent:
    """Identify clinical trials that appear to be missing results."""

    def analyze(self, study: dict[str, Any]) -> dict[str, Any]:
        """Check whether a completed study has posted results."""

        status = str(study.get("status", "")).upper()
        results_posted = bool(study.get("results_posted", False))

        missing_results = (
            status in {"COMPLETED", "TERMINATED"}
            and not results_posted
        )

        return {
            "agent": "missing_results",
            "nct_id": study.get("nct_id"),
            "status": status,
            "results_posted": results_posted,
            "missing_results": missing_results,
        }