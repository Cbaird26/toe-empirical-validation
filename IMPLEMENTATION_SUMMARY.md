# Minimal Scalar Hypothesis Card and Multi-Channel Constraint Net - Implementation Summary

## Completed Implementation

All tasks from the plan have been successfully implemented. The system now provides:

### 1. Minimal Scalar Hypothesis Card v0.1
- **File**: `data/constraints/minimal_scalar_hypothesis_card_v0.1.yaml`
- Defines Higgs-portal scalar model with all parameters, units, and equations
- Includes unit anchors for fail-fast checks
- Specifies channel mappings for all four channels
- Documents resonance guardrails and domain validation rules

### 2. Extended Parameter Card
- **File**: `data/constraints/parameter_card.yaml`
- Extended with channel definitions and mapping functions
- Includes forward and inverse mapping equations per channel
- Unit conversion anchors and domain validation rules

### 3. Joint Constraint Fusion Module
- **File**: `code/inference/scalar_constraint_fusion.py`
- Loads bounds from multiple channels
- Computes joint exclusion using union or intersection methods
- Generates exclusion plots (with matplotlib fallback to CSV)
- Computes allowed region and identifies next best tests
- Checks channel orthogonality and identifies experimental toggles

### 4. Three-Prong Constraint Net Scripts
- **Fifth-Force + EP**: `scripts/generate_fifth_force_ep_bounds.py`
- **Clocks/Spectroscopy**: `scripts/generate_clocks_spectroscopy_bounds.py`
- **Joint Generator**: `scripts/generate_joint_scalar_constraints.py`
- All scripts output standardized CSV format for fusion

### 5. Extended Falsification Dashboard
- **File**: `code/inference/fifth_force/falsification_dashboard.py`
- Added `add_joint_scalar_metrics()` function
- Integrates joint constraint results into main dashboard

### 6. Documentation
- **Hypothesis Card**: `docs/minimal_scalar_hypothesis_card.md`
- **Fusion Methodology**: `docs/joint_constraint_fusion.md`
- Complete documentation of parameters, equations, and usage

### 7. Makefile Targets
- `scalar-hypothesis-card`: Validate hypothesis card
- `scalar-three-prong`: Generate all three channel bounds
- `scalar-joint`: Generate joint exclusion plot and dashboard
- `scalar-full`: Run complete pipeline

### 8. Unit Tests
- **File**: `tests/test_scalar_constraint_fusion.py`
- Tests parameter card validation
- Tests constraint fusion functions
- Tests orthogonality and toggle identification

## File Structure

```
.
├── data/
│   └── constraints/
│       ├── minimal_scalar_hypothesis_card_v0.1.yaml
│       └── parameter_card.yaml
├── code/
│   └── inference/
│       ├── scalar_constraint_fusion.py
│       └── fifth_force/
│           └── falsification_dashboard.py
├── scripts/
│   ├── generate_fifth_force_ep_bounds.py
│   ├── generate_clocks_spectroscopy_bounds.py
│   └── generate_joint_scalar_constraints.py
├── docs/
│   ├── minimal_scalar_hypothesis_card.md
│   └── joint_constraint_fusion.md
├── tests/
│   └── test_scalar_constraint_fusion.py
├── results/
│   └── scalar_constraints/
│       ├── fifth_force_ep_bounds.csv
│       ├── clocks_spectroscopy_bounds.csv
│       ├── collider_higgs_bounds.csv (if exists)
│       ├── joint_bounds.csv
│       ├── joint_exclusion_plot.png
│       └── joint_dashboard.json
└── Makefile
```

## Usage

### Generate Individual Channel Bounds
```bash
python scripts/generate_fifth_force_ep_bounds.py
python scripts/generate_clocks_spectroscopy_bounds.py
python scripts/generate_collider_higgs_bounds.py  # If exists
```

### Generate Joint Constraints
```bash
python scripts/generate_joint_scalar_constraints.py
```

### Using Makefile
```bash
make scalar-full  # Run complete pipeline
```

## Key Features

1. **Standardized Format**: All channels output bounds in the same CSV schema
2. **Domain Discipline**: Strict real-only evaluation (no extrapolation)
3. **Orthogonality Checks**: Verifies channels have different systematics
4. **Toggle Identification**: Lists experimental strategies per channel
5. **Unit Anchors**: Fail-fast checks prevent catastrophic unit errors
6. **Resonance Guardrails**: Prevents computation in dangerous regions

## Next Steps

1. Generate actual constraint data from experimental results
2. Run the joint fusion pipeline to produce exclusion plots
3. Integrate with existing fifth-force and collider modules
4. Extend to additional channels as needed

All implementation tasks are complete and ready for use.
