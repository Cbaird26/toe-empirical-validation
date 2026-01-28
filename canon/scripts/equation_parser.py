#!/usr/bin/env python3
"""
Equation Parser for Zora Canon
Extracts LaTeX equations from documents and links them to claims.
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Equation:
    """Represents an extracted equation."""
    equation_id: str
    latex_formula: str
    context: str  # Surrounding text
    section: str
    page_number: Optional[int] = None
    line_range: Optional[Tuple[int, int]] = None
    related_claims: List[str] = None
    
    def __post_init__(self):
        if self.related_claims is None:
            self.related_claims = []


class EquationParser:
    """Parser for extracting equations from text."""
    
    # Patterns for common equation formats
    EQUATION_PATTERNS = [
        # LaTeX inline: $...$ or \(...\)
        (r'\$([^$]+)\$', 'inline'),
        (r'\\\(([^)]+)\\\)', 'inline'),
        
        # LaTeX display: $$...$$ or \[...\]
        (r'\$\$([^$]+)\$\$', 'display'),
        (r'\\\[([^\]]+)\\\]', 'display'),
        
        # Numbered equations: \begin{equation}...\end{equation}
        (r'\\begin\{equation\}(.*?)\\end\{equation\}', 'numbered'),
        
        # Simple math expressions (common patterns)
        (r'([A-Za-z_][A-Za-z0-9_]*\s*=\s*[^\.\n]+)', 'assignment'),
        
        # Fraction patterns: a/b or \frac{a}{b}
        (r'\\(frac\{([^}]+)\}\{([^}]+)\})', 'fraction'),
        
        # Subscript/superscript: a_b, a^b
        (r'([A-Za-z]_\{([^}]+)\})', 'subscript'),
        (r'([A-Za-z]\^\{([^}]+)\})', 'superscript'),
    ]
    
    def __init__(self):
        self.equations: List[Equation] = []
        self.equation_counter = 0
    
    def extract_equations(self, text: str, section: str, page_number: Optional[int] = None) -> List[Equation]:
        """
        Extract equations from text.
        
        Args:
            text: Text to parse
            section: Section name/identifier
            page_number: Optional page number
        
        Returns:
            List of extracted Equation objects
        """
        equations = []
        
        # Try each pattern
        for pattern, eq_type in self.EQUATION_PATTERNS:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                # Get formula from first capturing group, or full match if no group
                try:
                    formula = match.group(1).strip()
                except IndexError:
                    formula = match.group(0).strip()
                
                # Skip very short or invalid formulas
                if len(formula) < 3 or formula.count('{') != formula.count('}'):
                    continue
                
                # Get context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                # Generate equation ID
                self.equation_counter += 1
                section_clean = re.sub(r'[^A-Za-z0-9]', '_', section)
                eq_id = f"EQ_{section_clean}_{self.equation_counter}"
                
                # Find line numbers if possible
                line_start = text[:match.start()].count('\n') + 1
                line_end = text[:match.end()].count('\n') + 1
                
                equation = Equation(
                    equation_id=eq_id,
                    latex_formula=formula,
                    context=context,
                    section=section,
                    page_number=page_number,
                    line_range=(line_start, line_end) if line_start != line_end else None,
                    related_claims=[]
                )
                
                equations.append(equation)
        
        # Remove duplicates (same formula in same section)
        seen = set()
        unique_equations = []
        for eq in equations:
            key = (eq.latex_formula, eq.section)
            if key not in seen:
                seen.add(key)
                unique_equations.append(eq)
        
        self.equations.extend(unique_equations)
        return unique_equations
    
    def link_equation_to_claim(self, equation_id: str, claim_id: str):
        """Link an equation to a claim."""
        for eq in self.equations:
            if eq.equation_id == equation_id:
                if claim_id not in eq.related_claims:
                    eq.related_claims.append(claim_id)
                break
    
    def get_equations_for_section(self, section: str) -> List[Equation]:
        """Get all equations for a given section."""
        return [eq for eq in self.equations if eq.section == section]
    
    def export_json(self, output_path: Path):
        """Export equations to JSON."""
        data = {
            'equations': [asdict(eq) for eq in self.equations],
            'total_count': len(self.equations)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_latex_index(self, output_path: Path):
        """Export equations as LaTeX index for reference."""
        lines = ["% Zora Canon Equation Index", "% Generated automatically\n"]
        
        for eq in self.equations:
            lines.append(f"% {eq.equation_id} ({eq.section})")
            lines.append(f"\\begin{{equation}}")
            lines.append(f"{eq.latex_formula}")
            lines.append(f"\\end{{equation}}")
            lines.append(f"% Context: {eq.context[:100]}...\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


if __name__ == '__main__':
    # Test the parser
    parser = EquationParser()
    
    test_text = """
    The Lagrangian density is given by:
    $$L = L_{GR} + L_{SM} + L_{\Phi_c} + L_E$$
    
    Where the scalar field coupling is:
    $\\kappa_{cH} v_c = \\theta_{hc} (m_h^2 - m_c^2)$
    
    And the force range parameter is:
    \\begin{equation}
    \\lambda = \\frac{\\hbar c}{m_c}
    \\end{equation}
    """
    
    equations = parser.extract_equations(test_text, "Lagrangian Formulation", page_number=1)
    
    print(f"Extracted {len(equations)} equations:")
    for eq in equations:
        print(f"  {eq.equation_id}: {eq.latex_formula[:50]}...")
