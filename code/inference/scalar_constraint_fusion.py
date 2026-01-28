"""
Joint Constraint Fusion Module
Combines constraints from multiple channels to produce joint exclusion plots
"""

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def load_channel_bounds(csv_path: str) -> List[Dict]:
    """
    Load bounds from a channel CSV file.
    
    Expected CSV format:
    m_c_GeV, lambda_m, theta_max, kappa_vc_max_GeV, domain_min, domain_max, channel_name
    
    Returns list of dictionaries with bound data.
    """
    bounds = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bounds.append({
                'm_c_GeV': float(row['m_c_GeV']),
                'lambda_m': float(row.get('lambda_m', 0)),
                'theta_max': float(row['theta_max']),
                'kappa_vc_max_GeV': float(row['kappa_vc_max_GeV']),
                'domain_min': float(row.get('domain_min', 0)),
                'domain_max': float(row.get('domain_max', float('inf'))),
                'channel_name': row.get('channel_name', 'unknown')
            })
    return bounds


def load_all_channel_bounds(channel_files: Dict[str, str]) -> Dict[str, List[Dict]]:
    """
    Load bounds from all channel CSV files.
    
    Args:
        channel_files: Dict mapping channel names to CSV file paths
    
    Returns:
        Dict mapping channel names to lists of bound dictionaries
    """
    all_bounds = {}
    for channel_name, file_path in channel_files.items():
        if Path(file_path).exists():
            all_bounds[channel_name] = load_channel_bounds(file_path)
        else:
            print(f"Warning: Channel file not found: {file_path}")
            all_bounds[channel_name] = []
    return all_bounds


def compute_joint_exclusion(
    all_bounds: Dict[str, List[Dict]],
    method: str = 'union'
) -> List[Dict]:
    """
    Combine constraints from multiple channels.
    
    Args:
        all_bounds: Dict mapping channel names to bound lists
        method: 'union' (excluded if ANY channel excludes) or 'intersection' (excluded if ALL exclude)
    
    Returns:
        List of joint exclusion bounds
    """
    # Create a grid of m_c values from all channels
    m_c_values = set()
    for channel_bounds in all_bounds.values():
        for bound in channel_bounds:
            m_c_values.add(bound['m_c_GeV'])
    
    m_c_values = sorted(m_c_values)
    
    joint_bounds = []
    
    for m_c in m_c_values:
        # Get theta_max and kappa_vc_max from each channel at this m_c
        channel_limits = {}
        for channel_name, bounds in all_bounds.items():
            # Find closest bound to this m_c
            closest = None
            min_diff = float('inf')
            for bound in bounds:
                diff = abs(bound['m_c_GeV'] - m_c)
                if diff < min_diff:
                    min_diff = diff
                    closest = bound
            
            if closest and closest['m_c_GeV'] == m_c:
                channel_limits[channel_name] = {
                    'theta_max': closest['theta_max'],
                    'kappa_vc_max': closest['kappa_vc_max_GeV']
                }
        
        if not channel_limits:
            continue
        
        # Combine using union (most conservative) or intersection
        if method == 'union':
            # Excluded if ANY channel excludes (take minimum allowed values)
            theta_max = min([lim['theta_max'] for lim in channel_limits.values()])
            kappa_vc_max = min([lim['kappa_vc_max'] for lim in channel_limits.values()])
        else:  # intersection
            # Excluded if ALL channels exclude (take maximum allowed values)
            theta_max = max([lim['theta_max'] for lim in channel_limits.values()])
            kappa_vc_max = max([lim['kappa_vc_max'] for lim in channel_limits.values()])
        
        # Compute lambda from m_c
        hbar_c_gev_m = 1.973e-13
        lambda_m = hbar_c_gev_m / m_c if m_c > 0 else 0
        
        # Determine domain from all channels
        domain_mins = [b['domain_min'] for b in all_bounds.values() for b in b if b['m_c_GeV'] == m_c]
        domain_maxs = [b['domain_max'] for b in all_bounds.values() for b in b if b['m_c_GeV'] == m_c]
        
        domain_min = min(domain_mins) if domain_mins else 0
        domain_max = max(domain_maxs) if domain_maxs else float('inf')
        
        joint_bounds.append({
            'm_c_GeV': m_c,
            'lambda_m': lambda_m,
            'theta_max': theta_max,
            'kappa_vc_max_GeV': kappa_vc_max,
            'domain_min': domain_min,
            'domain_max': domain_max,
            'channel_name': 'joint'
        })
    
    return joint_bounds


