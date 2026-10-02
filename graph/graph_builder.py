from typing import Any

from langgraph.graph import END, START, StateGraph

from agents.broken_promises_agent import BrokenPromisesAgent
from agents.final_synthesis_agent import FinalSynthesisAgent
from agents.missing_results_agent import MissingResultsAgent
from agents.pattern_finder_agent import PatternFinderAgent
from agents.side_effect_agent import SideEffectAgent
from agents.timeline_agent import TimelineAgent
from agents.track_record_agent import TrackRecordAgent

from graph.state import AnalysisState

from memory.semantic_store import SemanticMemoryStore
from memory.episodic_store import EpisodicMemoryStore
from memory.procedural_store import ProceduralMemoryStore


timeline_agent = TimelineAgent()
track_record_agent = TrackRecordAgent()
side_effect_agent = SideEffectAgent()
missing_results_agent = MissingResultsAgent()
broken_promises_agent = BrokenPromisesAgent()
pattern_finder_agent = PatternFinderAgent()
final_synthesis_agent = FinalSynthesisAgent()


# ---------------------------------------------------------
# MEMORY STORES
# ---------------------------------------------------------

semantic_memory_store = SemanticMemoryStore()
episodic_memory_store = EpisodicMemoryStore()
procedural_memory_store = ProceduralMemoryStore()


# ---------------------------------------------------------
# MEMORY RETRIEVAL
# ---------------------------------------------------------

async def memory_retrieval_node(
    state: AnalysisState,
) -> dict[str, Any]:
    """Retrieve relevant memories before analysis."""

    query = state.get("query", "").strip()

    if not query:
        return {
            "semantic_memory": [],
            "episodic_memory": [],
            "procedural_memory": [],
        }

    semantic_memory = []
    episodic_memory = []
    procedural_memory = []

    try:
        semantic_memory = await semantic_memory_store.search(
            query=query,
            limit=5,
        )
    except Exception:
        semantic_memory = []

    try:
        episodic_memory = await episodic_memory_store.search(
            limit=5,
        )
    except Exception:
        episodic_memory = []

    try:
        procedural_memory = await procedural_memory_store.list_all(
            limit=10,
        )
    except Exception:
        procedural_memory = []

    return {
        "semantic_memory": semantic_memory,
        "episodic_memory": episodic_memory,
        "procedural_memory": procedural_memory,
    }


# ---------------------------------------------------------
# ANALYSIS NODES
# ---------------------------------------------------------

def timeline_node(
    state: AnalysisState,
) -> dict[str, Any]:

    studies = state.get("studies", [])

    if not studies:
        return {
            "timeline_analysis": {}
        }

    # Combine relevant memories for timeline analysis
    memory = (
        state.get("semantic_memory", [])
        + state.get("episodic_memory", [])
    )

    analyses = []

    for study in studies:
        analyses.append(
            timeline_agent.analyze(
                study,
                memory=memory,
            )
        )

    return {
        "timeline_analysis": {
            "total_studies": len(studies),
            "studies": analyses,
        }
    }

def track_record_node(
    state: AnalysisState,
) -> dict[str, Any]:

    studies = state.get("studies", [])

    return {
        "track_record_analysis": (
            track_record_agent.analyze(studies)
        )
    }


def side_effect_node(
    state: AnalysisState,
) -> dict[str, Any]:

    studies = state.get("studies", [])

    if not studies:
        return {
            "side_effect_analysis": {}
        }

    analyses = []

    for study in studies:
        analyses.append(
            side_effect_agent.analyze(study)
        )

    return {
        "side_effect_analysis": {
            "total_studies": len(studies),
            "studies": analyses,
        }
    }


def missing_results_node(
    state: AnalysisState,
) -> dict[str, Any]:

    studies = state.get("studies", [])

    if not studies:
        return {
            "missing_results_analysis": {}
        }

    analyses = []

    for study in studies:
        analyses.append(
            missing_results_agent.analyze(study)
        )

    return {
        "missing_results_analysis": {
            "total_studies": len(studies),
            "studies": analyses,
        }
    }


def broken_promises_node(
    state: AnalysisState,
) -> dict[str, Any]:

    studies = state.get("studies", [])

    if not studies:
        return {
            "broken_promises_analysis": {}
        }

    analyses = []

    for study in studies:
        analyses.append(
            broken_promises_agent.analyze([study])
        )

    return {
        "broken_promises_analysis": {
            "total_studies": len(studies),
            "studies": analyses,
        }
    }


