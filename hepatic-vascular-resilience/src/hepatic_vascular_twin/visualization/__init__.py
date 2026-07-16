"""Publication-quality plots and dashboard-style visualization."""

from hepatic_vascular_twin.visualization.dashboard import create_dashboard
from hepatic_vascular_twin.visualization.plots import (
    plot_healthy_vs_fragile,
    plot_hvri_comparison,
    plot_persistence_diagram,
    plot_spectral_comparison,
)

__all__ = [
    "plot_healthy_vs_fragile",
    "plot_spectral_comparison",
    "plot_persistence_diagram",
    "plot_hvri_comparison",
    "create_dashboard",
]
