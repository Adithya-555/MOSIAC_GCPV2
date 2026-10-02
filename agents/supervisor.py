from typing import Any


class SupervisorAgent:
    """Coordinate the specialized clinical analysis agents."""

    def __init__(self):
        self.agent_names = [
            "timeline_agent",
            "track_record_agent",
            "side_effect_agent",
            "missing_results_agent",
            "broken_promises_agent",
            "pattern_finder_agent",
        ]

    def get_agent_names(self) -> list[str]:
        """Return the available specialized agents."""
        return self.agent_names.copy()

    def create_plan(self, query: str) -> dict[str, Any]:
        """Create a basic analysis plan."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        return {
            "query": query,
            "agents": self.get_agent_names(),
            "status": "planned",
        }