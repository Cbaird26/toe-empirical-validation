#!/usr/bin/env python3
"""
Compute ToE Predictions and Compare to Experimental Bounds
This script computes the Theory of Everything predictions for α(λ) and compares
them to experimental bounds to determine if the theory is validated or falsified.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple


def compute_toe_alpha_prediction(lambda_m: float, theta_hc: float = 0.01, 
                                 m_h_GeV: float = 125.0, K_ToE: float = 1.0) -> float:
    """
    Compute ToE prediction for α(λ) from the unified Lagrangian.
    
    From the ToE, the fifth-force strength parameter α is:
    α(λ) = (θ_hc² / K_ToE) × (m_h² / (m_h² - m_c²))²
    
    Where:
    - λ = interaction range (m)
    - m_c = mediator mass (GeV) = ħc / λ
    - θ_hc = Higgs-Φc mixing angle
    - m_h = Higgs mass (125 GeV)
    - K_ToE = normalization constant
    
    Args:
        lambda_m: Interaction range in meters
        theta_hc: Higgs-Φc mixing angle (default: 0.01)
        m_h_GeV: Higgs mass in GeV (default: 125.0)
        K_ToE: Normalization constant (default: 1.0)
    
    Returns:
        Predicted α value
    """
    # Convert λ to m_c (mediator mass)
    # m_c = ħc / λ, where ħc ≈ 1.97e-16 GeV·m
    hbar_c = 1.97e-16  # GeV·m
    m_c_GeV = hbar_c / lambda_m if lambda_m > 0 else np.inf
    
    # Avoid resonance (m_c = m_h)
    if abs(m_c_GeV - m_h_GeV) < 0.1:
        m_c_GeV = m_h_GeV - 0.1
    
    # Compute α prediction
    # α = (θ_hc² / K_ToE) × (m_h² / (m_h² - m_c²))²
    m_h_sq = m_h_GeV ** 2
    m_c_sq = m_c_GeV ** 2
    
    denominator = m_h_sq - m_c_sq
    if abs(denominator) < 1e-10:
        # Near resonance, return large value (would need regularization)
        return 1e10
    
    ratio = m_h_sq / denominator
    alpha = (theta_hc ** 2 / K_ToE) * (ratio ** 2)
    
    return alpha


def compute_toe_prediction_band(lambda_values: np.ndarray, 
                                theta_range: Tuple[float, float] = (1e-4, 0.1),
                                num_theta_samples: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute ToE prediction band across parameter space.
    
    Args:
        lambda_values: Array of λ values (meters)
        theta_range: Range of θ_hc values to sample
        num_theta_samples: Number of θ samples
    
    Returns:
        Tuple of (alpha_min, alpha_max, alpha_median) arrays
    """
    theta_samples = np.logspace(np.log10(theta_range[0]), np.log10(theta_range[1]), num_theta_samples)
    
    alpha_predictions = []
    for lambda_val in lambda_values:
        alphas = []
        for theta in theta_samples:
            alpha = compute_toe_alpha_prediction(lambda_val, theta_hc=theta)
            alphas.append(alpha)
        alpha_predictions.append(alphas)
    
    alpha_predictions = np.array(alpha_predictions)
    
    alpha_min = np.min(alpha_predictions, axis=1)
    alpha_max = np.max(alpha_predictions, axis=1)
    alpha_median = np.median(alpha_predictions, axis=1)
    
    return alpha_min, alpha_max, alpha_median


