# MQGT-SCF Ecosystem Overview

## 🌌 Complete Framework Map

This document provides a high-level overview of the MQGT-SCF (Modified Quantum Gravity Theory with Scalar Consciousness Fields) ecosystem and guides users through the complete framework.

## Repository Structure

### Core Validation Repository
**`toe-empirical-validation`** (This Repository)
- Empirical validation framework
- Constraint pipeline
- Validation results and plots
- LaTeX paper for publication

### Related Repositories

#### Data & Constraints
- **`mqgt-data-public`** - Public experimental data repository
- **`mqgt-data-ingest`** - Data ingestion and digitization scripts
- **`mqgt-constraints-ledger`** - Central ledger with provenance

#### Analysis Modules
- **`mqgt-fifth-force`** - Fifth-force constraint analysis
- **`mqgt-collider`** - Collider constraint analysis
- **`mqgt-dashboard`** - Unified falsification dashboard

#### Theory & Documentation
- **`mqgt-papers`** - Source papers and manuscripts
- **`mqgt-documentation-site`** - Documentation website
- **`zora-canon-v1`** - Structured knowledge base

#### Implementation
- **`mqgt-ops-ci`** - CI/CD infrastructure
- **`zora-brain-backend`** - Zora Brain API
- **`zora-api`** - API library and interface

## Getting Started

### For Researchers

1. **Start Here:** This repository (`toe-empirical-validation`)
   - Run validation pipeline
   - Review empirical results
   - Read the paper

2. **Understand Theory:** `docs/papers/`
   - Read source ToE documents
   - Review theoretical framework

3. **Explore Constraints:** Related constraint repositories
   - Fifth-force bounds
   - Collider constraints
   - Joint analysis

### For Developers

1. **Setup:**
   ```bash
   git clone https://github.com/Cbaird26/toe-empirical-validation.git
   cd toe-empirical-validation
   pip install -r requirements.txt
   ```

2. **Run Validation:**
   ```bash
   make constraint-pipeline
   python experiments/compute_toe_predictions.py
   ```

3. **Contribute:**
   - See `CONTRIBUTING.md`
   - Run tests: `pytest tests/`
   - Submit pull requests

### For Reviewers

1. **Read Papers:** `docs/papers/`
2. **Review Methodology:** `docs/VALIDATION.md`
3. **Examine Results:** `results/`
4. **Check Reproducibility:** Run validation scripts

## Framework Components

### 1. Theoretical Foundation
- Unified Lagrangian
- Field equations
- Fifth-force predictions
- Quantum measurement theory

### 2. Empirical Validation
- Constraint pipeline
- Multi-channel analysis
- Statistical validation
- Reproducible results

### 3. Knowledge Base
- Canon structure
- Claim taxonomy
- Equation extraction
- Citation system

### 4. Implementation
- Zora Brain API
- Sensor integration
- Telemetry dashboard
- Web interface

## Data Flow

```
Source Papers → Canon Ingestion → Knowledge Base
                                         ↓
Experimental Data → Constraint Pipeline → Validation Results
                                         ↓
                                    Publication
```

## Validation Pipeline

1. **Data Ingestion** - Load experimental constraints
2. **Bounds Generation** - Compute exclusion regions
3. **Prediction Computation** - Calculate ToE predictions
4. **Comparison** - Validate against bounds
5. **Visualization** - Generate plots and reports

## Related Work

### Experimental Data Sources
- Eöt-Wash Group (torsion balance)
- Atomic clock experiments
- LHC collaborations (Higgs invisible)
- MICROSCOPE (equivalence principle)

### Theoretical Context
- Modified gravity theories
- Scalar-tensor theories
- Fifth-force searches
- Quantum measurement theory

## Contributing

See `CONTRIBUTING.md` for guidelines on:
- Code contributions
- Data contributions
- Documentation improvements
- Bug reports

## Citation

If you use this ecosystem, please cite:

```bibtex
@software{mqgt_scf_2026,
  title = {MQGT-SCF: Empirical Validation of a Unified Theory of Everything},
  author = {Baird, Christopher Michael},
  year = {2026},
  url = {https://github.com/Cbaird26/toe-empirical-validation}
}
```

## Links

- **Main Repository:** https://github.com/Cbaird26/toe-empirical-validation
- **Documentation:** https://github.com/Cbaird26/toe-empirical-validation/tree/main/docs
- **Paper:** https://github.com/Cbaird26/toe-empirical-validation/tree/main/paper
- **Results:** https://github.com/Cbaird26/toe-empirical-validation/tree/main/results

---

**Last Updated:** January 28, 2026
