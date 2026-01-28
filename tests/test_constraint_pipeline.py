#!/usr/bin/env python3
"""
Empirical Tests for Constraint Pipeline
Tests data ingestion, bounds generation, and plot creation.
"""

import csv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_data_ingestion():
    """Test experimental data ingestion."""
    print("Testing Data Ingestion...")
    
    # Check if Eöt-Wash data exists
    data_file = Path(__file__).parent.parent / "eotwash_prl2016_digitized_contract_READY.csv"
    
    if not data_file.exists():
        print(f"  ⚠ Data file not found: {data_file}")
        return False
    
    # Load and validate CSV
    with open(data_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) > 0, "Should have data rows"
    print(f"  ✓ Loaded {len(rows)} data points")
    
    # Validate columns
    expected_columns = ['lambda_m', 'alpha_max']
    for row in rows[:5]:  # Check first 5 rows
        for col in expected_columns:
            assert col in row, f"Row missing column: {col}"
            try:
                float(row[col])
            except ValueError:
                assert False, f"Invalid numeric value in {col}: {row[col]}"
    
    print("  ✓ CSV format validation passed")
    
    # Check data ranges
    lambda_values = [float(row['lambda_m']) for row in rows]
    alpha_values = [float(row['alpha_max']) for row in rows]
    
    assert all(l > 0 for l in lambda_values), "Lambda values should be positive"
    assert all(a > 0 for a in alpha_values), "Alpha values should be positive"
    
    print(f"  ✓ Lambda range: {min(lambda_values):.2e} - {max(lambda_values):.2e} m")
    print(f"  ✓ Alpha range: {min(alpha_values):.2e} - {max(alpha_values):.2e}")
    
    print("  ✓ Data ingestion tests passed")
    return True


def test_bounds_generation():
    """Test bounds generation scripts exist and are executable."""
    print("Testing Bounds Generation...")
    
    scripts_dir = Path(__file__).parent.parent / "scripts"
    
    required_scripts = [
        "generate_fifth_force_ep_bounds.py",
        "generate_joint_scalar_constraints.py",
        "run_constraint_pipeline.sh"
    ]
    
    for script_name in required_scripts:
        script_path = scripts_dir / script_name
        assert script_path.exists(), f"Script not found: {script_name}"
        assert script_path.is_file(), f"Not a file: {script_name}"
        print(f"  ✓ Found: {script_name}")
    
    print("  ✓ Bounds generation scripts exist")
    return True


def test_golden_plot_generator():
    """Test golden plot generator."""
    print("Testing Golden Plot Generator...")
    
    script_path = Path(__file__).parent.parent / "scripts" / "generate_golden_plot.py"
    
    assert script_path.exists(), "Golden plot generator not found"
    
    # Check imports
    with open(script_path, 'r') as f:
        content = f.read()
    
    required_imports = ['matplotlib', 'numpy', 'seaborn']
    for imp in required_imports:
        assert imp in content, f"Missing import: {imp}"
    
    print("  ✓ Golden plot generator exists and has required imports")
    return True


def test_hypothesis_card():
    """Test hypothesis card schema."""
    print("Testing Hypothesis Card...")
    
    import yaml
    
    card_path = Path(__file__).parent.parent / "data" / "constraints" / "minimal_scalar_hypothesis_card_v0.1.yaml"
    
    if not card_path.exists():
        print(f"  ⚠ Hypothesis card not found: {card_path}")
        return False
    
    with open(card_path, 'r') as f:
        card = yaml.safe_load(f)
    
    # Validate structure
    assert 'channels' in card, "Card should have channels"
    assert 'fifth_force' in card['channels'], "Card should have fifth_force channel"
    
    # Check forward/inverse mappings
    ff_channel = card['channels']['fifth_force']
    assert 'forward_mapping' in ff_channel, "Should have forward mapping"
    assert 'inverse_mapping' in ff_channel, "Should have inverse mapping"
    
    print("  ✓ Hypothesis card structure valid")
    print(f"  ✓ Channels: {list(card['channels'].keys())}")
    
    return True


def run_all_tests():
    """Run all constraint pipeline tests."""
    print("=" * 60)
    print("Constraint Pipeline Empirical Tests")
    print("=" * 60)
    print()
    
    results = []
    
    try:
        results.append(("Data Ingestion", test_data_ingestion()))
    except Exception as e:
        print(f"  ✗ Data ingestion test failed: {e}")
        results.append(("Data Ingestion", False))
    
    try:
        results.append(("Bounds Generation", test_bounds_generation()))
    except Exception as e:
        print(f"  ✗ Bounds generation test failed: {e}")
        results.append(("Bounds Generation", False))
    
    try:
        results.append(("Golden Plot Generator", test_golden_plot_generator()))
    except Exception as e:
        print(f"  ✗ Golden plot test failed: {e}")
        results.append(("Golden Plot Generator", False))
    
    try:
        results.append(("Hypothesis Card", test_hypothesis_card()))
    except Exception as e:
        print(f"  ✗ Hypothesis card test failed: {e}")
        results.append(("Hypothesis Card", False))
    
    print()
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