def compute_allowed_region(joint_bounds: List[Dict]) -> Dict:
    """
    Find the surviving parameter space.
    
    Returns:
        Dict with allowed region boundaries and statistics
    """
    if not joint_bounds:
        return {
            'allowed_points': 0,
            'total_points': 0,
            'coverage_fraction': 0.0,
            'min_m_c': None,
            'max_m_c': None,
            'min_kappa_vc': None,
            'max_kappa_vc': None
        }
    
    # For now, all points in joint_bounds represent exclusion boundaries
    # Points below the boundary are allowed
    m_c_values = [b['m_c_GeV'] for b in joint_bounds]
    kappa_vc_values = [b['kappa_vc_max_GeV'] for b in joint_bounds]
    
    return {
        'allowed_points': len(joint_bounds),  # Points on boundary
        'total_points': len(joint_bounds),
        'coverage_fraction': 1.0,
        'min_m_c': min(m_c_values) if m_c_values else None,
        'max_m_c': max(m_c_values) if m_c_values else None,
        'min_kappa_vc': min(kappa_vc_values) if kappa_vc_values else None,
        'max_kappa_vc': max(kappa_vc_values) if kappa_vc_values else None
    }


def identify_next_test(
    joint_bounds: List[Dict],
    channel_bounds: Dict[str, List[Dict]]
) -> List[Dict]:
    """
    Rank channels by sensitivity in the allowed region.
    
    Returns:
        List of channel recommendations sorted by sensitivity
    """
    recommendations = []
    
    for channel_name, bounds in channel_bounds.items():
        if not bounds:
            continue
        
        # Compute sensitivity metric: how tight are the bounds?
        theta_maxes = [b['theta_max'] for b in bounds]
        kappa_vc_maxes = [b['kappa_vc_max_GeV'] for b in bounds]
        
        avg_theta_max = sum(theta_maxes) / len(theta_maxes) if theta_maxes else float('inf')
        avg_kappa_vc_max = sum(kappa_vc_maxes) / len(kappa_vc_maxes) if kappa_vc_maxes else float('inf')
        
        # Lower bounds = higher sensitivity
        sensitivity = 1.0 / (avg_theta_max * avg_kappa_vc_max + 1e-30)
        
        recommendations.append({
            'channel_name': channel_name,
            'sensitivity': sensitivity,
            'avg_theta_max': avg_theta_max,
            'avg_kappa_vc_max': avg_kappa_vc_max,
            'num_points': len(bounds)
        })
    
    # Sort by sensitivity (highest first)
    recommendations.sort(key=lambda x: x['sensitivity'], reverse=True)
    
    return recommendations


def check_orthogonality(channel_bounds: Dict[str, List[Dict]]) -> Dict:
    """
    Verify channels have different systematics.
    
    Returns:
        Dict with orthogonality metrics
    """
    channel_names = list(channel_bounds.keys())
    orthogonality_matrix = {}
    
    for i, ch1 in enumerate(channel_names):
        for ch2 in channel_names[i+1:]:
            bounds1 = channel_bounds[ch1]
            bounds2 = channel_bounds[ch2]
            
            if not bounds1 or not bounds2:
                continue
            
            # Compute correlation of bounds at overlapping m_c values
            m_c_overlap = set(b['m_c_GeV'] for b in bounds1) & set(b['m_c_GeV'] for b in bounds2)
            
            if not m_c_overlap:
                correlation = 0.0
            else:
                theta1 = [b['theta_max'] for b in bounds1 if b['m_c_GeV'] in m_c_overlap]
                theta2 = [b['theta_max'] for b in bounds2 if b['m_c_GeV'] in m_c_overlap]
                
                if len(theta1) == len(theta2) and len(theta1) > 1:
                    # Simple correlation coefficient
                    mean1 = sum(theta1) / len(theta1)
                    mean2 = sum(theta2) / len(theta2)
                    
                    numerator = sum((theta1[i] - mean1) * (theta2[i] - mean2) for i in range(len(theta1)))
                    denom1 = sum((t - mean1)**2 for t in theta1)
                    denom2 = sum((t - mean2)**2 for t in theta2)
                    
                    if denom1 > 0 and denom2 > 0:
                        correlation = numerator / math.sqrt(denom1 * denom2)
                    else:
                        correlation = 0.0
                else:
                    correlation = 0.0
            
            orthogonality_matrix[f"{ch1}_vs_{ch2}"] = {
                'correlation': correlation,
                'overlap_points': len(m_c_overlap),
                'orthogonal': abs(correlation) < 0.5  # Low correlation = orthogonal
            }
    
    return {
        'orthogonality_matrix': orthogonality_matrix,
        'all_orthogonal': all(
            v['orthogonal'] for v in orthogonality_matrix.values()
        ) if orthogonality_matrix else True
    }


def compute_correlation_matrix(channel_bounds: Dict[str, List[Dict]]) -> Dict:
    """
    Check for degenerate constraints.
    
    Returns:
        Correlation matrix between channels
    """
    return check_orthogonality(channel_bounds)


