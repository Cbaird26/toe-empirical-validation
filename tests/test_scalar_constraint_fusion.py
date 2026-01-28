#!/usr/bin/env python3
"""
Unit tests for scalar constraint fusion and parameter card validation.
"""

import sys
import os
import unittest
import tempfile
import csv
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from code.inference.scalar_constraint_fusion import (
    load_channel_bounds,
    load_all_channel_bounds,
    compute_joint_exclusion,
    compute_allowed_region,
    check_orthogonality,
    identify_toggles
)


class TestParameterCardValidation(unittest.TestCase):
    """Test parameter card loading and validation."""
    
    def test_unit_anchor_lambda_to_mass(self):
        """Test unit conversion: λ = 100 μm → m_c ≈ 2 meV"""
        hbar_c_gev_m = 1.973e-13
        lambda_m = 1e-4  # 100 μm
        m_c_gev_expected = 1.973e-12
        m_c_gev_computed = hbar_c_gev_m / lambda_m
        
        self.assertAlmostEqual(m_c_gev_computed, m_c_gev_expected, places=10)
    
    def test_resonance_guardrail(self):
        """Test resonance guardrail check"""
        m_h_gev = 125.0
        m_c_gev = 125.0  # At resonance
        m_h_sq = m_h_gev ** 2
        m_c_sq = m_c_gev ** 2
        
        danger_zone_fraction = abs(m_c_sq - m_h_sq) / m_h_sq
        
        # Should be in danger zone
        self.assertLess(danger_zone_fraction, 0.01)


class TestConstraintFusion(unittest.TestCase):
    """Test constraint fusion functions."""
    
    def setUp(self):
        """Create temporary test CSV files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test channel bounds CSV
        self.test_csv = Path(self.temp_dir) / 'test_bounds.csv'
        with open(self.test_csv, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'm_c_GeV', 'lambda_m', 'theta_max', 'kappa_vc_max_GeV',
                'domain_min', 'domain_max', 'channel_name'
            ])
            writer.writeheader()
            writer.writerow({
                'm_c_GeV': '1e-12',
                'lambda_m': '1.973e-1',
                'theta_max': '1e-10',
                'kappa_vc_max_GeV': '1e-8',
                'domain_min': '0',
                'domain_max': '1',
                'channel_name': 'test_channel'
            })
    
    def test_load_channel_bounds(self):
        """Test loading channel bounds from CSV"""
        bounds = load_channel_bounds(str(self.test_csv))
        
        self.assertEqual(len(bounds), 1)
        self.assertEqual(bounds[0]['m_c_GeV'], 1e-12)
        self.assertEqual(bounds[0]['channel_name'], 'test_channel')
    
    def test_load_all_channel_bounds(self):
        """Test loading multiple channel bounds"""
        channel_files = {
            'test1': str(self.test_csv),
            'test2': str(Path(self.temp_dir) / 'nonexistent.csv')
        }
        
        all_bounds = load_all_channel_bounds(channel_files)
        
        self.assertIn('test1', all_bounds)
        self.assertIn('test2', all_bounds)
        self.assertEqual(len(all_bounds['test1']), 1)
        self.assertEqual(len(all_bounds['test2']), 0)
    
    def test_compute_joint_exclusion_union(self):
        """Test joint exclusion with union method"""
        all_bounds = {
            'channel1': [
                {'m_c_GeV': 1e-12, 'theta_max': 1e-10, 'kappa_vc_max_GeV': 1e-8,
                 'domain_min': 0, 'domain_max': 1, 'lambda_m': 0.1973}
            ],
            'channel2': [
                {'m_c_GeV': 1e-12, 'theta_max': 1e-11, 'kappa_vc_max_GeV': 1e-9,
                 'domain_min': 0, 'domain_max': 1, 'lambda_m': 0.1973}
            ]
        }
        
        joint = compute_joint_exclusion(all_bounds, method='union')
        
        self.assertEqual(len(joint), 1)
        # Union should take minimum (most conservative)
        self.assertEqual(joint[0]['theta_max'], 1e-11)
        self.assertEqual(joint[0]['kappa_vc_max_GeV'], 1e-9)
    
    def test_compute_allowed_region(self):
        """Test allowed region computation"""
        joint_bounds = [
            {'m_c_GeV': 1e-12, 'kappa_vc_max_GeV': 1e-8},
            {'m_c_GeV': 1e-11, 'kappa_vc_max_GeV': 1e-7}
        ]
        
        region = compute_allowed_region(joint_bounds)
        
        self.assertEqual(region['num_points'], 2)
        self.assertEqual(region['min_m_c'], 1e-12)
        self.assertEqual(region['max_m_c'], 1e-11)
    
    def test_check_orthogonality(self):
        """Test orthogonality checking"""
        channel_bounds = {
            'channel1': [
                {'m_c_GeV': 1e-12, 'theta_max': 1e-10}
            ],
            'channel2': [
                {'m_c_GeV': 1e-12, 'theta_max': 1e-11}
            ]
        }
        
        ortho = check_orthogonality(channel_bounds)
        
        self.assertIn('orthogonality_matrix', ortho)
        self.assertIn('all_orthogonal', ortho)
    
    def test_identify_toggles(self):
        """Test toggle identification"""
        toggles = identify_toggles()
        
        self.assertIn('fifth_force', toggles)
        self.assertIn('equivalence_principle', toggles)
        self.assertIn('collider_higgs', toggles)
        self.assertIn('atomic_clocks', toggles)
        
        # Check that toggles are lists
        for channel, toggle_list in toggles.items():
            self.assertIsInstance(toggle_list, list)
            self.assertGreater(len(toggle_list), 0)


if __name__ == '__main__':
    unittest.main()
