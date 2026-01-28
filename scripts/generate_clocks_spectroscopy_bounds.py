#!/usr/bin/env python3
"""
Generate clocks/spectroscopy bounds in standard format.
Maps scalar parameters to frequency shift predictions and compares with experimental limits.
"""

import sys
import os
import csv
import math
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Constants from parameter card
M_HIGGS_GEV = 125.0
K_ToE = 1.764e31
HBAR_C_GEV_M = 1.973e-13


def compute_clock_bounds(m_c_values: list, delta_nu_nu_max: float = 1e-18) -> list:
    """
    Compute atomic clock bounds from frequency shift limits.
    
    Args:
        m_c_values: List of m_c values in GeV
        delta_nu_nu_max: Maximum allowed fractional frequency shift (default: typical clock precision)
    
    Returns:
        List of clock bounds
    """
    bounds = []
    
    # Frequency shift: δν/ν = K_α × (θ_hc² / K_ToE) × scalar_amplitude
    # For ultralight scalars, amplitude depends on local density
    # Simplified: assume K_α ≈ 1 and amplitude ≈ 1 for coherent background
    K_alpha = 1.0
    scalar_amplitude = 1.0
    
    for m_c in m_c_values:
        if m_c <= 0:
            continue
        
        # Only apply to ultralight scalars (m_c < 1e-10 eV = 1e-19 GeV)
        if m_c > 1e-19:
            continue
        
        # Inverse mapping: θ_max from frequency shift limit
        # θ_max = sqrt((δν/ν)_max × K_ToE / (K_α × amplitude))
        theta_max = math.sqrt(delta_nu_nu_max * K_ToE / (K_alpha * scalar_amplitude))
        
        # Compute kappa_vc_max
        m_h_sq = M_HIGGS_GEV ** 2
        m_c_sq = m_c ** 2
        kappa_vc_max = abs(theta_max * (m_h_sq - m_c_sq))
        
        # Compute lambda
        lambda_m = HBAR_C_GEV_M / m_c if m_c > 0 else 0
        
        bounds.append({
            'm_c_GeV': m_c,
            'lambda_m': lambda_m,
            'theta_max': theta_max,
            'kappa_vc_max_GeV': kappa_vc_max,
            'domain_min': 0,  # Clock tests cover all ultralight ranges
            'domain_max': float('inf'),
            'channel_name': 'atomic_clocks'
        })
    
    return bounds


def main():
    """Main function to generate clock bounds."""
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Generate m_c grid for ultralight scalars
    # Range: 1e-23 to 1e-19 GeV (10^-23 to 10^-19 eV)
    m_c_values = [10**(i/10.0) * 1e-23 for i in range(40)]
    
    # Use typical atomic clock precision: 1e-18 fractional shift
    clock_bounds = compute_clock_bounds(m_c_values, delta_nu_nu_max=1e-18)
    
    # Output directory
    output_dir = project_root / 'results' / 'scalar_constraints'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write output
    output_file = output_dir / 'clocks_spectroscopy_bounds.csv'
    with open(output_file, 'w') as f:
        fieldnames = ['m_c_GeV', 'lambda_m', 'theta_max', 'kappa_vc_max_GeV',
                     'domain_min', 'domain_max', 'channel_name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for bound in clock_bounds:
            writer.writerow(bound)
    
    print(f"Generated {len(clock_bounds)} clock/spectroscopy bounds")
    print(f"Output: {output_file}")


if __name__ == '__main__':
    main()
