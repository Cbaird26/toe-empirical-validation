# Zora Canon

Structured, versioned, searchable knowledge base for the Theory of Everything corpus.

## Structure

```
canon/
├── sources/          # Original PDFs/DOCX files
├── extracted/        # Parsed JSON/structured data
├── canon/            # Final canonical format
│   ├── claims/       # Individual claim records
│   ├── equations/    # Extracted equations (LaTeX)
│   └── sections/     # Document structure
├── scripts/          # Ingestion scripts
└── manifests/        # Version tracking
```

## Usage

### Ingest Documents

```bash
# Single file
python scripts/canon_ingest.py \
  --input "A Theory of Everything - Updated - C.M. Baird., Et al (2026).docx" \
  --output-dir ./canon \
  --schema ./claim_schema.yaml

# Directory of files
python scripts/canon_ingest.py \
  --input ./sources \
  --output-dir ./canon \
  --skip-existing
```

### Claim Schema

Claims are classified into types:
- **Proven**: Empirically verified or mathematically proven
- **Derived**: Logically derived from proven statements
- **Modeled**: Predictions from computational models
- **Conjectural**: Theoretical hypotheses not yet validated
- **Narrative**: Interpretive, ethical, or metaphysical statements

See `claim_schema.yaml` for full taxonomy.

## Version Control

The canon uses SHA256 hashing for version tracking. Each document gets a unique `doc_id` based on its hash. The manifest (`manifests/canon_manifest.json`) tracks all ingested documents with metadata.

To create a version tag:
```bash
git tag -a v0.1-canon-seed -m "Initial canon seed"
```

## Dependencies

```bash
pip install python-docx pymupdf pyyaml
```

## Output Format

### Claims JSON
```json
{
  "claims": [
    {
      "claim_id": "CLAIM_Section_0001",
      "statement": "...",
      "claim_type": "Derived",
      "confidence": 0.75,
      "source_document": "...",
      "source_section": "...",
      "equation_refs": ["EQ_5_1"],
      "tags": ["physics", "scalar_field"]
    }
  ]
}
```

### Equations JSON
```json
{
  "equations": [
    {
      "equation_id": "EQ_Section_1",
      "latex_formula": "L = L_{GR} + L_{SM}",
      "context": "...",
      "section": "...",
      "related_claims": ["CLAIM_Section_0001"]
    }
  ]
}
```
