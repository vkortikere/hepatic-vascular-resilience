"""Project-specific weighted vascular graph schema and construction."""

from __future__ import annotations

import math
from typing import Any, Iterator, Tuple

import networkx as nx

NodeId = int
Position3D = Tuple[float, float, float]
EdgePair = Tuple[NodeId, NodeId]

EDGE_ATTR_KEYS = frozenset({"weight", "length", "radius", "resistance", "flow"})


class VascularGraphError(Exception):
    """Base exception for vascular graph operations."""


class DuplicateNodeError(VascularGraphError):
    """Raised when adding a node that already exists."""


class DuplicateEdgeError(VascularGraphError):
    """Raised when adding an edge that already exists."""


class NodeNotFoundError(VascularGraphError):
    """Raised when a referenced node does not exist."""


class EdgeNotFoundError(VascularGraphError):
    """Raised when a referenced edge does not exist."""


class InvalidAttributeError(VascularGraphError):
    """Raised when an attribute value fails validation."""


def _validate_position(position: Position3D) -> Position3D:
    """Validate and return a 3D position tuple."""
    if not isinstance(position, tuple) or len(position) != 3:
        raise InvalidAttributeError(
            f"position must be a 3-tuple (x, y, z); got {position!r}"
        )
    validated: list[float] = []
    for index, value in enumerate(position):
        if not isinstance(value, (int, float)):
            raise InvalidAttributeError(
                f"position[{index}] must be numeric; got {value!r}"
            )
        numeric = float(value)
        if not math.isfinite(numeric):
            raise InvalidAttributeError(
                f"position[{index}] must be finite; got {value!r}"
            )
        validated.append(numeric)
    return (validated[0], validated[1], validated[2])


def _validate_positive(value: float | None, name: str) -> None:
    """Require a numeric attribute to be strictly positive when provided."""
    if value is None:
        return
    if not isinstance(value, (int, float)):
        raise InvalidAttributeError(f"{name} must be numeric; got {value!r}")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0:
        raise InvalidAttributeError(f"{name} must be a positive finite number")


def _validate_non_negative(value: float | None, name: str) -> None:
    """Require a numeric attribute to be non-negative when provided."""
    if value is None:
        return
    if not isinstance(value, (int, float)):
        raise InvalidAttributeError(f"{name} must be numeric; got {value!r}")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0:
        raise InvalidAttributeError(f"{name} must be a non-negative finite number")


def _canonical_edge(u: NodeId, v: NodeId, *, directed: bool) -> EdgePair:
    """Return a stable edge key for internal storage."""
    if directed:
        return (u, v)
    return (u, v) if u <= v else (v, u)


