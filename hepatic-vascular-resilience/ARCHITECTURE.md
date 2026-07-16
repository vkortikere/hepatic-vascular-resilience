# ARCHITECTURE.md

# Hepatic Vascular Twin
Computational Software Architecture for the Hepatic Vascular Resilience Digital Twin (HVR-DT)

## 1. Project Purpose

This repository implements a reproducible research codebase for modeling hepatic vascular resilience from imaging, graph theory, topology, and perturbation analysis. The long-term goal is to estimate a Hepatic Vascular Resilience Index (HVRI) from vascular structure, topology, and flow-related features, with a build order that starts from synthetic validation before moving to real CT-derived data [file:21].

The software must support publication-quality experiments, modular development, unit testing, and reproducible figures. The project is not a single script; it is a staged scientific computing system with explicit inputs, outputs, and validation at every phase [file:21].

## 2. Design Principles

The architecture follows five principles.

- **Reproducibility first.** Every result must be regenerable from code, configuration, and versioned data.
- **Synthetic before clinical.** Validate mathematics and software behavior on synthetic vascular networks before using CT data.
- **Modularity.** Each scientific stage is isolated into its own module with a clear interface.
- **Testability.** Every core module must have unit tests.
- **Publication readiness.** The codebase must generate figures, reports, and notebook demonstrations suitable for a paper or presentation.

## 3. High-Level Pipeline

The full conceptual pipeline is:

```text
Input
  ├── Synthetic vascular network
  └── CT scan data
        ↓
Preprocessing
        ↓
Segmentation
        ↓
3D reconstruction
        ↓
Centerline extraction
        ↓
Weighted vascular graph
        ↓
Graph metrics + spectral analysis
        ↓
Topological analysis
        ↓
Hemodynamic approximation
        ↓
Perturbation / resilience simulation
        ↓
HVRI computation
        ↓
Visualization, validation, reports, and prediction
```

For Phase 1, only the synthetic branch is required. The CT, segmentation, reconstruction, and CFD layers are later extensions that should not block the initial prototype [file:21].

## 4. Repository Layout

The repository should use a `src/` layout to support packaging, imports, and testing.

```text
hepatic_vascular_twin/
├── README.md
├── pyproject.toml
├── .gitignore
├── docs/
│   ├── ARCHITECTURE.md
│   ├── METHODS_PRIORITY1.md
│   ├── PRIORITY1_REPORT.md
│   └── CHANGELOG.md
├── data/
│   ├── raw_ct/
│   ├── segmentation/
│   └── processed/
├── results/
│   ├── figures/
│   ├── tables/
│   └── logs/
├── notebooks/
│   ├── 01_priority1_demo.ipynb
│   ├── 02_reconstruction_demo.ipynb
│   └── 03_hvri_analysis.ipynb
├── tests/
│   ├── test_graph.py
│   ├── test_topology.py
│   ├── test_resilience.py
│   └── test_synthetic_networks.py
└── src/
    └── hepatic_vascular_twin/
        ├── __init__.py
        ├── preprocessing/
        │   ├── __init__.py
        │   ├── ct_loader.py
        │   ├── segmentation.py
        │   └── preprocessing_utils.py
        ├── reconstruction/
        │   ├── __init__.py
        │   ├── vessel_surface.py
        │   ├── centerline.py
        │   └── mesh_processing.py
        ├── graph/
        │   ├── __init__.py
        │   ├── vascular_graph.py
        │   ├── synthetic_networks.py
        │   ├── graph_metrics.py
        │   └── spectral_analysis.py
        ├── topology/
        │   ├── __init__.py
        │   ├── filtration.py
        │   ├── persistence.py
        │   └── topological_features.py
        ├── hemodynamics/
        │   ├── __init__.py
        │   ├── resistance.py
        │   ├── flow_solver.py
        │   └── cfd_interface.py
        ├── resilience/
        │   ├── __init__.py
        │   ├── perturbation.py
        │   └── hvri.py
        ├── visualization/
        │   ├── __init__.py
        │   ├── plots.py
        │   └── dashboard.py
        └── experiments/
            ├── __init__.py
            ├── synthetic_tests.py
            └── validation.py
```

