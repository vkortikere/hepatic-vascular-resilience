"""Vessel removal and edge-modification perturbation experiments."""

from __future__ import annotations

from typing import Any

from hepatic_vascular_twin.graph.vascular_graph import VascularGraph


def run_perturbation_study(
    graph: VascularGraph,
    *,
    seed: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Simulate progressive vessel loss and record downstream metric changes."""
    raise NotImplementedError("Priority 1 implementation pending.")
