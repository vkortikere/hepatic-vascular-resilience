"""Standard graph metrics for vascular networks."""

from __future__ import annotations

from typing import Any

from hepatic_vascular_twin.graph.vascular_graph import VascularGraph


def compute_graph_metrics(graph: VascularGraph) -> dict[str, Any]:
    """Compute degree, centrality, clustering, and path-based metrics."""
    raise NotImplementedError("Priority 1 implementation pending.")
