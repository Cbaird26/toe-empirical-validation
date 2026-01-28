#!/usr/bin/env python3
"""
Empirical Tests for Canon Ingestion System
Tests document parsing, claim extraction, and equation identification.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from canon.scripts.equation_parser import EquationParser
from canon.scripts.claim_extractor import ClaimExtractor


def test_equation_parser():
    """Test equation extraction."""
    print("Testing Equation Parser...")
    
    parser = EquationParser()
    
    test_text = r"""
    The unified Lagrangian is:
    $$L = L_{GR} + L_{SM} + L_{\Phi_c} + L_E$$
    
    The coupling strength is given by:
    $\kappa_{cH} v_c = \theta_{hc} (m_h^2 - m_c^2)$
    
    And the force range:
    \begin{equation}
    \lambda = \frac{\hbar c}{m_c}
    \end{equation}
    """
    
    equations = parser.extract_equations(test_text, "Test Section", page_number=1)
    
    assert len(equations) > 0, "Should extract at least one equation"
    print(f"  ✓ Extracted {len(equations)} equations")
    
    # Check equation IDs
    for eq in equations:
        assert eq.equation_id.startswith("EQ_"), "Equation ID should start with EQ_"
        assert len(eq.latex_formula) > 0, "Equation should have LaTeX formula"
    
    print("  ✓ Equation parser tests passed")
    return True


def test_claim_extractor():
    """Test claim extraction and classification."""
    print("Testing Claim Extractor...")
    
    extractor = ClaimExtractor()
    
    test_text = """
    The scalar field Φ_c couples to the Standard Model via Higgs-portal mixing.
    This coupling generates a Yukawa-type fifth force that deviates from inverse-square gravity.
    Experimental constraints from Eöt-Wash torsion balance tests limit the coupling strength.
    The theoretical prediction suggests that the coupling may be observable in future experiments.
    This has profound implications for our understanding of consciousness and awareness.
    """
    
    claims = extractor.extract_claims(test_text, "Test Section", "test_doc.docx")
    
    assert len(claims) > 0, "Should extract at least one claim"
    print(f"  ✓ Extracted {len(claims)} claims")
    
    # Check claim structure
    for claim in claims:
        assert claim.claim_id.startswith("CLAIM_"), "Claim ID should start with CLAIM_"
        assert claim.claim_type in ["Proven", "Derived", "Modeled", "Conjectural", "Narrative"]
        assert 0.0 <= claim.confidence <= 1.0, "Confidence should be in [0, 1]"
        assert len(claim.statement) > 0, "Claim should have statement"
    
    # Check type distribution
    types = [c.claim_type for c in claims]
    print(f"  ✓ Claim types: {set(types)}")
    
    print("  ✓ Claim extractor tests passed")
    return True


def test_schema_validation():
    """Test claim schema structure."""
    print("Testing Schema Validation...")
    
    try:
        import yaml
    except ImportError:
        print("  ⚠ PyYAML not installed (pip install pyyaml)")
        return False
    
    schema_path = Path(__file__).parent.parent / "canon" / "claim_schema.yaml"
    
    if not schema_path.exists():
        print(f"  ⚠ Schema file not found: {schema_path}")
        return False
    
    with open(schema_path, 'r') as f:
        schema = yaml.safe_load(f)
    
    # Validate structure
    assert 'claim_types' in schema, "Schema should have claim_types"
    assert 'confidence_levels' in schema, "Schema should have confidence_levels"
    assert 'claim_metadata' in schema, "Schema should have claim_metadata"
    
    # Check claim types
    expected_types = ["Proven", "Derived", "Modeled", "Conjectural", "Narrative"]
    schema_types = list(schema['claim_types'].keys())
    
    for exp_type in expected_types:
        assert exp_type in schema_types, f"Schema should include {exp_type}"
    
    print(f"  ✓ Schema has {len(schema_types)} claim types")
    print("  ✓ Schema validation passed")
    return True


def run_all_tests():
    """Run all empirical tests."""
    print("=" * 60)
    print("Canon Ingestion Empirical Tests")
    print("=" * 60)
    print()
    
    results = []
    
    try:
        results.append(("Equation Parser", test_equation_parser()))
    except Exception as e:
        print(f"  ✗ Equation parser test failed: {e}")
        results.append(("Equation Parser", False))
    
    try:
        results.append(("Claim Extractor", test_claim_extractor()))
    except Exception as e:
        print(f"  ✗ Claim extractor test failed: {e}")
        results.append(("Claim Extractor", False))
    
    try:
        results.append(("Schema Validation", test_schema_validation()))
    except Exception as e:
        print(f"  ✗ Schema validation test failed: {e}")
        results.append(("Schema Validation", False))
    
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
