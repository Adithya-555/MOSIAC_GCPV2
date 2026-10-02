from typing import Any


class FinalSynthesisAgent:
    """Combine all analysis-agent outputs into one final clinical trial analysis."""

    def synthesize(
        self,
        timeline_analysis: dict[str, Any],
        track_record_analysis: dict[str, Any],
        side_effect_analysis: dict[str, Any],
        missing_results_analysis: dict[str, Any],
        broken_promises_analysis: dict[str, Any],
        pattern_analysis: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "agent": "final_synthesis",

            "summary": {
                "timeline": self._summarize_section(
                    timeline_analysis
                ),
                "track_record": self._summarize_section(
                    track_record_analysis
                ),
                "side_effects": self._summarize_section(
                    side_effect_analysis
                ),
                "missing_results": self._summarize_section(
                    missing_results_analysis
                ),
                "broken_promises": self._summarize_section(
                    broken_promises_analysis
                ),
                "patterns": self._summarize_section(
                    pattern_analysis
                ),
            },

            "timeline_analysis": timeline_analysis,
            "track_record_analysis": track_record_analysis,
            "side_effect_analysis": side_effect_analysis,
            "missing_results_analysis": missing_results_analysis,
            "broken_promises_analysis": broken_promises_analysis,
            "pattern_analysis": pattern_analysis,
        }

    @staticmethod
    def _summarize_section(section: dict[str, Any]) -> dict[str, Any]:
        if not section:
            return {
                "available": False,
                "data": {},
            }

        return {
            "available": True,
            "data": section,
        }