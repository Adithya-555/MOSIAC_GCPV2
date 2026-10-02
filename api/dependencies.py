from functools import lru_cache

from graph.graph_builder import build_graph


@lru_cache
def get_analysis_graph():
    """Return the shared analysis graph."""
    return build_graph()