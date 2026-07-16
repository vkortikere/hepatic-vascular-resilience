"""Scalar topological features from persistence output."""

from __future__ import annotations

from typing import Any


def extract_topological_features(persistence_result: dict[str, Any]) -> dict[str, float]:
    """Summarize persistence into scalars: lifetime, total persistence, entropy, Betti."""
    raise NotImplementedError("Priority 1 implementation pending.")