class VascularGraph:
    """Container for a weighted hepatic vascular network.

    Nodes carry 3D positions. Edges carry vascular attributes such as length,
    radius, resistance, flow, and an optional scalar weight for downstream
    graph and spectral analysis.
    """

    def __init__(self, *, directed: bool = False) -> None:
        """Initialize an empty vascular graph."""
        self._directed = directed
        self._nodes: dict[NodeId, dict[str, Any]] = {}
        self._edges: dict[EdgePair, dict[str, Any]] = {}

    @property
    def directed(self) -> bool:
        """Whether the graph treats edges as directed."""
        return self._directed

    def add_node(
        self,
        node_id: NodeId,
        position: Position3D,
        **metadata: Any,
    ) -> None:
        """Add a node with a required 3D position and optional metadata.

        Args:
            node_id: Unique integer identifier for the node.
            position: ``(x, y, z)`` coordinates in 3D space.
            **metadata: Additional node-level attributes.

        Raises:
            DuplicateNodeError: If ``node_id`` already exists.
            InvalidAttributeError: If ``position`` is invalid.
        """
        if not isinstance(node_id, int):
            raise InvalidAttributeError(f"node_id must be int; got {type(node_id)!r}")
        if node_id in self._nodes:
            raise DuplicateNodeError(f"Node {node_id} already exists")

        validated_position = _validate_position(position)
        self._nodes[node_id] = {
            "position": validated_position,
            **metadata,
        }

    def add_edge(
        self,
        u: NodeId,
        v: NodeId,
        *,
        weight: float | None = None,
        length: float | None = None,
        radius: float | None = None,
        resistance: float | None = None,
        flow: float | None = None,
        **metadata: Any,
    ) -> None:
        """Add a weighted edge between two existing nodes.

        Args:
            u: Source or first endpoint node id.
            v: Target or second endpoint node id.
            weight: Edge weight used for graph analysis.
            length: Vessel segment length.
            radius: Vessel segment radius.
            resistance: Estimated hydraulic resistance.
            flow: Estimated flow magnitude.
            **metadata: Additional edge-level attributes.

        Raises:
            NodeNotFoundError: If either endpoint is missing.
            DuplicateEdgeError: If the edge already exists.
            InvalidAttributeError: If edge values fail validation.
        """
        if u == v:
            raise InvalidAttributeError("Self-loops are not allowed")
        if u not in self._nodes:
            raise NodeNotFoundError(f"Node {u} does not exist")
        if v not in self._nodes:
            raise NodeNotFoundError(f"Node {v} does not exist")

        _validate_positive(weight, "weight")
        _validate_positive(length, "length")
        _validate_positive(radius, "radius")
        _validate_positive(resistance, "resistance")
        _validate_non_negative(flow, "flow")

        edge_key = _canonical_edge(u, v, directed=self._directed)
        if edge_key in self._edges:
            raise DuplicateEdgeError(f"Edge {edge_key} already exists")

        self._edges[edge_key] = {
            "weight": float(weight) if weight is not None else None,
            "length": float(length) if length is not None else None,
            "radius": float(radius) if radius is not None else None,
            "resistance": float(resistance) if resistance is not None else None,
            "flow": float(flow) if flow is not None else None,
            "endpoints": (u, v),
            **metadata,
        }

    def has_node(self, node_id: NodeId) -> bool:
        """Return whether ``node_id`` exists in the graph."""
        return node_id in self._nodes

    def has_edge(self, u: NodeId, v: NodeId) -> bool:
        """Return whether an edge exists between ``u`` and ``v``."""
        return _canonical_edge(u, v, directed=self._directed) in self._edges

    def get_node(self, node_id: NodeId) -> dict[str, Any]:
        """Return a copy of node attributes including position.

        Raises:
            NodeNotFoundError: If the node does not exist.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(f"Node {node_id} does not exist")
        return dict(self._nodes[node_id])

    def get_edge(self, u: NodeId, v: NodeId) -> dict[str, Any]:
        """Return a copy of edge attributes.

        Raises:
            EdgeNotFoundError: If the edge does not exist.
        """
        edge_key = _canonical_edge(u, v, directed=self._directed)
        if edge_key not in self._edges:
            raise EdgeNotFoundError(f"Edge ({u}, {v}) does not exist")
        return dict(self._edges[edge_key])

    def node_ids(self) -> list[NodeId]:
        """Return all node ids in ascending order."""
        return sorted(self._nodes)

    def edge_pairs(self) -> list[EdgePair]:
        """Return stored edge endpoint pairs in insertion order."""
        return [
            attrs["endpoints"]
            for attrs in self._edges.values()
        ]

    def _attribute_present(self, attributes: dict[str, Any], name: str) -> bool:
        return name in attributes and attributes[name] is not None

    def has_required_node_attributes(self, *names: str) -> bool:
        """Return whether every node has all named attributes set."""
        if not names:
            return True
        return all(
            all(self._attribute_present(attrs, name) for name in names)
            for attrs in self._nodes.values()
        )

    def has_required_edge_attributes(self, *names: str) -> bool:
        """Return whether every edge has all named attributes set."""
        if not names:
            return True
        return all(
            all(self._attribute_present(attrs, name) for name in names)
            for attrs in self._edges.values()
        )

    def missing_edge_attributes(self, *names: str) -> dict[EdgePair, list[str]]:
        """Report missing edge attributes for each edge.

        Returns:
            Mapping from endpoint pair to the list of missing attribute names.
            Edges with all requested attributes are omitted.
        """
        missing: dict[EdgePair, list[str]] = {}
        for attrs in self._edges.values():
            absent = [name for name in names if not self._attribute_present(attrs, name)]
            if absent:
                missing[attrs["endpoints"]] = absent
        return missing

    def to_networkx(self) -> nx.Graph | nx.DiGraph:
        """Export the vascular graph as a NetworkX graph with attributes.

        Node attributes include ``x``, ``y``, ``z`` from the stored position
        plus any additional node metadata. Edge attributes include the vascular
        schema fields and any additional edge metadata.
        """
        graph: nx.Graph | nx.DiGraph
        if self._directed:
            graph = nx.DiGraph()
        else:
            graph = nx.Graph()

        for node_id, attrs in self._nodes.items():
            position = attrs["position"]
            node_attrs = {
                key: value
                for key, value in attrs.items()
                if key != "position"
            }
            node_attrs.update({"x": position[0], "y": position[1], "z": position[2]})
            graph.add_node(node_id, **node_attrs)

        for attrs in self._edges.values():
            u, v = attrs["endpoints"]
            edge_attrs = {
                key: value
                for key, value in attrs.items()
                if key != "endpoints"
            }
            graph.add_edge(u, v, **edge_attrs)

        return graph

    @classmethod
    def from_edge_list(
        cls,
        edge_list: list[EdgePair],
        *,
        node_positions: dict[NodeId, Position3D] | None = None,
        edge_attributes: dict[EdgePair, dict[str, Any]] | None = None,
        directed: bool = False,
    ) -> VascularGraph:
        """Build a vascular graph from an edge list and optional attribute maps.

        Args:
            edge_list: Sequence of endpoint pairs.
            node_positions: Mapping from node id to 3D position. Required for
                every node referenced by ``edge_list``.
            edge_attributes: Optional per-edge attribute dictionaries. Keys may
                use either endpoint order; undirected edges are normalized.
            directed: Whether to build a directed graph.

        Raises:
            NodeNotFoundError: If an edge references a node without a position.
            VascularGraphError: Subclass errors for duplicate or invalid data.
        """
        graph = cls(directed=directed)
        positions = node_positions or {}
        attributes = edge_attributes or {}

        referenced_nodes: set[NodeId] = set()
        for u, v in edge_list:
            referenced_nodes.add(u)
            referenced_nodes.add(v)

        missing_positions = sorted(node_id for node_id in referenced_nodes if node_id not in positions)
        if missing_positions:
            raise NodeNotFoundError(
                "Missing positions for nodes: "
                + ", ".join(str(node_id) for node_id in missing_positions)
            )

        for node_id in sorted(referenced_nodes):
            graph.add_node(node_id, positions[node_id])

        normalized_edge_attrs: dict[EdgePair, dict[str, Any]] = {}
        for (u, v), attrs in attributes.items():
            normalized_edge_attrs[_canonical_edge(u, v, directed=directed)] = dict(attrs)

        for u, v in edge_list:
            edge_key = _canonical_edge(u, v, directed=directed)
            attrs = normalized_edge_attrs.get(edge_key, {})
            known_attrs = {key: attrs[key] for key in EDGE_ATTR_KEYS if key in attrs}
            extra_attrs = {
                key: value for key, value in attrs.items() if key not in EDGE_ATTR_KEYS
            }
            graph.add_edge(u, v, **known_attrs, **extra_attrs)

        return graph

    def __len__(self) -> int:
        """Return the number of nodes."""
        return len(self._nodes)

    def __iter__(self) -> Iterator[NodeId]:
        """Iterate over node ids."""
        return iter(self.node_ids())

    def __repr__(self) -> str:
        return (
            f"VascularGraph(nodes={len(self._nodes)}, edges={len(self._edges)}, "
            f"directed={self._directed})"
        )
