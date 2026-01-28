#!/usr/bin/env python3
"""
Zora Canon Ingestion Script
Main script for extracting, structuring, and versioning ToE documents.
"""

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

# Optional imports with fallbacks
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# Import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from equation_parser import EquationParser
from claim_extractor import ClaimExtractor


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def normalize_text(text: str) -> str:
    """Normalize text: fix line endings, remove hyphenation, collapse whitespace."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Remove hyphenation at line breaks: "exam-\nple" -> "example"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    
    # Collapse repeated spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)
    
    # Collapse 3+ newlines into 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()


def extract_docx_text(path: Path) -> Tuple[str, Optional[int]]:
    """Extract text from DOCX file."""
    if not DOCX_AVAILABLE:
        raise RuntimeError("python-docx not installed. Install with: pip install python-docx")
    
    doc = docx.Document(str(path))
    
    # Extract text from paragraphs
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    
    text = "\n\n".join(paragraphs)
    
    # Try to get page count (approximate)
    page_count = None
    try:
        # This is approximate - DOCX doesn't have fixed page count
        # Estimate based on paragraph count
        page_count = len(paragraphs) // 20  # Rough estimate
    except:
        pass
    
    return normalize_text(text), page_count


def extract_pdf_text(path: Path) -> Tuple[str, Optional[int]]:
    """Extract text from PDF file."""
    # Prefer PyMuPDF if available
    if PDF_AVAILABLE:
        doc = fitz.open(path)
        pages = doc.page_count
        parts = []
        
        for i in range(pages):
            page = doc.load_page(i)
            parts.append(page.get_text("text"))
        
        doc.close()
        return normalize_text("\n\n".join(parts)), pages
    
    # Fallback to pypdf
    if PYPDF_AVAILABLE:
        reader = PdfReader(str(path))
        pages = len(reader.pages)
        parts = []
        
        for page in reader.pages:
            text = page.extract_text() or ""
            parts.append(text)
        
        return normalize_text("\n\n".join(parts)), pages
    
    raise RuntimeError(
        "No PDF extractor available. Install one of: "
        "pip install pymupdf  OR  pip install pypdf"
    )


def extract_text(path: Path) -> Tuple[str, Optional[int], str]:
    """Extract text from file, detecting format."""
    ext = path.suffix.lower()
    
    if ext == ".docx":
        text, pages = extract_docx_text(path)
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif ext == ".pdf":
        text, pages = extract_pdf_text(path)
        content_type = "application/pdf"
    elif ext == ".txt":
        text = normalize_text(path.read_text(encoding="utf-8", errors="replace"))
        pages = None
        content_type = "text/plain"
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    return text, pages, content_type


def parse_sections(text: str) -> list:
    """Parse document into sections based on headers."""
    sections = []
    
    # Pattern for section headers (various formats)
    # Numbered: "1. Introduction", "1.1 Background"
    # Unnumbered: "Introduction", "## Background"
    header_patterns = [
        r'^(#{1,6})\s+(.+)$',  # Markdown headers
        r'^(\d+(?:\.\d+)*)\s+(.+)$',  # Numbered sections
        r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headers
    ]
    
    lines = text.split('\n')
    current_section = {
        'title': 'Introduction',
        'text': '',
        'start_line': 0
    }
    
    for i, line in enumerate(lines):
        is_header = False
        
        for pattern in header_patterns:
            match = re.match(pattern, line.strip())
            if match:
                # Save previous section
                if current_section['text'].strip():
                    current_section['end_line'] = i
                    sections.append(current_section)
                
                # Start new section
                title = match.group(-1).strip()  # Last group is title
                current_section = {
                    'title': title,
                    'text': '',
                    'start_line': i
                }
                is_header = True
                break
        
        if not is_header:
            current_section['text'] += line + '\n'
    
    # Add final section
    if current_section['text'].strip():
        current_section['end_line'] = len(lines)
        sections.append(current_section)
    
    return sections


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into Zora Canon")
    parser.add_argument("--input", required=True, help="Input file or directory")
    parser.add_argument("--output-dir", required=True, help="Output directory for canon")
    parser.add_argument("--schema", help="Path to claim schema YAML")
    parser.add_argument("--skip-existing", action="store_true", 
                       help="Skip files that already exist in manifest")
    
    args = parser.parse_args()
    
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup subdirectories
    sources_dir = output_dir / "sources"
    extracted_dir = output_dir / "extracted"
    canon_dir = output_dir / "canon"
    manifests_dir = output_dir / "manifests"
    
    for d in [sources_dir, extracted_dir, canon_dir / "claims", 
              canon_dir / "equations", canon_dir / "sections", manifests_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Load existing manifest if it exists
    manifest_path = manifests_dir / "canon_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        existing_hashes = {doc['sha256'] for doc in manifest.get('documents', [])}
    else:
        manifest = {
            'version': '0.1',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'documents': []
        }
        existing_hashes = set()
    
    # Initialize extractors
    schema_path = Path(args.schema) if args.schema else output_dir.parent / "claim_schema.yaml"
    claim_extractor = ClaimExtractor(schema_path if schema_path.exists() else None)
    equation_parser = EquationParser()
    
    # Process input files
    if input_path.is_file():
        files_to_process = [input_path]
    else:
        files_to_process = list(input_path.rglob("*"))
        files_to_process = [f for f in files_to_process 
                           if f.is_file() and f.suffix.lower() in {'.pdf', '.docx', '.txt'}]
    
    processed_count = 0
    
    for file_path in files_to_process:
        print(f"Processing: {file_path.name}")
        
        # Compute hash
        file_hash = sha256_file(file_path)
        
        # Skip if already processed
        if args.skip_existing and file_hash in existing_hashes:
            print(f"  Skipping (already in manifest)")
            continue
        
        try:
            # Extract text
            text, pages, content_type = extract_text(file_path)
            
            # Copy to sources
            sources_file = sources_dir / file_path.name
            if not sources_file.exists():
                import shutil
                shutil.copy2(file_path, sources_file)
            
            # Parse sections
            sections = parse_sections(text)
            
            # Process each section
            doc_id = file_hash[:16]
            doc_claims = []
            doc_equations = []
            
            for section in sections:
                section_title = section['title']
                section_text = section['text']
                
                # Extract equations
                eqs = equation_parser.extract_equations(
                    section_text, section_title, pages
                )
                doc_equations.extend(eqs)
                
                # Extract claims
                claims = claim_extractor.extract_claims(
                    section_text, section_title, file_path.name, pages
                )
                doc_claims.extend(claims)
            
            # Save extracted data
            extracted_data = {
                'doc_id': doc_id,
                'filename': file_path.name,
                'sha256': file_hash,
                'pages': pages,
                'content_type': content_type,
                'sections': [
                    {
                        'title': s['title'],
                        'text': s['text'],
                        'start_line': s['start_line'],
                        'end_line': s.get('end_line', s['start_line'])
                    }
                    for s in sections
                ],
                'extracted_at': datetime.now(timezone.utc).isoformat()
            }
            
            extracted_file = extracted_dir / f"{doc_id}.json"
            with open(extracted_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            # Save claims
            claims_file = canon_dir / "claims" / f"{doc_id}_claims.json"
            claim_extractor.export_json(claims_file)
            
            # Save equations
            equations_file = canon_dir / "equations" / f"{doc_id}_equations.json"
            equation_parser.export_json(equations_file)
            
            # Save sections
            sections_file = canon_dir / "sections" / f"{doc_id}_sections.json"
            with open(sections_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data['sections'], f, indent=2, ensure_ascii=False)
            
            # Update manifest
            doc_meta = {
                'doc_id': doc_id,
                'filename': file_path.name,
                'relpath': str(file_path.relative_to(input_path.parent)) if input_path.is_dir() else file_path.name,
                'sha256': file_hash,
                'bytes': file_path.stat().st_size,
                'mtime_utc': datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc).isoformat(),
                'pages': pages,
                'content_type': content_type,
                'claims_count': len(doc_claims),
                'equations_count': len(doc_equations),
                'sections_count': len(sections)
            }
            
            manifest['documents'].append(doc_meta)
            processed_count += 1
            
            print(f"  ✓ Extracted {len(sections)} sections, {len(doc_claims)} claims, {len(doc_equations)} equations")
        
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")
            continue
    
    # Save updated manifest
    manifest['updated_at'] = datetime.now(timezone.utc).isoformat()
    manifest['total_documents'] = len(manifest['documents'])
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Processed {processed_count} documents")
    print(f"✓ Manifest saved to: {manifest_path}")


if __name__ == '__main__':
    main()