def compare_predictions_to_bounds(bounds_file: Path, output_dir: Path) -> Dict:
    """
    Compare ToE predictions to experimental bounds.
    
    Args:
        bounds_file: Path to joint_bounds.csv
        output_dir: Output directory for results
    
    Returns:
        Dictionary with comparison results
    """
    # Load bounds
    bounds_df = pd.read_csv(bounds_file)
    
    # Extract lambda values
    lambda_values = bounds_df['lambda_m'].values
    
    # Compute ToE predictions
    print("Computing ToE predictions...")
    alpha_min, alpha_max, alpha_median = compute_toe_prediction_band(lambda_values)
    
    # Get experimental bounds (alpha_max from bounds)
    # Note: bounds file has theta_max, need to convert to alpha_max
    # For now, use a conservative estimate based on theta_max
    # alpha_bound ≈ (theta_max² / K_ToE) for comparison
    theta_max = bounds_df['theta_max'].values
    K_ToE = 1.0
    alpha_bound_estimate = (theta_max ** 2) / K_ToE
    
    # Compare predictions to bounds
    violations = []
    validations = []
    
    for i, lambda_val in enumerate(lambda_values):
        pred_max = alpha_max[i]
        bound = alpha_bound_estimate[i]
        
        if pred_max > bound:
            violations.append({
                'lambda_m': lambda_val,
                'predicted_alpha_max': pred_max,
                'bound_alpha': bound,
                'violation_factor': pred_max / bound
            })
        else:
            validations.append({
                'lambda_m': lambda_val,
                'predicted_alpha_max': pred_max,
                'bound_alpha': bound,
                'safety_margin': bound / pred_max if pred_max > 0 else np.inf
            })
    
    # Create comparison plot
    plt.figure(figsize=(12, 8))
    
    # Plot experimental bounds
    plt.loglog(lambda_values, alpha_bound_estimate, 'r-', linewidth=2, 
               label='Experimental Bound (Upper Limit)', alpha=0.7)
    plt.fill_between(lambda_values, alpha_bound_estimate, 1e10, 
                     alpha=0.2, color='red', label='Excluded Region')
    
    # Plot ToE predictions
    plt.loglog(lambda_values, alpha_median, 'b-', linewidth=2, 
               label='ToE Prediction (Median)', alpha=0.8)
    plt.fill_between(lambda_values, alpha_min, alpha_max, 
                     alpha=0.3, color='blue', label='ToE Prediction Band')
    
    # Mark violations
    if violations:
        violation_lambdas = [v['lambda_m'] for v in violations]
        violation_alphas = [v['predicted_alpha_max'] for v in violations]
        plt.scatter(violation_lambdas, violation_alphas, 
                   color='red', marker='x', s=100, label='Violations', zorder=5)
    
    plt.xlabel('Interaction Range λ (m)', fontsize=12)
    plt.ylabel('Fifth-Force Strength α', fontsize=12)
    plt.title('ToE Predictions vs. Experimental Bounds', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_file = output_dir / 'toe_predictions_vs_bounds.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate summary
    total_points = len(lambda_values)
    num_violations = len(violations)
    num_validations = len(validations)
    validation_rate = num_validations / total_points if total_points > 0 else 0
    
    summary = {
        'total_data_points': int(total_points),
        'violations': num_violations,
        'validations': num_validations,
        'validation_rate': float(validation_rate),
        'status': 'VALIDATED' if validation_rate > 0.95 else 'PARTIALLY_VALIDATED' if validation_rate > 0.5 else 'FALSIFIED',
        'interpretation': {
            'if_validated': 'ToE predictions lie within experimental bounds. Theory is consistent with data.',
            'if_partial': 'Some ToE predictions exceed bounds. Theory may need parameter adjustment.',
            'if_falsified': 'ToE predictions violate experimental bounds. Theory needs revision.'
        }
    }
    
    # Save results
    results = {
        'summary': summary,
        'violations': violations[:10],  # First 10 violations
        'sample_validations': validations[:10],  # First 10 validations
        'prediction_statistics': {
            'alpha_min': float(np.min(alpha_min)),
            'alpha_max': float(np.max(alpha_max)),
            'alpha_median_min': float(np.min(alpha_median)),
            'alpha_median_max': float(np.max(alpha_median))
        }
    }
    
    results_file = output_dir / 'toe_validation_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    bounds_file = project_root / "results" / "scalar_constraints" / "joint_bounds.csv"
    output_dir = project_root / "results" / "empirical_validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not bounds_file.exists():
        print(f"Error: Bounds file not found: {bounds_file}")
        print("Run 'make constraint-pipeline' first to generate bounds.")
        return
    
    print("="*80)
    print("ToE PREDICTION VALIDATION")
    print("="*80)
    print(f"Bounds file: {bounds_file}")
    print(f"Output directory: {output_dir}\n")
    
    results = compare_predictions_to_bounds(bounds_file, output_dir)
    
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    print(f"Total data points: {results['summary']['total_data_points']}")
    print(f"Violations: {results['summary']['violations']}")
    print(f"Validations: {results['summary']['validations']}")
    print(f"Validation rate: {results['summary']['validation_rate']*100:.2f}%")
    print(f"\nStatus: {results['summary']['status']}")
    print(f"\nInterpretation:")
    if results['summary']['status'] == 'VALIDATED':
        print(f"  {results['summary']['interpretation']['if_validated']}")
    elif results['summary']['status'] == 'PARTIALLY_VALIDATED':
        print(f"  {results['summary']['interpretation']['if_partial']}")
    else:
        print(f"  {results['summary']['interpretation']['if_falsified']}")
    
    print(f"\nResults saved to: {output_dir}")
    print(f"Plot saved to: {output_dir / 'toe_predictions_vs_bounds.png'}")


if __name__ == "__main__":
    main()
