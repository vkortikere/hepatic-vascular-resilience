"""Synthetic healthy and fragile vascular network generators for validation."""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, MutableMapping, Optional, Sequence, Tuple

from hepatic_vascular_twin.graph.vascular_graph import (
    EdgePair,
    Position3D,
    VascularGraph,
)

EdgeSpec = Tuple[int, int, Dict[str, Any]]
EdgeAttributeMap = Dict[EdgePair, Dict[str, Any]]


def _make_rng(seed: Optional[int]) -> random.Random:
    """Return a seeded random number generator."""
    return random.Random(seed)


def _euclidean_length(a: Position3D, b: Position3D) -> float:
    """Compute the Euclidean length between two 3D positions."""
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def _poiseuille_resistance(length: float, radius: float) -> float:
    """Approximate hydraulic resistance with a simplified Poiseuille relation."""
    return length / (radius**4)


def _edge_exists(u: int, v: int, edges: Sequence[EdgeSpec]) -> bool:
    """Return whether an undirected edge already exists in ``edges``."""
    key = (u, v) if u <= v else (v, u)
    for left, right, _ in edges:
        existing = (left, right) if left <= right else (right, left)
        if existing == key:
            return True
    return False


def _build_backbone(
    positions: MutableMapping[int, Position3D],
    edges: List[EdgeSpec],
    *,
    num_nodes: int,
    spacing: float = 1.0,
) -> List[int]:
    """Create a linear trunk/backbone chain along the x-axis."""
    if num_nodes < 2:
        raise ValueError("backbone requires at least 2 nodes")

    backbone: List[int] = []
    for node_id in range(num_nodes):
        positions[node_id] = (node_id * spacing, 0.0, 0.0)
        backbone.append(node_id)

    for node_id in range(num_nodes - 1):
        edges.append((node_id, node_id + 1, {"role": "backbone"}))

    return backbone


def _next_node_id(positions: MutableMapping[int, Position3D]) -> int:
    """Allocate the next unused integer node id."""
    return max(positions) + 1


def _add_branch(
    parent_id: int,
    positions: MutableMapping[int, Position3D],
    edges: List[EdgeSpec],
    rng: random.Random,
    *,
    branch_index: int,
    branch_length: float,
) -> int:
    """Attach a single branch vessel to ``parent_id`` and return the new node id."""
    child_id = _next_node_id(positions)
    parent_x, parent_y, parent_z = positions[parent_id]
    angle = rng.uniform(0.0, 2.0 * math.pi)
    offset = branch_length * (0.85 + 0.15 * branch_index)
    child_pos = (
        parent_x + offset * math.cos(angle),
        parent_y + offset * math.sin(angle),
        parent_z,
    )
    positions[child_id] = child_pos
    edges.append((parent_id, child_id, {"role": "branch"}))
    return child_id


def _add_branches(
    backbone: Sequence[int],
    positions: MutableMapping[int, Position3D],
    edges: List[EdgeSpec],
    rng: random.Random,
    *,
    branches_per_node: int,
    branch_stride: int,
    branch_length: float,
) -> List[int]:
    """Add lateral branches from selected backbone nodes."""
    branch_tips: List[int] = []
    interior_nodes = list(backbone[1:-1])

    for offset, parent_id in enumerate(interior_nodes):
        if offset % branch_stride != 0:
            continue
        for branch_index in range(branches_per_node):
            tip_id = _add_branch(
                parent_id,
                positions,
                edges,
                rng,
                branch_index=branch_index,
                branch_length=branch_length,
            )
            branch_tips.append(tip_id)

    return branch_tips


def _candidate_shortcut_pairs(
    backbone: Sequence[int],
    branch_tips: Sequence[int],
    edges: Sequence[EdgeSpec],
) -> List[EdgePair]:
    """List backbone and tip pairs that can form shortcut cycles."""
    candidates: List[EdgePair] = []

    for left_index, left_id in enumerate(backbone):
        for right_id in backbone[left_index + 2 :]:
            if not _edge_exists(left_id, right_id, edges):
                candidates.append((left_id, right_id))

    if branch_tips:
        for tip_id in branch_tips:
            for backbone_id in backbone[::2]:
                if tip_id != backbone_id and not _edge_exists(tip_id, backbone_id, edges):
                    candidates.append((tip_id, backbone_id))

    return candidates


def _add_shortcuts(
    backbone: Sequence[int],
    branch_tips: Sequence[int],
    edges: List[EdgeSpec],
    rng: random.Random,
    *,
    shortcut_count: int,
) -> None:
    """Add shortcut vessels that create cycles in an otherwise tree-like scaffold."""
    if shortcut_count <= 0:
        return

    candidates = _candidate_shortcut_pairs(backbone, branch_tips, edges)
    rng.shuffle(candidates)

    added = 0
    for left_id, right_id in candidates:
        if _edge_exists(left_id, right_id, edges):
            continue
        edges.append((left_id, right_id, {"role": "shortcut"}))
        added += 1
        if added >= shortcut_count:
            break


