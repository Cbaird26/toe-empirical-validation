#!/usr/bin/env python3
"""
Experimental Data Ingestion Module
Loads constraint curves and validates against hypothesis card schema.
"""

import argparse
import csv
import hashlib
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


def sha256_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_hypothesis_card(schema_path: Path) -> Dict:
    """Load hypothesis card YAML."""
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


def validate_csv_format(csv_path: Path, expected_columns: List[str]) -> bool:
    """Validate CSV has expected columns."""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        actual_columns = reader.fieldnames
        
        if not actual_columns:
            return False
        
        # Check all expected columns are present
        for col in expected_columns:
            if col not in actual_columns:
                print(f"Warning: Missing column '{col}' in {csv_path.name}")
                return False
        
        return True


def load_eotwash_curve(csv_path: Path) -> List[Dict]:
    """Load Eöt-Wash constraint curve from CSV."""
    expected_columns = ['lambda_m', 'alpha_max']
    
    if not validate_csv_format(csv_path, expected_columns):
        raise ValueError(f"Invalid CSV format for {csv_path.name}")
    
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lambda_m = float(row['lambda_m'])
                alpha_max = float(row['alpha_max'])
                
                # Validate domain (should be positive)
                if lambda_m <= 0 or alpha_max <= 0:
                    continue
                
                data.append({
                    'lambda_m': lambda_m,
                    'alpha_max': alpha_max,
                    'source_id': row.get('source_id', 'unknown'),
                    'ref': row.get('ref', '')
                })
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid row: {e}")
                continue
    
    return data


def validate_against_schema(data: List[Dict], schema: Dict) -> Dict:
    """Validate data against hypothesis card schema."""
    channel = schema.get('channels', {}).get('fifth_force', {})
    
    # Check input format matches
    expected_format = channel.get('input_format', 'alpha_max vs lambda_m')
    
    # Validate domain
    domain_validation = channel.get('domain_validation', 'Real-only')
    
    validated_data = []
    for point in data:
        lambda_m = point['lambda_m']
        alpha_max = point['alpha_max']
        
        # Domain validation: ensure real, positive values
        if lambda_m > 0 and alpha_max > 0:
            validated_data.append(point)
        else:
            print(f"Warning: Skipping invalid domain point: λ={lambda_m}, α={alpha_max}")
    
    return validated_data


def generate_provenance_metadata(csv_path: Path, data: List[Dict]) -> Dict:
    """Generate provenance metadata for ingested data."""
    file_hash = sha256_file(csv_path)
    
    # Extract source info from first row if available
    source_id = data[0].get('source_id', 'unknown') if data else 'unknown'
    ref = data[0].get('ref', '') if data else ''
    
    metadata = {
        'dataset_id': file_hash[:16],
        'filename': csv_path.name,
        'sha256': file_hash,
        'ingested_at': datetime.now(timezone.utc).isoformat(),
        'source_id': source_id,
        'reference': ref,
        'data_points': len(data),
        'lambda_range': {
            'min': min(p['lambda_m'] for p in data) if data else None,
            'max': max(p['lambda_m'] for p in data) if data else None
        },
        'alpha_range': {
            'min': min(p['alpha_max'] for p in data) if data else None,
            'max': max(p['alpha_max'] for p in data) if data else None
        }
    }
    
    return metadata


def register_in_mqgt_data_public(data: List[Dict], metadata: Dict, output_dir: Path, source_csv_path: Path):
    """Register data in mqgt-data-public structure."""
    # Create canonical directory
    canonical_dir = output_dir / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    
    # Save canonical CSV
    canonical_file = canonical_dir / f"{metadata['dataset_id']}_canonical.csv"
    with open(canonical_file, 'w', newline='') as f:
        fieldnames = ['lambda_m', 'alpha_max', 'source_id', 'ref']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    # Save provenance JSON
    provenance_file = output_dir / "provenance" / f"{metadata['dataset_id']}_provenance.json"
    provenance_file.parent.mkdir(parents=True, exist_ok=True)
    
    provenance_data = {
        **metadata,
        'canonical_file': str(canonical_file.relative_to(output_dir)),
        'format': 'CSV',
        'columns': ['lambda_m', 'alpha_max', 'source_id', 'ref']
    }
    
    with open(provenance_file, 'w') as f:
        json.dump(provenance_data, f, indent=2)
    
    # Update manifest
    manifest_file = output_dir / "manifest.json"
    if manifest_file.exists():
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = {
            'version': '0.1',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'datasets': []
        }
    
    manifest['datasets'].append({
        'dataset_id': metadata['dataset_id'],
        'filename': source_csv_path.name,
        'sha256': metadata['sha256'],
        'canonical_file': str(canonical_file.relative_to(output_dir)),
        'provenance_file': str(provenance_file.relative_to(output_dir))
    })
    manifest['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return canonical_file, provenance_file


def main():
    parser = argparse.ArgumentParser(description="Ingest experimental constraint data")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--schema", required=True, help="Path to hypothesis card YAML")
    parser.add_argument("--output-dir", required=True, help="Output directory (mqgt-data-public structure)")
    
    args = parser.parse_args()
    
    csv_path = Path(args.input).expanduser().resolve()
    schema_path = Path(args.schema).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    print(f"Loading hypothesis card: {schema_path}")
    schema = load_hypothesis_card(schema_path)
    
    print(f"Loading constraint curve: {csv_path}")
    data = load_eotwash_curve(csv_path)
    print(f"  Loaded {len(data)} data points")
    
    print("Validating against schema...")
    validated_data = validate_against_schema(data, schema)
    print(f"  Validated {len(validated_data)} data points")
    
    print("Generating provenance metadata...")
    metadata = generate_provenance_metadata(csv_path, validated_data)
    
    print("Registering in mqgt-data-public structure...")
    canonical_file, provenance_file = register_in_mqgt_data_public(
        validated_data, metadata, output_dir, csv_path
    )
    
    print(f"\n✓ Ingested dataset: {metadata['dataset_id']}")
    print(f"  Canonical file: {canonical_file}")
    print(f"  Provenance file: {provenance_file}")
    print(f"  Data points: {metadata['data_points']}")
    print(f"  λ range: {metadata['lambda_range']['min']:.2e} - {metadata['lambda_range']['max']:.2e} m")
    print(f"  α range: {metadata['alpha_range']['min']:.2e} - {metadata['alpha_range']['max']:.2e}")


if __name__ == '__main__':
    main()
