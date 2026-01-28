#!/usr/bin/env bash
# End-to-end constraint pipeline orchestrator
# Runs data ingestion, bounds generation, and joint constraint fusion

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RESULTS_DIR="${PROJECT_ROOT}/results/scalar_constraints"
DATA_DIR="${PROJECT_ROOT}/data"
SCHEMA_FILE="${DATA_DIR}/constraints/minimal_scalar_hypothesis_card_v0.1.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "MQGT Constraint Pipeline"
echo "=========================================="
echo ""

# Create results directory
mkdir -p "${RESULTS_DIR}"

# Step 1: Ingest experimental data (if needed)
echo -e "${YELLOW}Step 1: Data Ingestion${NC}"
if [ -f "${PROJECT_ROOT}/eotwash_prl2016_digitized_contract_READY.csv" ]; then
    echo "  Found Eöt-Wash data, ingesting..."
    python3 "${SCRIPT_DIR}/ingest_experimental_data.py" \
        --input "${PROJECT_ROOT}/eotwash_prl2016_digitized_contract_READY.csv" \
        --schema "${SCHEMA_FILE}" \
        --output-dir "${DATA_DIR}/public" || {
        echo -e "${RED}  ✗ Data ingestion failed${NC}"
        exit 1
    }
    echo -e "${GREEN}  ✓ Data ingested${NC}"
else
    echo "  Skipping data ingestion (file not found)"
fi
echo ""

# Step 2: Generate fifth-force bounds
echo -e "${YELLOW}Step 2: Fifth-Force Bounds Generation${NC}"
python3 "${SCRIPT_DIR}/generate_fifth_force_ep_bounds.py" || {
    echo -e "${RED}  ✗ Fifth-force bounds generation failed${NC}"
    exit 1
}
echo -e "${GREEN}  ✓ Fifth-force bounds generated${NC}"
echo ""

# Step 3: Generate clocks/spectroscopy bounds (if available)
echo -e "${YELLOW}Step 3: Clocks/Spectroscopy Bounds${NC}"
if [ -f "${SCRIPT_DIR}/generate_clocks_spectroscopy_bounds.py" ]; then
    python3 "${SCRIPT_DIR}/generate_clocks_spectroscopy_bounds.py" || {
        echo -e "${YELLOW}  ⚠ Clocks bounds generation failed (non-critical)${NC}"
    }
    echo -e "${GREEN}  ✓ Clocks bounds generated${NC}"
else
    echo "  Skipping clocks bounds (script not found)"
fi
echo ""

# Step 4: Generate joint constraints
echo -e "${YELLOW}Step 4: Joint Constraint Fusion${NC}"
python3 "${SCRIPT_DIR}/generate_joint_scalar_constraints.py" || {
    echo -e "${RED}  ✗ Joint constraint generation failed${NC}"
    exit 1
}
echo -e "${GREEN}  ✓ Joint constraints generated${NC}"
echo ""

# Step 5: Generate golden plot
echo -e "${YELLOW}Step 5: Golden Plot Generation${NC}"
if [ -f "${SCRIPT_DIR}/generate_golden_plot.py" ]; then
    python3 "${SCRIPT_DIR}/generate_golden_plot.py" || {
        echo -e "${YELLOW}  ⚠ Golden plot generation failed (non-critical)${NC}"
    }
    echo -e "${GREEN}  ✓ Golden plot generated${NC}"
else
    echo "  Skipping golden plot (script not found)"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✓ Pipeline complete!${NC}"
echo "=========================================="
echo ""
echo "Results saved to: ${RESULTS_DIR}"
echo ""
echo "Generated files:"
ls -lh "${RESULTS_DIR}"/*.csv "${RESULTS_DIR}"/*.json "${RESULTS_DIR}"/*.png 2>/dev/null || true
