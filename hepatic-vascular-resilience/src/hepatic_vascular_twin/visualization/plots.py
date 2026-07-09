"""Static publication-quality figure generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def plot_healthy_vs_fragile(
    healthy: Any,
    fragile: Any,
    *,
    output_path: Path | None = None,
    **kwargs: Any,
) -> Any:
    """Render healthy vs fragile network comparison figure."""
    raise NotImplementedError("Priority 1 implementation pending.")


def plot_spectral_comparison(
    results: dict[str, Any],
    *,
    output_path: Path | None = None,
    **kwargs: Any,
) -> Any:
    """Render spectral metric comparison figure."""
    raise NotImplementedError("Priority 1 implementation pending.")


def plot_persistence_diagram(
    persistence_result: dict[str, Any],
    *,
    output_path: Path | None = None,
    **kwargs: Any,
) -> Any:
    """Render persistence diagram / barcode figure."""
    raise NotImplementedError("Priority 1 implementation pending.")


def plot_hvri_comparison(
    scores: dict[str, float],
    *,
    output_path: Path | None = None,
    **kwargs: Any,
) -> Any:
    """Render HVRI comparison figure."""
    raise NotImplementedError("Priority 1 implementation pending.")