def _assign_edge_attributes(
    positions: Mapping[int, Position3D],
    edge_specs: Sequence[EdgeSpec],
    rng: random.Random,
    *,
    base_radius: float,
) -> Tuple[List[EdgePair], EdgeAttributeMap]:
    """Convert structural edge specs into validated vascular edge attributes."""
    edge_list: List[EdgePair] = []
    edge_attributes: EdgeAttributeMap = {}

    for left_id, right_id, metadata in edge_specs:
        role = metadata.get("role", "vessel")
        start = positions[left_id]
        end = positions[right_id]
        length = _euclidean_length(start, end)

        if role == "backbone":
            radius = base_radius * 1.2
        elif role == "shortcut":
            radius = base_radius * 0.9
        else:
            radius = base_radius * rng.uniform(0.45, 0.75)

        resistance = _poiseuille_resistance(length, radius)
        weight = radius / length

        edge_list.append((left_id, right_id))
        edge_attributes[(left_id, right_id)] = {
            "weight": weight,
            "length": length,
            "radius": radius,
            "resistance": resistance,
            "flow": None,
            "role": role,
        }

    return edge_list, edge_attributes


def _assemble_vascular_graph(
    positions: Mapping[int, Position3D],
    edge_specs: Sequence[EdgeSpec],
    rng: random.Random,
    *,
    base_radius: float,
) -> VascularGraph:
    """Build a ``VascularGraph`` from node positions and structural edge specs."""
    edge_list, edge_attributes = _assign_edge_attributes(
        positions,
        edge_specs,
        rng,
        base_radius=base_radius,
    )
    return VascularGraph.from_edge_list(
        edge_list,
        node_positions=dict(positions),
        edge_attributes=edge_attributes,
    )


def generate_healthy_network(
    *,
    seed: Optional[int] = 42,
    backbone_nodes: int = 7,
    branches_per_node: int = 2,
    branch_length: float = 0.8,
    shortcut_count: int = 3,
    base_radius: float = 0.5,
) -> VascularGraph:
    """Generate a synthetic healthy vascular network with redundant connectivity.

    The network is built from a trunk/backbone graph with dense lateral branching
    and a small number of shortcut vessels that introduce independent cycles.

    Args:
        seed: Random seed for reproducible geometry and branch placement.
        backbone_nodes: Number of nodes in the main trunk/backbone.
        branches_per_node: Branch vessels added at each interior backbone node.
        branch_length: Nominal length scale for branch segments.
        shortcut_count: Number of shortcut edges used to create cycles.
        base_radius: Reference vessel radius for attribute assignment.

    Returns:
        A ``VascularGraph`` with complete edge attributes for Priority 1 analysis.
    """
    rng = _make_rng(seed)
    positions: Dict[int, Position3D] = {}
    edges: List[EdgeSpec] = []

    backbone = _build_backbone(positions, edges, num_nodes=backbone_nodes)
    branch_tips = _add_branches(
        backbone,
        positions,
        edges,
        rng,
        branches_per_node=branches_per_node,
        branch_stride=1,
        branch_length=branch_length,
    )
    _add_shortcuts(
        backbone,
        branch_tips,
        edges,
        rng,
        shortcut_count=shortcut_count,
    )

    return _assemble_vascular_graph(
        positions,
        edges,
        rng,
        base_radius=base_radius,
    )


def generate_fragile_network(
    *,
    seed: Optional[int] = 42,
    backbone_nodes: int = 7,
    branches_per_node: int = 1,
    branch_stride: int = 2,
    branch_length: float = 0.6,
    base_radius: float = 0.35,
) -> VascularGraph:
    """Generate a synthetic fragile vascular network that is sparse and tree-like.

    The network shares the same trunk/backbone construction strategy as the
    healthy generator, but uses narrower branching and omits shortcut vessels so
    the resulting topology remains acyclic and less redundant.

    Args:
        seed: Random seed for reproducible geometry and branch placement.
        backbone_nodes: Number of nodes in the main trunk/backbone.
        branches_per_node: Branch vessels added at selected backbone nodes.
        branch_stride: Add branches every ``branch_stride`` interior backbone nodes.
        branch_length: Nominal length scale for branch segments.
        base_radius: Reference vessel radius for attribute assignment.

    Returns:
        A ``VascularGraph`` with complete edge attributes for Priority 1 analysis.
    """
    rng = _make_rng(seed)
    positions: Dict[int, Position3D] = {}
    edges: List[EdgeSpec] = []

    backbone = _build_backbone(positions, edges, num_nodes=backbone_nodes)
    _add_branches(
        backbone,
        positions,
        edges,
        rng,
        branches_per_node=branches_per_node,
        branch_stride=branch_stride,
        branch_length=branch_length,
    )

    return _assemble_vascular_graph(
        positions,
        edges,
        rng,
        base_radius=base_radius,
    )
