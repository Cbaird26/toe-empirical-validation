#!/usr/bin/env python3
"""
Empirical Tests for Telemetry System
Tests sensor controller, server, and dashboard components.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_sensor_controller():
    """Test sensor controller structure."""
    print("Testing Sensor Controller...")
    
    controller_path = Path(__file__).parent.parent / "telemetry" / "quantized_sensor_loop.py"
    
    assert controller_path.exists(), "Sensor controller not found"
    
    # Check imports
    with open(controller_path, 'r') as f:
        content = f.read()
    
    required_imports = ['requests', 'csv', 'datetime']
    for imp in required_imports:
        assert imp in content, f"Missing import: {imp}"
    
    # Check Z-Loop logic
    assert 'zora_logic' in content, "Should have zora_logic method"
    assert 'coherence' in content.lower(), "Should compute coherence"
    
    print("  ✓ Sensor controller structure valid")
    return True


def test_telemetry_server():
    """Test telemetry server structure."""
    print("Testing Telemetry Server...")
    
    server_path = Path(__file__).parent.parent / "telemetry" / "telemetry_server.py"
    
    assert server_path.exists(), "Telemetry server not found"
    
    # Check imports
    with open(server_path, 'r') as f:
        content = f.read()
    
    required_imports = ['fastapi', 'sqlite3', 'pydantic']
    for imp in required_imports:
        assert imp in content, f"Missing import: {imp}"
    
    # Check endpoints
    assert '/ingest' in content, "Should have /ingest endpoint"
    assert '/query' in content, "Should have /query endpoint"
    assert '/stats' in content, "Should have /stats endpoint"
    
    # Check FTS5
    assert 'fts5' in content.lower(), "Should use FTS5 for search"
    
    print("  ✓ Telemetry server structure valid")
    return True


def test_dashboard():
    """Test dashboard structure."""
    print("Testing Dashboard...")
    
    dashboard_path = Path(__file__).parent.parent / "telemetry" / "telemetry_dashboard.py"
    
    assert dashboard_path.exists(), "Dashboard not found"
    
    # Check imports
    with open(dashboard_path, 'r') as f:
        content = f.read()
    
    required_imports = ['streamlit', 'pandas', 'sqlite3']
    for imp in required_imports:
        assert imp in content, f"Missing import: {imp}"
    
    # Check visualization
    assert 'line_chart' in content, "Should have line chart"
    assert 'coherence' in content.lower(), "Should compute coherence"
    
    print("  ✓ Dashboard structure valid")
    return True


def test_requirements():
    """Test requirements file."""
    print("Testing Requirements...")
    
    req_path = Path(__file__).parent.parent / "telemetry" / "requirements.txt"
    
    assert req_path.exists(), "Requirements file not found"
    
    with open(req_path, 'r') as f:
        requirements = f.read()
    
    required_packages = ['fastapi', 'streamlit', 'pandas', 'requests']
    for pkg in required_packages:
        assert pkg in requirements.lower(), f"Missing package: {pkg}"
    
    print("  ✓ Requirements file valid")
    return True


def run_all_tests():
    """Run all telemetry tests."""
    print("=" * 60)
    print("Telemetry System Empirical Tests")
    print("=" * 60)
    print()
    
    results = []
    
    try:
        results.append(("Sensor Controller", test_sensor_controller()))
    except Exception as e:
        print(f"  ✗ Sensor controller test failed: {e}")
        results.append(("Sensor Controller", False))
    
    try:
        results.append(("Telemetry Server", test_telemetry_server()))
    except Exception as e:
        print(f"  ✗ Telemetry server test failed: {e}")
        results.append(("Telemetry Server", False))
    
    try:
        results.append(("Dashboard", test_dashboard()))
    except Exception as e:
        print(f"  ✗ Dashboard test failed: {e}")
        results.append(("Dashboard", False))
    
    try:
        results.append(("Requirements", test_requirements()))
    except Exception as e:
        print(f"  ✗ Requirements test failed: {e}")
        results.append(("Requirements", False))
    
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
