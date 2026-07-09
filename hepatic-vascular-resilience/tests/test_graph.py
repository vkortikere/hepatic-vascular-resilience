"""Tests for the graph module."""

from __future__ import annotations

import math
from typing import Dict, Tuple, Union

import networkx as nx
import pytest

from hepatic_vascular_twin.graph.vascular_graph import (
    DuplicateEdgeError,
    DuplicateNodeError,
    EdgeNotFoundError,
    InvalidAttributeError,
    NodeNotFoundError,
    VascularGraph,
)


def _build_simple_graph() -> VascularGraph:
    graph = VascularGraph()
    graph.add_node(0, (0.0, 0.0, 0.0))
    graph.add_node(1, (1.0, 0.0, 0.0))
    graph.add_edge(
        0,
        1,
        weight=1.0,
        length=1.0,
        radius=0.5,
        resistance=0.2,
        flow=0.1,
    )
    return graph


def test_empty_graph_has_no_nodes_or_edges() -> None:
    graph = VascularGraph()
    assert len(graph) == 0
    assert graph.node_ids() == []
    assert graph.edge_pairs() == []


def test_add_node_stores_position() -> None:
    graph = VascularGraph()
    graph.add_node(0, (1.0, 2.0, 3.0), branch_id="root")

    node = graph.get_node(0)
    assert node["position"] == (1.0, 2.0, 3.0)
    assert node["branch_id"] == "root"


def test_duplicate_node_raises() -> None:
    graph = VascularGraph()
    graph.add_node(0, (0.0, 0.0, 0.0))

    with pytest.raises(DuplicateNodeError):
        graph.add_node(0, (1.0, 1.0, 1.0))


@pytest.mark.parametrize(
    "position",
    [
        (0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
        ("a", 0.0, 0.0),
        (math.inf, 0.0, 0.0),
        (math.nan, 0.0, 0.0),
    ],
)
def test_invalid_position_raises(
    position: Union[Tuple[float, ...], Tuple[str, float, float]],
) -> None:
    graph = VascularGraph()
    with pytest.raises(InvalidAttributeError):
        graph.add_node(0, position)  # type: ignore[arg-type]


def test_add_edge_with_attributes() -> None:
    graph = _build_simple_graph()
    edge = graph.get_edge(0, 1)

    assert edge["weight"] == 1.0
    assert edge["length"] == 1.0
    assert edge["radius"] == 0.5
    assert edge["resistance"] == 0.2
    assert edge["flow"] == 0.1


def test_add_edge_requires_existing_nodes() -> None:
    graph = VascularGraph()
    graph.add_node(0, (0.0, 0.0, 0.0))

    with pytest.raises(NodeNotFoundError):
        graph.add_edge(0, 1, length=1.0)


def test_duplicate_edge_raises() -> None:
    graph = _build_simple_graph()

    with pytest.raises(DuplicateEdgeError):
        graph.add_edge(0, 1, length=1.0)


def test_self_loop_raises() -> None:
    graph = VascularGraph()
    graph.add_node(0, (0.0, 0.0, 0.0))

    with pytest.raises(InvalidAttributeError):
        graph.add_edge(0, 0, length=1.0)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"length": 0.0}, "length"),
        ({"radius": -1.0}, "radius"),
        ({"resistance": 0.0}, "resistance"),
        ({"flow": -0.1}, "flow"),
        ({"weight": 0.0}, "weight"),
    ],
)
def test_invalid_edge_attributes_raise(kwargs: Dict[str, float], message: str) -> None:
    graph = VascularGraph()
    graph.add_node(0, (0.0, 0.0, 0.0))
    graph.add_node(1, (1.0, 0.0, 0.0))

    with pytest.raises(InvalidAttributeError, match=message):
        graph.add_edge(0, 1, **kwargs)


def test_has_required_edge_attributes() -> None:
    graph = _build_simple_graph()

    assert graph.has_required_edge_attributes("length", "radius")
    assert not graph.has_required_edge_attributes("length", "radius", "branch_id")


def test_missing_edge_attributes_reports_gaps() -> None:
    graph = VascularGraph()
    graph.add_node(0, (0.0, 0.0, 0.0))
    graph.add_node(1, (1.0, 0.0, 0.0))
    graph.add_edge(0, 1, length=1.0)

    missing = graph.missing_edge_attributes("length", "radius", "flow")
    assert missing == {(0, 1): ["radius", "flow"]}


def test_to_networkx_preserves_attributes() -> None:
    graph = _build_simple_graph()
    nx_graph = graph.to_networkx()

    assert isinstance(nx_graph, nx.Graph)
    assert nx_graph.number_of_nodes() == 2
    assert nx_graph.number_of_edges() == 1
    assert nx_graph.nodes[0]["x"] == 0.0
    assert nx_graph.nodes[1]["z"] == 0.0
    assert nx_graph.edges[0, 1]["weight"] == 1.0
    assert nx_graph.edges[0, 1]["resistance"] == 0.2


def test_from_edge_list_builds_graph() -> None:
    graph = VascularGraph.from_edge_list(
        [(0, 1), (1, 2)],
        node_positions={
            0: (0.0, 0.0, 0.0),
            1: (1.0, 0.0, 0.0),
            2: (2.0, 0.0, 0.0),
        },
        edge_attributes={
            (0, 1): {"length": 1.0, "radius": 0.5, "weight": 1.0},
            (1, 2): {"length": 1.2, "radius": 0.4},
        },
    )

    assert graph.node_ids() == [0, 1, 2]
    assert graph.edge_pairs() == [(0, 1), (1, 2)]
    assert graph.get_edge(1, 2)["radius"] == 0.4
    assert graph.has_required_edge_attributes("length", "radius")
    assert not graph.has_required_edge_attributes("weight")


def test_from_edge_list_requires_positions_for_all_endpoints() -> None:
    with pytest.raises(NodeNotFoundError, match="Missing positions"):
        VascularGraph.from_edge_list(
            [(0, 1)],
            node_positions={0: (0.0, 0.0, 0.0)},
        )


def test_get_edge_not_found_raises() -> None:
    graph = _build_simple_graph()

    with pytest.raises(EdgeNotFoundError):
        graph.get_edge(0, 2)


def test_undirected_edge_lookup_is_order_invariant() -> None:
    graph = _build_simple_graph()

    assert graph.has_edge(1, 0)
    assert graph.get_edge(1, 0)["length"] == 1.0
