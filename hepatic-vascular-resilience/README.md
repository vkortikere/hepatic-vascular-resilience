# Hepatic Vascular Twin (HVR-DT)

Reproducible research codebase for modeling **hepatic vascular resilience** from imaging, graph theory, topology, and perturbation analysis. The long-term goal is a **Hepatic Vascular Resilience Index (HVRI)** built from vascular structure, topology, and flow-related features.

This repository follows a staged build order: **synthetic validation first**, then CT-derived reconstruction, hemodynamics, and clinical prediction.

## Priority 1 scope (current milestone)

Priority 1 validates the mathematical framework on **synthetic vascular networks** before any CT or CFD work:

- Synthetic vascular graph generator (healthy vs fragile)
- Weighted vascular graph class
- Graph metrics and spectral analysis
- Topological features (filtration, persistence)
- Perturbation simulation and initial HVRI
- Unit tests, demo notebook, and publication figures

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system design and [docs/METHODS_PRIORITY1.md](docs/METHODS_PRIORITY1.md) for Priority 1 methods (to be filled as modules are implemented).

## Repository layout

```text
src/hepatic_vascular_twin/   # installable Python package
tests/                       # unit tests
notebooks/                   # demo and analysis notebooks
results/figures/             # generated figures
docs/                        # methods and milestone reports
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Development

Run tests:

```bash
pytest
```

Open the Priority 1 demo notebook:

```bash
jupyter notebook notebooks/01_priority1_demo.ipynb
```

Figures should be written to `results/figures/`.

## License

MIT (see project metadata in `pyproject.toml`).
