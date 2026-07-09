"""Filtration strategies for vascular topology (length, radius, flow, geometry)."""

from __future__ import annotations

from typing import Any, Literal

from hepatic_vascular_twin.graph.vascular_graph import VascularGraph

FiltrationKind = Literal["length", "radius", "flow", "weight"]


def build_filtration(
    graph: VascularGraph,
    *,
    kind: FiltrationKind = "length",
    **kwargs: Any,
) -> Any:
    """Define a filtration on the vascular graph for persistent homology."""
    raise NotImplementedError("Priority 1 implementation pending.")