## 5. Module Responsibilities

### 5.1 preprocessing

This package handles CT input and image-level preprocessing. It is only used after the synthetic prototype is complete.

- `ct_loader.py`: reads CT volumes and metadata.
- `segmentation.py`: performs or wraps vessel segmentation.
- `preprocessing_utils.py`: utility functions such as normalization, cropping, resampling, and masking.

**Inputs:** CT volumes, masks, imaging metadata.  
**Outputs:** standardized image volumes, masks, and intermediate processed arrays.

### 5.2 reconstruction

This package converts segmented image data into geometric vessel representations.

- `vessel_surface.py`: builds surface models from segmentation.
- `centerline.py`: extracts centerlines from surfaces or segmentation.
- `mesh_processing.py`: cleans and simplifies meshes, repairs topology, and prepares geometry for graph construction.

**Inputs:** segmentation masks, surfaces, meshes.  
**Outputs:** vessel surfaces, centerlines, cleaned mesh objects, geometric descriptors.

### 5.3 graph

This package contains the core network model.

- `vascular_graph.py`: defines the weighted vascular graph object and associated schema.
- `synthetic_networks.py`: generates healthy and fragile synthetic vascular trees for validation.
- `graph_metrics.py`: computes degree, centrality, clustering, bridges, and path-based metrics.
- `spectral_analysis.py`: computes adjacency, Laplacian, eigenvalues, algebraic connectivity, and spectral gap.

**Inputs:** centerlines, branch data, synthetic edge lists.  
**Outputs:** NetworkX graphs or equivalent graph objects, graph metrics, and spectral summaries.

### 5.4 topology

This package extracts topological structure from the vascular graph or its geometric filtration.

- `filtration.py`: defines filtration strategy from edge length, radius, flow, or geometry.
- `persistence.py`: computes persistence diagrams, barcodes, and persistence summaries.
- `topological_features.py`: converts persistence output into scalar features such as lifetime, total persistence, entropy, and Betti summaries.

**Inputs:** graph object, edge weights, filtrations.  
**Outputs:** persistence diagrams, barcodes, and topological feature vectors.

### 5.5 hemodynamics

This package estimates flow and resistance.

- `resistance.py`: computes edge resistance using reduced-physics approximations.
- `flow_solver.py`: solves simplified flow propagation through the vascular graph.
- `cfd_interface.py`: reserved wrapper for later CFD integration.

**Inputs:** graph geometry, vessel length, radius, pressure boundary conditions.  
**Outputs:** edge resistance, estimated flow, pressure/flow fields, CFD hooks.

### 5.6 resilience

This package defines the resilience score and perturbation experiments.

- `perturbation.py`: removes vessels or modifies edge properties and recomputes downstream metrics.
- `hvri.py`: combines spectral, topological, and flow-related features into a composite HVRI score.

**Inputs:** graph, topology features, flow estimates, perturbation settings.  
**Outputs:** damage curves, resilience curves, HVRI scores, feature importance summaries.

### 5.7 visualization

This package handles all figure generation and dashboard-style outputs.

- `plots.py`: publication-quality static plots.
- `dashboard.py`: interactive or semi-interactive visualization tools.

**Inputs:** metrics, diagrams, scores, graphs, tables.  
**Outputs:** PNG/PDF figures, interactive views, figure-ready exports.

### 5.8 experiments

This package orchestrates experiments and validation.

- `synthetic_tests.py`: end-to-end synthetic validation experiments.
- `validation.py`: statistical comparisons, ablation studies, and downstream validation.

**Inputs:** module outputs and labeled conditions.  
**Outputs:** experiment tables, validation summaries, saved figures, and reproducible logs.

## 6. Implementation Priorities

The project must be built in phases.

