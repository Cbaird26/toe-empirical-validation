# Usage Examples

## Quick Examples

### Example 1: Run Full Validation Pipeline

```bash
# Activate virtual environment
source .venv/bin/activate

# Run complete validation
make constraint-pipeline

# Compute ToE predictions and validate
python experiments/compute_toe_predictions.py

# Run full validation suite
python experiments/run_empirical_validation.py
```

**Output:**
- Constraint plots in `results/scalar_constraints/`
- Validation results in `results/empirical_validation/`
- JSON results files with statistics

### Example 2: Extract Claims from ToE Document

```bash
# Ingest ToE document into canon
python canon/scripts/canon_ingest.py \
    --input "docs/papers/A Completed Theory of Everything --C.M. Baird., et al (2026).docx" \
    --output-dir ./canon \
    --schema ./canon/claim_schema.yaml

# View extracted claims
cat canon/canon/claims/*.json | jq '.statement' | head -10
```

### Example 3: Query Zora Brain API

```bash
# Start Zora Brain backend (in separate terminal)
cd zora-brain-backend
python zora_brain_api.py

# Query the API
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the unified Lagrangian?",
    "max_citations": 5
  }'
```

### Example 4: Run Sensor Experiment

```bash
# Start telemetry server (in separate terminal)
cd telemetry
uvicorn telemetry_server:app --host 0.0.0.0 --port 8000

# Run Phyphox autonomous loop
python experiments/phyphox_autonomous_loop.py \
    --phyphox-url http://192.168.1.5:8080 \
    --duration 3600 \
    --output-dir ./logs

# View dashboard
streamlit run telemetry_dashboard.py
```

### Example 5: Generate Custom Constraint Plot

```python
# Custom constraint analysis
import pandas as pd
import matplotlib.pyplot as plt
from scripts.generate_golden_plot import compute_predicted_alpha_band

# Load bounds
bounds_df = pd.read_csv('results/scalar_constraints/joint_bounds.csv')

# Compute predictions
lambda_values = bounds_df['lambda_m'].values
alpha_min, alpha_max, alpha_median = compute_predicted_alpha_band(
    lambda_values, 
    theta_range=(1e-4, 0.1)
)

# Plot
plt.loglog(lambda_values, alpha_median, label='ToE Prediction')
plt.loglog(lambda_values, bounds_df['alpha_max'], label='Experimental Bound')
plt.xlabel('λ (m)')
plt.ylabel('α')
plt.legend()
plt.savefig('custom_plot.png')
```

## Advanced Examples

### Example 6: Bayesian Parameter Estimation

```python
# Bayesian analysis (requires additional packages)
import numpy as np
import pymc3 as pm

# Define likelihood
with pm.Model() as model:
    theta = pm.Uniform('theta', lower=1e-4, upper=0.1)
    alpha_pred = compute_predicted_alpha(theta, lambda_values)
    
    # Likelihood
    likelihood = pm.Normal('likelihood', 
                          mu=alpha_pred, 
                          sigma=experimental_errors,
                          observed=experimental_data)
    
    # Sample
    trace = pm.sample(1000)
    
# Analyze results
pm.summary(trace)
```

### Example 7: Custom Claim Extraction

```python
from canon.scripts.claim_extractor import ClaimExtractor
from canon.scripts.equation_parser import EquationParser

# Initialize extractors
claim_extractor = ClaimExtractor('canon/claim_schema.yaml')
equation_parser = EquationParser()

# Extract from custom text
text = """
The unified Lagrangian integrates General Relativity with the Standard Model.
The consciousness field Φc mediates a fifth force through Higgs mixing.
"""

claims = claim_extractor.extract_claims(text, "Custom Section", "custom.txt")
equations = equation_parser.extract_equations(text, "Custom Section")

print(f"Found {len(claims)} claims and {len(equations)} equations")
```

### Example 8: Batch Processing Multiple Documents

```python
from pathlib import Path
from canon.scripts.canon_ingest import main as ingest_doc

# Process multiple documents
documents = [
    "docs/papers/A Completed Theory of Everything --C.M. Baird., et al (2026).docx",
    "docs/papers/other_paper.pdf",
]

for doc in documents:
    print(f"Processing {doc}...")
    # Run ingestion (would need to adapt main function)
    # ingest_doc(doc)
```

## Integration Examples

### Example 9: Integrate with Other MQGT Repos

```bash
# Clone related repositories
git clone https://github.com/Cbaird26/mqgt-fifth-force.git
git clone https://github.com/Cbaird26/mqgt-collider.git

# Use their constraint data
cp mqgt-fifth-force/data/bounds.csv data/external/
cp mqgt-collider/data/higgs_bounds.csv data/external/

# Run joint analysis
python scripts/generate_joint_scalar_constraints.py
```

### Example 10: Export Results for Publication

```python
import json
import pandas as pd

# Load validation results
with open('results/empirical_validation/toe_validation_results.json') as f:
    results = json.load(f)

# Create publication table
df = pd.DataFrame({
    'Data Points': [results['summary']['total_data_points']],
    'Violations': [results['summary']['violations']],
    'Validations': [results['summary']['validations']],
    'Validation Rate': [f"{results['summary']['validation_rate']*100:.1f}%"]
})

# Export to LaTeX table
print(df.to_latex(index=False))
```

## Jupyter Notebook Examples

See `examples/` directory for Jupyter notebooks:
- `constraint_analysis.ipynb` - Interactive constraint analysis
- `prediction_computation.ipynb` - ToE prediction exploration
- `canon_exploration.ipynb` - Canon knowledge base queries

## Command-Line Tools

### Available Commands

```bash
# Constraint pipeline
make constraint-pipeline

# Individual components
python scripts/generate_fifth_force_ep_bounds.py
python scripts/generate_clocks_spectroscopy_bounds.py
python scripts/generate_joint_scalar_constraints.py
python scripts/generate_golden_plot.py

# Validation
python experiments/compute_toe_predictions.py
python experiments/run_empirical_validation.py

# Canon ingestion
python canon/scripts/canon_ingest.py --help

# Paper compilation
cd paper && pdflatex main.tex
```

## API Examples

### Zora Brain API

```python
import requests

# Query Zora Brain
response = requests.post(
    'http://localhost:8001/query',
    json={
        'question': 'What are the empirical predictions?',
        'max_citations': 5,
        'require_citations': True
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Citations: {len(result['citations'])}")
```

### Telemetry API

```python
import requests
import time

# Send sensor data
for i in range(10):
    requests.post(
        'http://localhost:8000/ingest',
        json={
            'sensor_id': 'magnetometer_001',
            'metric': 'field_strength',
            'value': 50.0 + i * 0.1,
            'unit': 'μT'
        }
    )
    time.sleep(0.1)

# Query data
response = requests.get('http://localhost:8000/query?sensor_id=magnetometer_001')
print(response.json())
```

## More Examples

For more examples, see:
- `tests/` - Test files with usage examples
- `experiments/` - Experimental protocols
- `scripts/` - Individual script documentation

---

**Last Updated:** January 28, 2026
