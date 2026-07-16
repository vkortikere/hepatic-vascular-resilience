"""Tests for synthetic network generators."""

from __future__ import annotations

import networkx as nx
import pytest

from hepatic_vascular_twin.graph.synthetic_networks import (
    generate_fragile_network,
    generate_healthy_network,
)
from hepatic_vascular_twin.graph.vascular_graph import VascularGraph

REQUIRED_EDGE_ATTRS = ("weight", "length", "radius", "resistance")


def _graph_signature(graph: VascularGraph) -> tuple:
    """Build a deterministic signature for graph comparison."""
    edge_data = []
    for left_id, right_id in graph.edge_pairs():
        attrs = graph.get_edge(left_id, right_id)
        edge_data.append(
            (
                left_id,
                right_id,
                attrs["weight"],
                attrs["length"],
                attrs["radius"],
                attrs["resistance"],
                attrs.get("role"),
            )
        )
    return (tuple(graph.node_ids()), tuple(edge_data))


def _cycle_count(graph: VascularGraph) -> int:
    """Count independent cycles using NetworkX cycle basis."""
    return len(nx.cycle_basis(graph.to_networkx()))


def _average_degree(graph: VascularGraph) -> float:
    """Return the average node degree of the exported NetworkX graph."""
    nx_graph = graph.to_networkx()
    if nx_graph.number_of_nodes() == 0:
        return 0.0
    degrees = [degree for _, degree in nx_graph.degree()]
    return sum(degrees) / len(degrees)


def _assert_valid_edge_attributes(graph: VascularGraph) -> None:
    """Verify all edges satisfy VascularGraph attribute rules."""
    assert graph.has_required_edge_attributes(*REQUIRED_EDGE_ATTRS)
    assert graph.missing_edge_attributes(*REQUIRED_EDGE_ATTRS) == {}

    for left_id, right_id in graph.edge_pairs():
        attrs = graph.get_edge(left_id, right_id)
        for name in REQUIRED_EDGE_ATTRS:
            value = attrs[name]
            assert isinstance(value, (int, float))
            assert value > 0


def test_generators_return_vascular_graph_instances() -> None:
    healthy = generate_healthy_network(seed=7)
    fragile = generate_fragile_network(seed=7)

    assert isinstance(healthy, VascularGraph)
    assert isinstance(fragile, VascularGraph)
    assert len(healthy) > 0
    assert len(fragile) > 0


@pytest.mark.parametrize("seed", [0, 1, 42])
def test_generators_are_deterministic_with_fixed_seed(seed: int) -> None:
    healthy_a = generate_healthy_network(seed=seed)
    healthy_b = generate_healthy_network(seed=seed)
    fragile_a = generate_fragile_network(seed=seed)
    fragile_b = generate_fragile_network(seed=seed)

    assert _graph_signature(healthy_a) == _graph_signature(healthy_b)
    assert _graph_signature(fragile_a) == _graph_signature(fragile_b)


def test_healthy_graph_has_more_cycles_than_fragile() -> None:
    healthy = generate_healthy_network(seed=42)
    fragile = generate_fragile_network(seed=42)

    assert _cycle_count(healthy) > _cycle_count(fragile)
    assert _cycle_count(fragile) == 0


def test_healthy_graph_has_higher_connectivity_than_fragile() -> None:
    healthy = generate_healthy_network(seed=42)
    fragile = generate_fragile_network(seed=42)

    healthy_nx = healthy.to_networkx()
    fragile_nx = fragile.to_networkx()

    assert healthy_nx.number_of_edges() > fragile_nx.number_of_edges()
    assert _average_degree(healthy) > _average_degree(fragile)


def test_all_edges_have_valid_required_attributes() -> None:
    _assert_valid_edge_attributes(generate_healthy_network(seed=11))
    _assert_valid_edge_attributes(generate_fragile_network(seed=11))


def test_different_seeds_can_produce_different_graphs() -> None:
    healthy_a = generate_healthy_network(seed=1)
    healthy_b = generate_healthy_network(seed=2)

    assert _graph_signature(healthy_a) != _graph_signature(healthy_b)
