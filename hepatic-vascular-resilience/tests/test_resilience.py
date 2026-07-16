"""Tests for the resilience module."""

import pytest

from hepatic_vascular_twin.resilience.hvri import compute_hvri
from hepatic_vascular_twin.resilience.perturbation import run_perturbation_study
from hepatic_vascular_twin.graph.vascular_graph import VascularGraph


@pytest.mark.skip(reason="Scaffold only — implementation pending")
def test_perturbation_decreases_resilience() -> None:
    """Perturbation decreases resilience measures in expected cases."""
    graph = VascularGraph()
    result = run_perturbation_study(graph, seed=42)
    assert result is not None


@pytest.mark.skip(reason="Scaffold only — implementation pending")
def test_hvri_stable_under_fixed_seed() -> None:
    """HVRI is stable under repeated runs with the same configuration."""
    graph = VascularGraph()
    score_a = compute_hvri(graph)
    score_b = compute_hvri(graph)
    assert score_a == score_b
