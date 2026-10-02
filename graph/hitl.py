from typing import Any


class HumanReview:
    """Handle human review of analysis results."""

    def review(
        self,
        analysis: dict[str, Any],
        approved: bool = False,
        feedback: str = "",
    ) -> dict[str, Any]:
        """Record a human review decision."""

        return {
            "approved": approved,
            "feedback": feedback,
            "analysis": analysis,
            "status": "approved" if approved else "pending",
        }