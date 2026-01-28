#!/usr/bin/env python3
"""
Golden Plot Generator
Creates publication-ready exclusion plots showing α_limit(λ) vs predicted α(λ) band.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Constants from hypothesis card
M_HIGGS_GEV = 125.0
K_ToE = 1.764e31
HBAR_C_GEV_M = 1.973e-13


def load_joint_bounds(csv_path: Path) -> List[Dict]:
    """Load joint constraint bounds from CSV."""
    bounds = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bounds.append({
                'm_c_GeV': float(row['m_c_GeV']),
                'lambda_m': float(row['lambda_m']),
                'theta_max': float(row['theta_max']),
                'kappa_vc_max_GeV': float(row['kappa_vc_max_GeV']),
                'channel_name': row.get('channel_name', 'joint')
            })
    return bounds


def compute_predicted_alpha_band(lambda_values: np.ndarray, 
                                 theta_values: np.ndarray) -> np.ndarray:
    """
    Compute predicted α(λ) band from ToE.
    
    Uses forward mapping: α(λ) = (θ_hc² / K_ToE) × (m_h² / (m_h² - m_c²))²
    """
    m_h_sq = M_HIGGS_GEV ** 2
    
    # Convert λ to m_c
    m_c_values = HBAR_C_GEV_M / lambda_values
    
    # Compute α for each θ
    alpha_bands = []
    for theta in theta_values:
        m_c_sq = m_c_values ** 2
        denominator = m_h_sq - m_c_sq
        
        # Avoid resonance (m_c ≈ m_h)
        mask = np.abs(denominator) > 0.01 * m_h_sq
        
        alpha = np.zeros_like(lambda_values)
        alpha[mask] = (theta ** 2 / K_ToE) * (m_h_sq / denominator[mask]) ** 2
        alpha[~mask] = np.nan
        
        alpha_bands.append(alpha)
    
    return np.array(alpha_bands)


def generate_golden_plot(bounds_csv: Path, output_dir: Path, 
                        predicted_theta_range: Optional[tuple] = None):
    """
    Generate golden exclusion plot.
    
    Args:
        bounds_csv: Path to joint bounds CSV
        output_dir: Output directory for plots
        predicted_theta_range: Tuple (theta_min, theta_max) for predicted band
    """
    if predicted_theta_range is None:
        predicted_theta_range = (1e-10, 1e-6)  # Default range
    
    print(f"Loading bounds from: {bounds_csv}")
    bounds = load_joint_bounds(bounds_csv)
    
    if not bounds:
        raise ValueError("No bounds data found")
    
    # Extract lambda and alpha_max from bounds
    # Convert theta_max to alpha_max using inverse mapping
    lambda_values = np.array([b['lambda_m'] for b in bounds])
    theta_max_values = np.array([b['theta_max'] for b in bounds])
    
    # Convert theta_max to alpha_max (inverse of forward mapping)
    m_h_sq = M_HIGGS_GEV ** 2
    m_c_values = HBAR_C_GEV_M / lambda_values
    m_c_sq = m_c_values ** 2
    
    # alpha_max = (theta_max² / K_ToE) × (m_h² / (m_h² - m_c²))²
    denominator = m_h_sq - m_c_sq
    mask = np.abs(denominator) > 0.01 * m_h_sq
    
    alpha_max_values = np.zeros_like(lambda_values)
    alpha_max_values[mask] = (theta_max_values[mask] ** 2 / K_ToE) * \
                             (m_h_sq / denominator[mask]) ** 2
    alpha_max_values[~mask] = np.nan
    
    # Create lambda grid for predicted band
    lambda_min = np.min(lambda_values[lambda_values > 0])
    lambda_max = np.max(lambda_values)
    lambda_grid = np.logspace(np.log10(lambda_min), np.log10(lambda_max), 200)
    
    # Compute predicted alpha band
    theta_min, theta_max = predicted_theta_range
    theta_grid = np.logspace(np.log10(theta_min), np.log10(theta_max), 5)
    alpha_bands = compute_predicted_alpha_band(lambda_grid, theta_grid)
    
    # Create plot
    plt.style.use('seaborn-v0_8-paper')
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot exclusion region (above the curve is excluded)
    ax.loglog(lambda_values, alpha_max_values, 'r-', linewidth=2, 
             label='Exclusion Bound (Eöt-Wash + EP)', zorder=3)
    
    # Fill excluded region
    ax.fill_between(lambda_values, alpha_max_values, 1e10, 
                    alpha=0.3, color='red', label='Excluded Region', zorder=1)
    
    # Plot predicted band
    alpha_min = np.nanmin(alpha_bands, axis=0)
    alpha_max_pred = np.nanmax(alpha_bands, axis=0)
    
    ax.fill_between(lambda_grid, alpha_min, alpha_max_pred, 
                   alpha=0.2, color='blue', label='ToE Predicted Band', zorder=2)
    ax.loglog(lambda_grid, alpha_min, 'b--', linewidth=1.5, alpha=0.7)
    ax.loglog(lambda_grid, alpha_max_pred, 'b--', linewidth=1.5, alpha=0.7)
    
    # Formatting
    ax.set_xlabel('Force Range λ (m)', fontsize=12)
    ax.set_ylabel('Yukawa Strength α', fontsize=12)
    ax.set_title('Fifth-Force Constraints: Exclusion Bound vs ToE Prediction', 
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, which='both')
    
    # Set axis limits
    ax.set_xlim(lambda_min * 0.5, lambda_max * 2)
    ax.set_ylim(np.nanmin(alpha_max_values) * 0.1, np.nanmax(alpha_max_values) * 10)
    
    plt.tight_layout()
    
    # Save plots
    output_dir.mkdir(parents=True, exist_ok=True)
    
    png_file = output_dir / 'golden_exclusion_plot.png'
    pdf_file = output_dir / 'golden_exclusion_plot.pdf'
    
    plt.savefig(png_file, dpi=300, bbox_inches='tight')
    print(f"  Saved PNG: {png_file}")
    
    plt.savefig(pdf_file, bbox_inches='tight')
    print(f"  Saved PDF: {pdf_file}")
    
    plt.close()
    
    # Generate summary JSON
    summary = {
        'plot_generated_at': str(Path.cwd()),
        'bounds_file': str(bounds_csv),
        'lambda_range': {
            'min': float(lambda_min),
            'max': float(lambda_max)
        },
        'alpha_exclusion_range': {
            'min': float(np.nanmin(alpha_max_values)),
            'max': float(np.nanmax(alpha_max_values))
        },
        'predicted_theta_range': {
            'min': float(theta_min),
            'max': float(theta_max)
        },
        'data_points': len(bounds)
    }
    
    summary_file = output_dir / 'golden_plot_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  Saved summary: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate golden exclusion plot")
    parser.add_argument("--bounds-csv", 
                       default="results/scalar_constraints/joint_bounds.csv",
                       help="Path to joint bounds CSV")
    parser.add_argument("--output-dir",
                       default="results/scalar_constraints",
                       help="Output directory for plots")
    parser.add_argument("--theta-min", type=float, default=1e-10,
                       help="Minimum theta for predicted band")
    parser.add_argument("--theta-max", type=float, default=1e-6,
                       help="Maximum theta for predicted band")
    
    args = parser.parse_args()
    
    bounds_csv = Path(args.bounds_csv).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    
    if not bounds_csv.exists():
        print(f"Warning: Bounds CSV not found: {bounds_csv}")
        print("  Run constraint pipeline first: ./scripts/run_constraint_pipeline.sh")
        return
    
    generate_golden_plot(
        bounds_csv,
        output_dir,
        predicted_theta_range=(args.theta_min, args.theta_max)
    )
    
    print("\n✓ Golden plot generation complete!")


if __name__ == '__main__':
    main()
