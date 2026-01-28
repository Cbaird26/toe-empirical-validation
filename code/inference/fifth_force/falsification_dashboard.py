"""
Falsification Dashboard
Generates dashboard with metrics from all constraint channels
"""

import json
from pathlib import Path
from typing import Dict, Optional


def add_joint_scalar_metrics(
    dashboard: Dict,
    joint_dashboard_path: str
) -> Dict:
    """
    Integrate joint scalar constraint results into falsification dashboard.
    
    Args:
        dashboard: Existing dashboard dictionary
        joint_dashboard_path: Path to joint_dashboard.json from scalar fusion
    
    Returns:
        Updated dashboard with joint scalar metrics
    """
    joint_path = Path(joint_dashboard_path)
    
    if not joint_path.exists():
        dashboard['joint_scalar'] = {
            'status': 'not_available',
            'message': 'Joint scalar constraints not yet generated'
        }
        return dashboard
    
    # Load joint dashboard
    with open(joint_path, 'r') as f:
        joint_data = json.load(f)
    
    # Add joint scalar section
    dashboard['joint_scalar'] = {
        'status': 'available',
        'allowed_region': joint_data.get('allowed_region', {}),
        'next_test_recommendations': joint_data.get('next_test_recommendations', []),
        'orthogonality': joint_data.get('orthogonality_analysis', {}),
        'channel_coverage': joint_data.get('channel_coverage', {}),
        'joint_bounds_summary': joint_data.get('joint_bounds_summary', {}),
        'experimental_toggles': joint_data.get('experimental_toggles', {})
    }
    
    return dashboard


def generate_falsification_dashboard(
    output_path: str,
    joint_dashboard_path: Optional[str] = None
) -> None:
    """
    Generate complete falsification dashboard.
    
    Args:
        output_path: Path to save dashboard JSON
        joint_dashboard_path: Optional path to joint scalar dashboard
    """
    dashboard = {
        'version': '2.0',
        'title': 'ToE Constraint Pipeline Falsification Dashboard'
    }
    
    # Add joint scalar metrics if available
    if joint_dashboard_path:
        dashboard = add_joint_scalar_metrics(dashboard, joint_dashboard_path)
    
    # Save dashboard
    with open(output_path, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"Falsification dashboard saved: {output_path}")