### Priority 1: Required prototype

This is the first publishable software milestone and should be completed before any CT or CFD work.

Deliverables:
- Synthetic vascular graph generator.
- Weighted vascular graph class.
- Graph metrics.
- Spectral analysis.
- Topological features.
- Perturbation simulation.
- Initial HVRI implementation.
- Unit tests.
- Demo notebook.
- Figures for healthy vs fragile comparisons.

Scientific goal:
Validate that the mathematical framework can distinguish robust and fragile synthetic networks.

### Priority 2: Real vascular reconstruction

Deliverables:
- CT loading.
- Segmentation wrapper.
- Surface extraction.
- Centerline extraction.
- Graph generation from anatomical geometry.

Scientific goal:
Convert image-derived vessel anatomy into a graph that matches the synthetic data interface.

### Priority 3: Hemodynamic modeling

Deliverables:
- Resistance estimation.
- Simplified flow solver.
- Optional CFD interface.

Scientific goal:
Attach reduced flow physics to the vascular graph without requiring full CFD for the first prototype.

### Priority 4: Clinical prediction

Deliverables:
- Patient-level feature table.
- Outcome labels.
- Statistical models.
- Predictive evaluation.

Scientific goal:
Test whether HVRI and related features correlate with clinical outcomes.

## 7. Data Flow Between Modules

The core data flow should be explicit and consistent.

1. `synthetic_networks.py` generates test graphs or vessel trees.
2. `vascular_graph.py` converts raw vessel descriptions into a weighted graph object.
3. `graph_metrics.py` and `spectral_analysis.py` compute network summaries.
4. `filtration.py` defines a filtration on the same graph or vessel geometry.
5. `persistence.py` computes persistence output from the filtration.
6. `topological_features.py` summarizes topological information into scalars.
7. `resistance.py` and `flow_solver.py` estimate hemodynamic quantities.
8. `perturbation.py` simulates vessel loss or damage.
9. `hvri.py` integrates all feature families into one resilience index.
10. `plots.py`, notebooks, and `synthetic_tests.py` generate figures and reproducible demonstrations.

## 8. Inputs and Outputs

### 8.1 Graph layer
**Inputs:** node positions, edge list, radius, length, flow, weight, branch identifiers.  
**Outputs:** graph object, adjacency matrix, Laplacian, graph metadata.

### 8.2 Topology layer
**Inputs:** weighted graph, radii, flow values, or geometric thresholds.  
**Outputs:** persistence diagrams, barcodes, Betti summaries, entropy, total persistence.

### 8.3 Hemodynamics layer
**Inputs:** edge geometry, viscosity, pressure assumptions, graph connectivity.  
**Outputs:** resistance values, flow estimates, pressure drops, branch-level hemodynamic weights.

### 8.4 Resilience layer
**Inputs:** graph, topology features, flow fields, perturbation parameters.  
**Outputs:** perturbed graphs, loss curves, damage scores, HVRI.

### 8.5 Visualization layer
**Inputs:** all numeric outputs from prior modules.  
**Outputs:** figures, saved tables, and notebook-ready visualizations.

## 9. Required Python Libraries

### Core scientific stack
- `numpy`
- `scipy`
- `pandas`
- `networkx`

### Visualization
- `matplotlib`
- `seaborn`
- `plotly`

### Topology
- `gudhi`
- `ripser`
- `scikit-tda`

### Imaging and geometry
- `nibabel`
- `SimpleITK`
- `vtk`
- `vmtk` if available

### Machine learning and statistics
- `scikit-learn`
- `statsmodels`

### Reproducibility and development
- `pytest`
- `jupyter`
- `black`
- `ruff`
- `mypy`
- `tqdm`

## 10. Open-Source Tools vs Custom Code