def identify_toggles() -> Dict[str, List[str]]:
    """
    List experimental toggles per channel.
    
    Returns:
        Dict mapping channel names to lists of toggle strategies
    """
    return {
        'fifth_force': [
            'material_swap',  # Different composition materials
            'geometry_reversal',  # Reverse test geometry
            'separation_modulation',  # Vary separation at multiple frequencies
            'pressure_temperature_change',  # Screening toggle + electrostatics diagnostics
            'patch_potential_characterization'  # Explicit EM diagnostics
        ],
        'equivalence_principle': [
            'multiple_material_pairs',  # Different nuclear sensitivities
            'seasonal_orbital_modulation',  # Time-dependent checks
            'independent_platform_crosscheck'  # Torsion vs atom interferometer
        ],
        'collider_higgs': [
            'consistency_across_production_modes',  # Different production channels
            'consistency_across_decay_channels',  # Different decay modes
            'multi_observable_agreement'  # Signal strength + BR + width
        ],
        'atomic_clocks': [
            'multi_species_comparison',  # Different sensitivity coefficients
            'multi_site_correlation',  # Cross-lab correlation
            'phase_consistency',  # Consistent phase relationships
            'consistent_scaling_across_transitions'  # Pattern matching
        ]
    }


def generate_joint_exclusion_plot(
    joint_bounds: List[Dict],
    output_path: str,
    channel_bounds: Optional[Dict[str, List[Dict]]] = None
) -> None:
    """
    Generate 2D exclusion plot (m_c vs |κ_cH v_c|).
    
    Note: Requires matplotlib. If not available, creates data file for plotting.
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Extract data
        m_c_values = [b['m_c_GeV'] for b in joint_bounds]
        kappa_vc_values = [b['kappa_vc_max_GeV'] for b in joint_bounds]
        
        # Create plot
        plt.figure(figsize=(10, 8))
        plt.loglog(m_c_values, kappa_vc_values, 'k-', linewidth=2, label='Joint Exclusion')
        
        # Add individual channels if provided
        if channel_bounds:
            colors = ['red', 'blue', 'green', 'orange']
            for i, (channel_name, bounds) in enumerate(channel_bounds.items()):
                if bounds:
                    m_c_ch = [b['m_c_GeV'] for b in bounds]
                    kappa_ch = [b['kappa_vc_max_GeV'] for b in bounds]
                    plt.loglog(m_c_ch, kappa_ch, '--', color=colors[i % len(colors)],
                              alpha=0.6, label=channel_name)
        
        plt.xlabel('m_c (GeV)', fontsize=12)
        plt.ylabel('|κ_cH v_c| (GeV)', fontsize=12)
        plt.title('Joint Scalar Field Exclusion Plot', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        
    except ImportError:
        # Fallback: create CSV for external plotting
        csv_path = output_path.replace('.png', '.csv')
        with open(csv_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['m_c_GeV', 'kappa_vc_max_GeV'])
            writer.writeheader()
            for bound in joint_bounds:
                writer.writerow({
                    'm_c_GeV': bound['m_c_GeV'],
                    'kappa_vc_max_GeV': bound['kappa_vc_max_GeV']
                })
        print(f"Matplotlib not available. Saved plot data to {csv_path}")


def save_joint_bounds_csv(joint_bounds: List[Dict], output_path: str) -> None:
    """Save joint bounds to CSV file."""
    with open(output_path, 'w') as f:
        fieldnames = ['m_c_GeV', 'lambda_m', 'theta_max', 'kappa_vc_max_GeV',
                     'domain_min', 'domain_max', 'channel_name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for bound in joint_bounds:
            writer.writerow(bound)


def generate_dashboard_json(
    joint_bounds: List[Dict],
    channel_bounds: Dict[str, List[Dict]],
    output_path: str
) -> None:
    """
    Generate dashboard JSON with allowed region and metrics.
    """
    allowed_region = compute_allowed_region(joint_bounds)
    next_tests = identify_next_test(joint_bounds, channel_bounds)
    orthogonality = check_orthogonality(channel_bounds)
    toggles = identify_toggles()
    
    dashboard = {
        'version': '1.0',
        'date_generated': str(Path(output_path).stat().st_mtime) if Path(output_path).exists() else '',
        'allowed_region': allowed_region,
        'next_test_recommendations': next_tests,
        'orthogonality_analysis': orthogonality,
        'experimental_toggles': toggles,
        'channel_coverage': {
            name: len(bounds) for name, bounds in channel_bounds.items()
        },
        'joint_bounds_summary': {
            'num_points': len(joint_bounds),
            'm_c_range': [min(b['m_c_GeV'] for b in joint_bounds),
                         max(b['m_c_GeV'] for b in joint_bounds)] if joint_bounds else [0, 0],
            'kappa_vc_range': [min(b['kappa_vc_max_GeV'] for b in joint_bounds),
                              max(b['kappa_vc_max_GeV'] for b in joint_bounds)] if joint_bounds else [0, 0]
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(dashboard, f, indent=2)