def pattern_finder_node(
    state: AnalysisState,
) -> dict[str, Any]:

    studies = state.get("studies", [])

    return {
        "pattern_analysis": (
            pattern_finder_agent.analyze(studies)
        )
    }

def final_synthesis_node(state: AnalysisState) -> dict[str, Any]:
    return {
        "final_analysis": final_synthesis_agent.synthesize(
            timeline_analysis=state.get("timeline_analysis", {}),
            track_record_analysis=state.get(
                "track_record_analysis",
                {},
            ),
            side_effect_analysis=state.get(
                "side_effect_analysis",
                {},
            ),
            missing_results_analysis=state.get(
                "missing_results_analysis",
                {},
            ),
            broken_promises_analysis=state.get(
                "broken_promises_analysis",
                {},
            ),
            pattern_analysis=state.get(
                "pattern_analysis",
                {},
            ),
        )
    }


# ---------------------------------------------------------
# MEMORY SAVE
# ---------------------------------------------------------

async def memory_save_node(
    state: AnalysisState,
) -> dict[str, Any]:
    """Save useful information from the completed analysis."""

    query = state.get("query", "").strip()
    studies = state.get("studies", [])

    if not query:
        return {}

    # -----------------------------------------------------
    # Save episodic memory
    # -----------------------------------------------------

    try:
        await episodic_memory_store.save(
            event_type="clinical_trial_analysis",
            description=(
                f"MOSIAC completed an analysis for query: {query}"
            ),
            metadata={
                "query": query,
                "study_count": len(studies),
                "nct_ids": [
                    study.get("nct_id")
                    for study in studies
                    if study.get("nct_id")
                ],
            },
        )
    except Exception:
        pass

    # -----------------------------------------------------
    # Save semantic memory
    # -----------------------------------------------------

    if studies:

        try:
            for study in studies:

                nct_id = study.get("nct_id")

                if not nct_id:
                    continue

                title = study.get("title", "")
                status = study.get("status", "")
                sponsor = study.get("sponsor", "")

                content = (
                    f"Clinical trial {nct_id}: "
                    f"{title}. "
                    f"Status: {status}. "
                    f"Sponsor: {sponsor}."
                )

                await semantic_memory_store.save(
                    memory_key=f"trial:{nct_id}",
                    content=content,
                    metadata={
                        "nct_id": nct_id,
                        "status": status,
                        "sponsor": sponsor,
                    },
                )

        except Exception:
            pass

    return {}


# ---------------------------------------------------------
# GRAPH
# ---------------------------------------------------------

def build_graph():

    builder = StateGraph(AnalysisState)

    # Memory
    builder.add_node(
        "memory_retrieval",
        memory_retrieval_node,
    )

    # Analysis
    builder.add_node(
        "timeline",
        timeline_node,
    )

    builder.add_node(
        "track_record",
        track_record_node,
    )

    builder.add_node(
        "side_effect",
        side_effect_node,
    )

    builder.add_node(
        "missing_results",
        missing_results_node,
    )

    builder.add_node(
        "broken_promises",
        broken_promises_node,
    )

    builder.add_node(
        "pattern_finder",
        pattern_finder_node,
    )

    builder.add_node(
        "final_synthesis",
        final_synthesis_node,
    )

    builder.add_node(
        "memory_save",
        memory_save_node,
    )

    # Graph flow
    builder.add_edge(
        START,
        "memory_retrieval",
    )

    builder.add_edge(
        "memory_retrieval",
        "timeline",
    )

    builder.add_edge(
        "timeline",
        "track_record",
    )

    builder.add_edge(
        "track_record",
        "side_effect",
    )

    builder.add_edge(
        "side_effect",
        "missing_results",
    )

    builder.add_edge(
        "missing_results",
        "broken_promises",
    )

    builder.add_edge(
        "broken_promises",
        "pattern_finder",
    )

    builder.add_edge(
        "pattern_finder",
        "final_synthesis",
    )

    builder.add_edge(
        "final_synthesis",
        "memory_save",
    )

    builder.add_edge(
        "memory_save",
        END,
    )

    return builder.compile()