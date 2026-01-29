# Installation Guide

## Quick Start

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Git** (for cloning repository)
- **LaTeX** (optional, for paper compilation)

### Step 1: Clone Repository

```bash
git clone https://github.com/Cbaird26/toe-empirical-validation.git
cd toe-empirical-validation
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Run validation tests
python experiments/run_empirical_validation.py

# Or run constraint pipeline
make constraint-pipeline
```

## Detailed Installation

### Python Dependencies

All Python dependencies are listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Key packages:**
- `numpy` - Numerical computations
- `pandas` - Data analysis
- `matplotlib` - Plotting
- `scipy` - Scientific computing
- `pyyaml` - Configuration files
- `fastapi` - API framework (for Zora Brain)
- `python-docx` - DOCX processing
- `pymupdf` - PDF processing

### LaTeX (Optional)

For compiling the paper:

**macOS:**
```bash
brew install --cask mactex
```

**Linux:**
```bash
sudo apt-get install texlive-full
```

**Windows:**
- Install MiKTeX or TeX Live

**Or use Overleaf:**
- Upload `paper/` directory to https://www.overleaf.com

### Git LFS (For Large Files)

If cloning large files:

```bash
# Install Git LFS
# macOS:
brew install git-lfs
# Linux:
sudo apt-get install git-lfs
# Windows: Download from https://git-lfs.github.com/

# Initialize Git LFS
git lfs install

# Pull large files
git lfs pull
```

### Ollama (Optional, for Zora Brain)

For Zora Brain backend:

```bash
# Install Ollama
# macOS/Linux: https://ollama.ai
# Or: brew install ollama

# Pull model
ollama pull gpt-oss:20b
```

## Platform-Specific Notes

### macOS

- Python 3.8+ comes with macOS
- Use Homebrew for LaTeX: `brew install --cask mactex`
- MPS (Metal) acceleration available for PyTorch

### Linux

- Install Python: `sudo apt-get install python3 python3-pip`
- Install LaTeX: `sudo apt-get install texlive-full`
- May need: `sudo apt-get install python3-dev`

### Windows

- Install Python from python.org
- Use MiKTeX or TeX Live for LaTeX
- Use Git Bash or WSL for shell commands

## Docker Installation (Alternative)

```bash
# Build Docker image
docker build -t mqgt-validation .

# Run validation
docker run -v $(pwd)/results:/app/results mqgt-validation make constraint-pipeline
```

## Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

### LaTeX Compilation Errors

```bash
# Check LaTeX installation
pdflatex --version

# Install missing packages
# macOS: tlmgr install <package>
# Linux: sudo apt-get install texlive-<package>
```

### Git LFS Issues

```bash
# Reinitialize Git LFS
git lfs install

# Track large files
git lfs track "*.pdf"
git lfs track "*.png"

# Pull large files
git lfs pull
```

### Permission Errors

```bash
# Fix permissions (macOS/Linux)
chmod +x scripts/*.sh
chmod +x experiments/*.py
```

## Verification

After installation, verify everything works:

```bash
# Test Python installation
python --version
python -c "import numpy, pandas, matplotlib; print('✓ Core packages OK')"

# Test constraint pipeline
make constraint-pipeline

# Test validation
python experiments/run_empirical_validation.py

# Test paper compilation (if LaTeX installed)
cd paper && pdflatex main.tex
```

## Next Steps

After installation:

1. **Run Validation:** `make constraint-pipeline`
2. **View Results:** Check `results/` directory
3. **Read Paper:** Open `paper/main.pdf`
4. **Explore Code:** Review `scripts/` and `experiments/`

## Getting Help

- **Issues:** https://github.com/Cbaird26/toe-empirical-validation/issues
- **Documentation:** See `docs/` directory
- **Examples:** See `experiments/` directory

---

**Last Updated:** January 28, 2026
