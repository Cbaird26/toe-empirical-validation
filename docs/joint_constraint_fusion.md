# Joint Constraint Fusion

## Overview

Joint constraint fusion combines bounds from multiple experimental channels to produce a unified exclusion plot and identify the allowed parameter region for the scalar field model.

## Methodology

### Fusion Methods

**Union Method** (Default, Most Conservative):
- A parameter point is excluded if **ANY** channel excludes it
- Takes the minimum allowed values across channels
- Most conservative approach, appropriate for initial analysis

**Intersection Method** (Optional):
- A parameter point is excluded only if **ALL** channels exclude it
- Takes the maximum allowed values across channels
- Less conservative, requires all channels to agree

### Standardized Input Format

All channels must produce bounds in the same CSV format:

```csv
m_c_GeV, lambda_m, theta_max, kappa_vc_max_GeV, domain_min, domain_max, channel_name
```

This standardization enables automatic fusion across different experimental channels.

## Channel Orthogonality

### Why Orthogonality Matters

Different experimental channels have different systematics. Orthogonal channels provide independent constraints that cannot be explained by a single systematic error.

### Orthogonality Metrics

The fusion module computes correlation coefficients between channels:
- **Low correlation** (< 0.5): Channels are orthogonal (good)
- **High correlation** (> 0.5): Channels may share systematics (warning)

### Three-Prong Net

The recommended three-prong constraint net provides orthogonal coverage:

1. **Fifth-Force/EP**: Tabletop gravity tests (micrometer to meter scales)
2. **Collider Higgs**: High-energy particle physics (GeV to TeV scales)
3. **Atomic Clocks**: Precision frequency measurements (ultralight scalars)

These channels have:
- Different experimental platforms
- Different systematics
- Different sensitivity ranges
- Different physical mechanisms

## Experimental Toggles

Each channel includes experimental "toggles" that break degeneracies and identify systematics:

### Fifth-Force Toggles
- Material swap (different composition)
- Geometry reversal
- Separation modulation at multiple frequencies
- Pressure/temperature changes
- Patch potential characterization

### Equivalence Principle Toggles
- Multiple material pairs (different nuclear sensitivities)
- Seasonal/orbital modulation
- Independent platform cross-check (torsion vs atom interferometer)

### Collider Toggles
- Consistency across production modes
- Consistency across decay channels
- Multi-observable agreement (signal strength + BR + width)

### Atomic Clock Toggles
- Multi-species comparison (different sensitivity coefficients)
- Multi-site correlation (cross-lab)
- Phase consistency
- Consistent scaling across transitions

## Output Products

### Joint Exclusion Plot
- 2D plot: m_c vs |κ_cH v_c|
- Shows exclusion regions from all channels
- Highlights allowed parameter space

### Joint Bounds CSV
- Standardized format with combined constraints
- Ready for further analysis or plotting

### Dashboard JSON
Contains:
- **Allowed Region**: Boundaries and statistics
- **Next Test Recommendations**: Ranked by sensitivity
- **Orthogonality Analysis**: Correlation matrix
- **Channel Coverage**: Number of points per channel
- **Experimental Toggles**: Available strategies per channel

## Interpretation

### Allowed Region
Points below the exclusion boundary are allowed. The allowed region represents parameter space where the scalar model is not yet ruled out.

### Next Test Recommendations
Channels are ranked by sensitivity in the allowed region. Higher sensitivity means tighter bounds, indicating where new experiments would be most effective.

### Coverage Fraction
The fraction of parameter space covered by experimental constraints. Higher coverage means more complete testing.

## Usage

```bash
# Generate individual channel bounds
python scripts/generate_fifth_force_ep_bounds.py
python scripts/generate_clocks_spectroscopy_bounds.py
python scripts/generate_collider_higgs_bounds.py

# Generate joint constraints
python scripts/generate_joint_scalar_constraints.py
```

Results are saved in `results/scalar_constraints/`:
- `joint_bounds.csv`: Combined bounds
- `joint_exclusion_plot.png`: Visualization
- `joint_dashboard.json`: Complete metrics

## Limitations

1. **Domain Discipline**: Only evaluates on experimental support (no extrapolation)
2. **Conservative Union**: Uses most conservative combination method
3. **Simplified Models**: Assumes simple Yukawa mediator (no screening)
4. **Grid Resolution**: Limited by input channel resolution

## Future Enhancements

- Likelihood-based fusion (beyond union/intersection)
- Bayesian parameter estimation
- Systematic uncertainty propagation
- Multi-dimensional parameter space exploration
