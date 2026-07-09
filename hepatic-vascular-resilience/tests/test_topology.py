"""Tests for the topology module."""

import pytest

from hepatic_vascular_twin.topology.topological_features import extract_topological_features


@pytest.mark.skip(reason="Scaffold only — implementation pending")
def test_topological_features_deterministic() -> None:
    """Topological features are deterministic under fixed seeds."""
    features = extract_topological_features({})
    assert isinstance(features, dict)
