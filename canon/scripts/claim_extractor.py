#!/usr/bin/env python3
"""
Claim Extractor for Zora Canon
Identifies and classifies claims from extracted text using NLP patterns.
"""

import re
import json
import yaml
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class Claim:
    """Represents a single claim."""
    claim_id: str
    statement: str
    claim_type: str  # Proven/Derived/Modeled/Conjectural/Narrative
    confidence: float
    source_document: str
    source_section: str
    page_number: Optional[int] = None
    line_range: Optional[Tuple[int, int]] = None
    equation_refs: List[str] = field(default_factory=list)
    scriptural_mapping: Optional[str] = None
    citation: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None


class ClaimExtractor:
    """Extracts and classifies claims from text."""
    
    # Patterns for identifying claims
    CLAIM_PATTERNS = {
        'proven': [
            r'(?:proven|demonstrated|established|verified|confirmed)',
            r'(?:theorem|proof|derivation)',
            r'(?:experimentally\s+verified|empirically\s+confirmed)',
        ],
        'derived': [
            r'(?:derived|follows|implies|consequence|predicts)',
            r'(?:from\s+equation|from\s+the\s+lagrangian)',
            r'(?:theoretical\s+prediction)',
        ],
        'modeled': [
            r'(?:model|simulation|computation|numerical)',
            r'(?:constraint|bound|limit)',
            r'(?:parameter\s+space|exclusion\s+region)',
        ],
        'conjectural': [
            r'(?:hypothesis|proposal|suggests|may\s+be|possibly)',
            r'(?:speculation|conjecture|theoretical\s+extension)',
        ],
        'narrative': [
            r'(?:interpretation|meaning|significance|implication)',
            r'(?:ethical|metaphysical|consciousness|awareness)',
            r'(?:scriptural|dharma|emptiness|interdependence)',
        ],
    }
    
    # Confidence keywords
    CONFIDENCE_KEYWORDS = {
        'certain': ['proven', 'demonstrated', 'established', 'verified'],
        'very_high': ['strongly', 'clearly', 'definitively'],
        'high': ['likely', 'probably', 'well-supported'],
        'moderate': ['may', 'could', 'possibly', 'suggests'],
        'low': ['speculation', 'conjecture', 'hypothesis'],
        'narrative': ['interpretation', 'meaning', 'significance'],
    }
    
    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize with claim schema."""
        self.schema = None
        if schema_path and schema_path.exists():
            with open(schema_path, 'r') as f:
                self.schema = yaml.safe_load(f)
        
        self.claims: List[Claim] = []
        self.claim_counter = 0
    
    def extract_claims(self, text: str, section: str, source_doc: str, 
                      page_number: Optional[int] = None) -> List[Claim]:
        """
        Extract claims from text.
        
        Args:
            text: Text to analyze
            section: Section name/identifier
            source_doc: Source document name
            page_number: Optional page number
        
        Returns:
            List of extracted Claim objects
        """
        claims = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            # Classify claim type
            claim_type, confidence = self._classify_claim(sentence)
            
            # Skip if confidence is too low (likely not a claim)
            if confidence < 0.2:
                continue
            
            # Generate claim ID
            self.claim_counter += 1
            section_clean = re.sub(r'[^A-Za-z0-9]', '_', section)
            claim_id = f"CLAIM_{section_clean}_{self.claim_counter:04d}"
            
            # Extract tags
            tags = self._extract_tags(sentence)
            
            # Find equation references
            equation_refs = self._find_equation_refs(sentence)
            
            # Find scriptural mappings
            scriptural_mapping = self._find_scriptural_mapping(sentence)
            
            # Find line numbers
            line_start = text.find(sentence)
            if line_start >= 0:
                line_num = text[:line_start].count('\n') + 1
                line_range = (line_num, line_num)
            else:
                line_range = None
            
            claim = Claim(
                claim_id=claim_id,
                statement=sentence,
                claim_type=claim_type,
                confidence=confidence,
                source_document=source_doc,
                source_section=section,
                page_number=page_number,
                line_range=line_range,
                equation_refs=equation_refs,
                scriptural_mapping=scriptural_mapping,
                tags=tags
            )
            
            claims.append(claim)
        
        self.claims.extend(claims)
        return claims
    
    def _classify_claim(self, text: str) -> Tuple[str, float]:
        """Classify claim type and confidence."""
        text_lower = text.lower()
        
        # Check each claim type pattern
        scores = {}
        for claim_type, patterns in self.CLAIM_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            scores[claim_type] = score
        
        # Determine claim type
        if max(scores.values()) == 0:
            # Default to derived if no pattern matches
            claim_type = 'derived'
            confidence = 0.5
        else:
            claim_type = max(scores, key=scores.get)
            
            # Map to schema claim types
            type_mapping = {
                'proven': 'Proven',
                'derived': 'Derived',
                'modeled': 'Modeled',
                'conjectural': 'Conjectural',
                'narrative': 'Narrative',
            }
            claim_type = type_mapping.get(claim_type, 'Derived')
            
            # Determine confidence
            confidence = self._estimate_confidence(text_lower, claim_type)
        
        return claim_type, confidence
    
    def _estimate_confidence(self, text: str, claim_type: str) -> float:
        """Estimate confidence level from text."""
        # Base confidence by type
        base_confidence = {
            'Proven': 0.95,
            'Derived': 0.75,
            'Modeled': 0.60,
            'Conjectural': 0.40,
            'Narrative': 0.20,
        }.get(claim_type, 0.50)
        
        # Adjust based on confidence keywords
        for level, keywords in self.CONFIDENCE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    adjustments = {
                        'certain': 0.1,
                        'very_high': 0.05,
                        'high': 0.0,
                        'moderate': -0.1,
                        'low': -0.2,
                        'narrative': -0.1,
                    }
                    base_confidence += adjustments.get(level, 0)
                    break
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, base_confidence))
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text."""
        tags = []
        
        tag_keywords = {
            'physics': ['field', 'lagrangian', 'hamiltonian', 'quantum', 'particle'],
            'mathematics': ['equation', 'derivation', 'theorem', 'proof', 'integral'],
            'consciousness': ['awareness', 'consciousness', 'mind', 'experience'],
            'ethics': ['ethical', 'moral', 'value', 'constraint'],
            'scalar_field': ['scalar', 'phi', 'φ', 'field'],
            'higgs_portal': ['higgs', 'portal', 'mixing', 'coupling'],
            'fifth_force': ['fifth force', 'yukawa', 'deviation', 'gravity'],
            'collider': ['collider', 'lhc', 'cern', 'atlas', 'cms'],
        }
        
        text_lower = text.lower()
        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def _find_equation_refs(self, text: str) -> List[str]:
        """Find references to equations in text."""
        refs = []
        
        # Pattern: "Equation (5.1)" or "Eq. 5.1" or "EQ_5_1"
        patterns = [
            r'(?:equation|eq\.?)\s*[\(]?\s*(\d+(?:\.\d+)?)',
            r'EQ[_\-](\d+(?:[_\-]\d+)?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref = match.group(1)
                # Normalize format
                ref_normalized = f"EQ_{ref.replace('.', '_')}"
                refs.append(ref_normalized)
        
        return list(set(refs))  # Remove duplicates
    
    def _find_scriptural_mapping(self, text: str) -> Optional[str]:
        """Find scriptural/ethical mappings."""
        mappings = {
            'dharma': ['dharma', 'buddha', 'teaching', 'sutra'],
            'ethics': ['ethical', 'moral', 'right', 'wrong', 'constraint'],
            'consciousness': ['awareness', 'consciousness', 'mind', 'experience'],
            'emptiness': ['emptiness', 'sunyata', 'void', 'empty'],
            'interdependence': ['interdependence', 'dependent', 'arising', 'pratityasamutpada'],
        }
        
        text_lower = text.lower()
        for mapping, keywords in mappings.items():
            if any(keyword in text_lower for keyword in keywords):
                return mapping
        
        return None
    
    def export_json(self, output_path: Path):
        """Export claims to JSON."""
        data = {
            'claims': [asdict(claim) for claim in self.claims],
            'total_count': len(self.claims),
            'by_type': self._count_by_type()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count claims by type."""
        counts = {}
        for claim in self.claims:
            counts[claim.claim_type] = counts.get(claim.claim_type, 0) + 1
        return counts


if __name__ == '__main__':
    # Test the extractor
    extractor = ClaimExtractor()
    
    test_text = """
    The scalar field Φ_c couples to the Standard Model via Higgs-portal mixing.
    This coupling generates a Yukawa-type fifth force that deviates from inverse-square gravity.
    Experimental constraints from Eöt-Wash torsion balance tests limit the coupling strength.
    The theoretical prediction suggests that the coupling may be observable in future experiments.
    This has profound implications for our understanding of consciousness and awareness.
    """
    
    claims = extractor.extract_claims(test_text, "Scalar Field Coupling", "test_doc.docx")
    
    print(f"Extracted {len(claims)} claims:")
    for claim in claims:
        print(f"  {claim.claim_id}: [{claim.claim_type}] {claim.statement[:60]}...")
