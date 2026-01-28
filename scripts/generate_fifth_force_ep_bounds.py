#!/usr/bin/env python3
"""
Generate combined fifth-force + EP bounds in standard format.
Combines constraints from fifth-force (Yukawa) and equivalence principle tests.
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


def load_fifth_force_bounds(bounds_file: str) -> list:
    """Load fifth-force bounds from existing CSV."""
    bounds = []
    if Path(bounds_file).exists():
        with open(bounds_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lambda_m = float(row.get('lambda_m', 0))
                theta_max = float(row.get('theta_max', 0))
                
                # Compute m_c from lambda
                m_c_GeV = HBAR_C_GEV_M / lambda_m if lambda_m > 0 else 0
                
                # Compute kappa_vc_max from theta_max
                m_h_sq = M_HIGGS_GEV ** 2
                m_c_sq = m_c_GeV ** 2
                kappa_vc_max = abs(theta_max * (m_h_sq - m_c_sq))
                
                bounds.append({
                    'm_c_GeV': m_c_GeV,
                    'lambda_m': lambda_m,
                    'theta_max': theta_max,
                    'kappa_vc_max_GeV': kappa_vc_max,
                    'domain_min': lambda_m,  # Approximate
                    'domain_max': lambda_m,
                    'channel_name': 'fifth_force'
                })
    return bounds


def compute_ep_bounds(m_c_values: list, eta_max: float = 1e-15) -> list:
    """
    Compute EP bounds from composition-dependent limits.
    
    Args:
        m_c_values: List of m_c values in GeV
        eta_max: Maximum allowed EP violation parameter (default: MICROSCOPE limit)
    
    Returns:
        List of EP bounds
    """
    bounds = []
    
    # EP violation: η = (ΔZ/A) × (θ_hc² / K_ToE) × f_nuclear
    # For simplicity, assume ΔZ/A ≈ 0.1 and f_nuclear ≈ 1
    delta_Z_over_A = 0.1
    f_nuclear = 1.0
    
    for m_c in m_c_values:
        if m_c <= 0:
            continue
        
        # Inverse mapping: θ_max from η_max
        m_h_sq = M_HIGGS_GEV ** 2
        m_c_sq = m_c ** 2
        
        # θ_max = sqrt(η_max × K_ToE / (ΔZ/A × f_nuclear))
        theta_max = math.sqrt(eta_max * K_ToE / (delta_Z_over_A * f_nuclear))
        
        # Compute kappa_vc_max
        kappa_vc_max = abs(theta_max * (m_h_sq - m_c_sq))
        
        # Compute lambda
        lambda_m = HBAR_C_GEV_M / m_c if m_c > 0 else 0
        
        bounds.append({
            'm_c_GeV': m_c,
            'lambda_m': lambda_m,
            'theta_max': theta_max,
            'kappa_vc_max_GeV': kappa_vc_max,
            'domain_min': 0,  # EP tests cover all ranges
            'domain_max': float('inf'),
            'channel_name': 'equivalence_principle'
        })
    
    return bounds


def combine_bounds(fifth_force_bounds: list, ep_bounds: list) -> list:
    """
    Combine fifth-force and EP bounds using union (most conservative).
    
    For each m_c, take the minimum allowed theta_max and kappa_vc_max.
    """
    # Create a combined set of m_c values
    m_c_set = set()
    for bound in fifth_force_bounds:
        m_c_set.add(bound['m_c_GeV'])
    for bound in ep_bounds:
        m_c_set.add(bound['m_c_GeV'])
    
    m_c_values = sorted(m_c_set)
    
    combined = []
    
    for m_c in m_c_values:
        # Find bounds from each channel at this m_c
        ff_bound = None
        ep_bound = None
        
        for bound in fifth_force_bounds:
            if abs(bound['m_c_GeV'] - m_c) < 1e-15:
                ff_bound = bound
                break
        
        for bound in ep_bounds:
            if abs(bound['m_c_GeV'] - m_c) < 1e-15:
                ep_bound = bound
                break
        
        # Take minimum (most conservative)
        if ff_bound and ep_bound:
            theta_max = min(ff_bound['theta_max'], ep_bound['theta_max'])
            kappa_vc_max = min(ff_bound['kappa_vc_max_GeV'], ep_bound['kappa_vc_max_GeV'])
            domain_min = min(ff_bound['domain_min'], ep_bound['domain_min'])
            domain_max = max(ff_bound['domain_max'], ep_bound['domain_max'])
        elif ff_bound:
            theta_max = ff_bound['theta_max']
            kappa_vc_max = ff_bound['kappa_vc_max_GeV']
            domain_min = ff_bound['domain_min']
            domain_max = ff_bound['domain_max']
        elif ep_bound:
            theta_max = ep_bound['theta_max']
            kappa_vc_max = ep_bound['kappa_vc_max_GeV']
            domain_min = ep_bound['domain_min']
            domain_max = ep_bound['domain_max']
        else:
            continue
        
        combined.append({
            'm_c_GeV': m_c,
            'lambda_m': HBAR_C_GEV_M / m_c if m_c > 0 else 0,
            'theta_max': theta_max,
            'kappa_vc_max_GeV': kappa_vc_max,
            'domain_min': domain_min,
            'domain_max': domain_max,
            'channel_name': 'fifth_force_ep'
        })
    
    return combined


def main():
    """Main function to generate combined bounds."""
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Try to load existing fifth-force bounds
    fifth_force_file = project_root / 'results' / 'toe_constraints' / 'theta_max_vs_lambda.csv'
    fifth_force_bounds = load_fifth_force_bounds(str(fifth_force_file))
    
    # Generate EP bounds for a range of m_c values
    # Use m_c values from fifth-force if available, otherwise generate grid
    if fifth_force_bounds:
        m_c_values = [b['m_c_GeV'] for b in fifth_force_bounds]
    else:
        # Generate grid: 1e-12 to 1e-3 GeV (meV to MeV scale)
        m_c_values = [10**(i/10.0) * 1e-12 for i in range(40)]
    
    ep_bounds = compute_ep_bounds(m_c_values, eta_max=1e-15)
    
    # Combine bounds
    combined_bounds = combine_bounds(fifth_force_bounds, ep_bounds)
    
    # Output directory
    output_dir = project_root / 'results' / 'scalar_constraints'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write output
    output_file = output_dir / 'fifth_force_ep_bounds.csv'
    with open(output_file, 'w') as f:
        fieldnames = ['m_c_GeV', 'lambda_m', 'theta_max', 'kappa_vc_max_GeV',
                     'domain_min', 'domain_max', 'channel_name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for bound in combined_bounds:
            writer.writerow(bound)
    
    print(f"Generated {len(combined_bounds)} combined fifth-force + EP bounds")
    print(f"Output: {output_file}")


if __name__ == '__main__':
    main()
