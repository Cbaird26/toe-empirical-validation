# Minimal Scalar Hypothesis Card v0.1

## Overview

The Minimal Scalar Hypothesis Card defines a Higgs-portal scalar field model for empirical testing within the ToE constraint pipeline. This card serves as the "passport" for the scalar field, specifying all parameters, units, equations, and channel mappings required for falsification.

## Model Definition

**Model Type**: Higgs-portal scalar (Template A)

**Key Assumptions**:
- No screening (simple Yukawa mediator)
- Mediator only (not dark matter or dark energy)
- Coupling via H†H operator
- Negligible self-interactions (linear theory)

## Primary Parameters

### m_c (Scalar Field Mass)
- **Unit**: GeV
- **Range**: [1e-6, 1e3] (meV to TeV scale)
- **Description**: Sets the force range via λ = ħc/m_c

### θ_hc (Higgs-Scalar Mixing Angle)
- **Unit**: Dimensionless
- **Range**: [-1, 1]
- **Equation**: θ_hc ≈ -κ_cH v_c / (m_h² - m_c²)
- **Notes**: Small angle approximation valid for m_c << m_h

### |κ_cH v_c| (Effective Coupling Strength)
- **Unit**: GeV
- **Range**: [1e-15, 1e-3]
- **Equation**: |κ_cH v_c| = |θ_hc (m_h² - m_c²)|
- **Notes**: Derived from mixing angle and mass difference

## Derived Quantities

### λ (Force Range Parameter)
- **Unit**: meters
- **Equation**: λ = ħc / m_c
- **Conversion**: λ(m) = (1.973e-13 GeV·m) / m_c(GeV)
- **Notes**: Compton wavelength of the scalar mediator

## Unit Anchors (Fail-Fast Checks)

These anchors prevent catastrophic unit conversion errors:

1. **λ = 100 μm → m_c ≈ 2 meV**
   - λ = 1e-4 m
   - m_c = 1.973e-12 GeV = 1.973e-3 meV

2. **λ = 1 mm → m_c ≈ 0.2 meV**
   - λ = 1e-3 m
   - m_c = 1.973e-13 GeV = 1.973e-4 meV

3. **λ = 10 μm → m_c ≈ 20 meV**
   - λ = 1e-5 m
   - m_c = 1.973e-11 GeV = 1.973e-2 meV

## Resonance Guardrails

**Danger Zone**: |m_c² - m_h²| / m_h² < 0.01

When the scalar mass approaches the Higgs mass (m_h = 125 GeV), the mixing formulas break down. The pipeline raises a ValueError in this region, requiring exact treatment.

## Channel Mappings

### Fifth-Force Channel
- **Description**: Yukawa deviation from inverse-square gravity
- **Forward**: α(λ) = (θ_hc² / K_ToE) × (m_h² / (m_h² - m_c²))²
- **Inverse**: θ_max(λ) = sqrt(α_max(λ) × K_ToE) × |m_h² - m_c²| / m_h²
- **Input**: alpha_max vs lambda_m
- **Output**: theta_max vs lambda_m, kappa_vc_max vs m_c
- **Mandatory Datasets**: lee2020_fig5_canonical.csv, eotwash_2016_canonical.csv

### Equivalence Principle Channel
- **Description**: Composition-dependent acceleration differences
- **Forward**: η_EP = (ΔZ/A) × (θ_hc² / K_ToE) × coupling_coefficient
- **Inverse**: θ_max from η_max limit
- **Input**: eta_max (EP violation parameter)
- **Output**: theta_max vs m_c
- **Mandatory Datasets**: microscope_ep_limits.csv

### Collider Higgs Channel
- **Description**: Higgs invisible decay and signal strength modifications
- **Forward**: BR(H → invisible) = sin²(θ_hc) for m_c < m_h/2
- **Inverse**: θ_max = arcsin(sqrt(BR_max))
- **Input**: BR_invisible_max
- **Output**: theta_max vs m_c, kappa_vc_max vs m_c
- **Mandatory Datasets**: atlas_hinv_2023.csv, cms_hinv_2023.csv

### Atomic Clocks Channel
- **Description**: Frequency shifts from scalar-induced constant variations
- **Forward**: δν/ν = K_α × (θ_hc² / K_ToE) × scalar_amplitude
- **Inverse**: θ_max from frequency shift limits
- **Input**: delta_nu_nu_max
- **Output**: theta_max vs m_c
- **Mandatory Datasets**: nist_clock_limits.csv, ptb_clock_limits.csv

## Domain Validation Rules

**Rule**: Strict real-only evaluation

- **Enforcement**: Return NaN outside experimental support
- **Extrapolation**: Forbidden
- **Notes**: Each channel must specify domain_min and domain_max in output CSV

## Output Schema

All channels must produce bounds in standardized CSV format:

```
m_c_GeV, lambda_m, theta_max, kappa_vc_max_GeV, domain_min, domain_max, channel_name
```

This format enables joint constraint fusion across channels.

## Physical Constants

- M_PL_REDUCED_GEV: 2.435e18
- V_HIGGS_GEV: 246.0
- M_HIGGS_GEV: 125.0
- HBAR_C_GEV_M: 1.973e-13
- HBAR_C_EV_M: 1.973e-7
- K_ToE: 1.764e31 (normalization constant for fifth-force mapping)

## Usage

The hypothesis card is defined in `data/constraints/minimal_scalar_hypothesis_card_v0.1.yaml` and serves as the reference for all constraint calculations. All forward and inverse mappings must be consistent with the equations defined in this card.