### Can use existing open-source tools
- Image loading and basic preprocessing: `SimpleITK`, `nibabel`.
- Segmentation utilities: `SimpleITK`, `scikit-image` if needed.
- Graph representation and standard metrics: `networkx`.
- Persistent homology: `gudhi` or `ripser`.
- Surface and centerline workflows: `vtk`, `vmtk`.
- Plotting and notebook visualization: `matplotlib`, `seaborn`, `plotly`.
- Statistical modeling: `scikit-learn`, `statsmodels`.

### Must be custom code
- The project-specific vascular graph schema.
- Synthetic healthy and fragile generators.
- The filtration rules used for vascular topology.
- The HVRI formula and feature fusion strategy.
- The perturbation protocol and resilience scoring.
- The experiment orchestration and validation logic.
- The publication-specific plots and report generation.

## 11. Reproducibility Requirements

Every experiment should be runnable from a fixed configuration and seed. The codebase should store:
- parameter files,
- random seeds,
- versioned figures,
- saved result tables,
- notebook outputs,
- and milestone reports.

All figures should be written to `results/figures/`. All tables should be written to `results/tables/`. All major development milestones should generate a markdown report in `docs/`.

## 12. Testing Strategy

Each priority 1 module must have tests.

Recommended tests:
- Graph construction preserves node and edge attributes.
- Synthetic healthy graphs have higher connectivity than fragile graphs.
- Spectral analysis returns valid Laplacian eigenvalues.
- Topological features are deterministic under fixed seeds.
- Perturbation decreases resilience measures in expected cases.
- HVRI is stable under repeated runs with the same configuration.

The first research milestone should aim for a small but meaningful test suite rather than broad coverage of unfinished modules.

## 13. Visualization Outputs

The first milestone should generate at least these deliverables:
- `healthy_vs_fragile_network.png`
- `spectral_comparison.png`
- `persistence_diagram.png`
- `hvri_comparison.png`

Later milestones may add:
- vessel reconstruction figures,
- centerline overlays,
- perturbation curves,
- flow maps,
- and patient-level dashboards.

## 14. Milestone Documentation

The repository should include project memory documents for future reference.

### `METHODS_PRIORITY1.md`
This should describe:
- synthetic network generation,
- graph definitions,
- topological computations,
- resilience scoring,
- validation protocol,
- and assumptions.

### `PRIORITY1_REPORT.md`
This should summarize:
- purpose,
- architecture,
- implemented modules,
- validation performed,
- figures created,
- limitations,
- and next steps.

### `CHANGELOG.md`
This should track versioned milestones and feature completion.

## 15. Implementation Guidance for Cursor

When using Cursor, do not request the whole system at once. Build one module per step.

Recommended order:
1. `src/hepatic_vascular_twin/graph/vascular_graph.py`
2. `src/hepatic_vascular_twin/graph/synthetic_networks.py`
3. `src/hepatic_vascular_twin/graph/graph_metrics.py`
4. `src/hepatic_vascular_twin/graph/spectral_analysis.py`
5. `src/hepatic_vascular_twin/topology/filtration.py`
6. `src/hepatic_vascular_twin/topology/persistence.py`
7. `src/hepatic_vascular_twin/topology/topological_features.py`
8. `src/hepatic_vascular_twin/resilience/perturbation.py`
9. `src/hepatic_vascular_twin/resilience/hvri.py`
10. `src/hepatic_vascular_twin/experiments/synthetic_tests.py`
11. `notebooks/01_priority1_demo.ipynb`

Each module should include type hints, documentation, and tests.

## 16. Scope Control

Do not begin full CT reconstruction, CFD, or clinical prediction until Priority 1 is complete and validated. The synthetic prototype is not a placeholder; it is the foundation that proves the software and mathematics work before clinical complexity is introduced.

## 17. Definition of Done

Priority 1 is complete when the repository can:
- generate synthetic vascular networks,
- compute graph and spectral metrics,
- compute topological features,
- simulate perturbations,
- calculate HVRI,
- produce reproducible figures,
- and pass unit tests.

At that point, the codebase will be ready to accept real vascular reconstruction data as the next phase.
