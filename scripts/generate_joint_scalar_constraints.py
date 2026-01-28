#!/usr/bin/env python3
"""
Generate joint scalar constraints from all three channels.
Main script that combines fifth-force/EP, collider Higgs, and clocks/spectroscopy bounds.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from code.inference.scalar_constraint_fusion import (
    load_all_channel_bounds,
    compute_joint_exclusion,
    generate_joint_exclusion_plot,
    save_joint_bounds_csv,
    generate_dashboard_json
)


def main():
    """Main function to generate joint constraints."""
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    results_dir = project_root / 'results' / 'scalar_constraints'
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Define channel files
    channel_files = {
        'fifth_force_ep': str(results_dir / 'fifth_force_ep_bounds.csv'),
        'collider_higgs': str(results_dir / 'collider_higgs_bounds.csv'),
        'atomic_clocks': str(results_dir / 'clocks_spectroscopy_bounds.csv')
    }
    
    # Load all channel bounds
    print("Loading channel bounds...")
    all_bounds = load_all_channel_bounds(channel_files)
    
    # Check which channels have data
    available_channels = {k: v for k, v in all_bounds.items() if v}
    print(f"Available channels: {list(available_channels.keys())}")
    
    if not available_channels:
        print("Error: No channel bounds found. Please generate bounds first.")
        print("Run:")
        print("  python scripts/generate_fifth_force_ep_bounds.py")
        print("  python scripts/generate_clocks_spectroscopy_bounds.py")
        print("  python scripts/generate_collider_higgs_bounds.py")
        return
    
    # Compute joint exclusion (union method: most conservative)
    print("Computing joint exclusion...")
    joint_bounds = compute_joint_exclusion(available_channels, method='union')
    
    if not joint_bounds:
        print("Warning: No joint bounds computed.")
        return
    
    print(f"Computed {len(joint_bounds)} joint exclusion points")
    
    # Save joint bounds CSV
    joint_csv = results_dir / 'joint_bounds.csv'
    save_joint_bounds_csv(joint_bounds, str(joint_csv))
    print(f"Saved joint bounds: {joint_csv}")
    
    # Generate exclusion plot
    plot_file = results_dir / 'joint_exclusion_plot.png'
    print(f"Generating exclusion plot: {plot_file}")
    generate_joint_exclusion_plot(
        joint_bounds,
        str(plot_file),
        channel_bounds=available_channels
    )
    
    # Generate dashboard JSON
    dashboard_file = results_dir / 'joint_dashboard.json'
    print(f"Generating dashboard: {dashboard_file}")
    generate_dashboard_json(
        joint_bounds,
        available_channels,
        str(dashboard_file)
    )
    
    print("\nJoint constraint generation complete!")
    print(f"Results in: {results_dir}")


if __name__ == '__main__':
    main()
