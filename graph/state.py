from typing import Any, TypedDict


class AnalysisState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes."""

    query: str

    studies: list[dict[str, Any]]
    papers: list[dict[str, Any]]

    # Memory context retrieved before analysis
    semantic_memory: list[dict[str, Any]]
    episodic_memory: list[dict[str, Any]]
    procedural_memory: list[dict[str, Any]]

    timeline_analysis: dict[str, Any]
    track_record_analysis: dict[str, Any]
    side_effect_analysis: dict[str, Any]
    missing_results_analysis: dict[str, Any]
    broken_promises_analysis: dict[str, Any]
    pattern_analysis: dict[str, Any]

    final_analysis: dict[str, Any]

    errors: list[str]