# LaTeX Paper: Empirical Validation of MQGT-SCF

This directory contains the LaTeX source for the empirical validation paper.

## Files

- **main.tex** - Main LaTeX document
- **README.md** - This file

## Compilation

### Local Compilation

```bash
# Install LaTeX (if needed)
# macOS: brew install --cask mactex
# Linux: sudo apt-get install texlive-full
# Windows: Install MiKTeX or TeX Live

# Compile
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Or use latexmk
latexmk -pdf main.tex
```

### Overleaf (Recommended)

1. Go to [Overleaf.com](https://www.overleaf.com)
2. Create new project → Upload Project
3. Upload the `paper/` directory
4. Compile in browser

## Structure

The paper includes:

1. **Abstract** - Summary of validation results
2. **Introduction** - Context and motivation; **Scope, Control, and Non-Interference Statement** (Hard Patch) — physics vs engineering safety, Zora advisory-by-default, no interference with lawful defense/governance
3. **Theoretical Framework** - Unified Lagrangian and predictions
4. **Empirical Validation Methodology** - Constraint pipeline
5. **Results** - 80 data points, 100% validation rate
6. **Discussion** - Implications and limitations
7. **Conclusion** - Summary and future work

## Figures

The paper references figures from `../results/scalar_constraints/`:
- `golden_exclusion_plot.png` - Main exclusion plot
- `toe_predictions_vs_bounds.png` - Validation comparison

Make sure these paths are correct when compiling.

## Journal Submission

### Suggested Journals

1. **Physical Review Letters (PRL)** - For high-impact results
2. **Physical Review D (PRD)** - For theoretical physics
3. **Foundations of Physics** - For foundational work
4. **Open Access Options:**
   - PLOS ONE
   - Scientific Reports
   - arXiv.org (preprint)

### Before Submission

- [ ] Add all co-authors
- [ ] Complete bibliography with full references
- [ ] Add figure captions
- [ ] Check formatting for target journal
- [ ] Add supplementary material section
- [ ] Include data availability statement
- [ ] Add author contributions section

## Customization

### For Different Journals

Most journals provide LaTeX templates. To adapt:

1. Download journal template
2. Copy content from `main.tex`
3. Adjust formatting as needed
4. Follow journal-specific guidelines

### Adding More Content

- **Methods Section**: Expand constraint pipeline details
- **Supplementary Material**: Add detailed derivations
- **Extended Results**: Include sensor experiment results
- **Discussion**: Add more theoretical implications

## Citation

When published, cite as:

```bibtex
@article{baird2026validation,
  title = {Empirical Validation of a Unified Theory of Everything: Modified Quantum Gravity Theory with Scalar Consciousness Fields},
  author = {Baird, Christopher Michael},
  journal = {[Journal Name]},
  year = {2026},
  ...
}
```

## Notes

- The paper is currently in draft form
- Figures need to be included (paths may need adjustment)
- Bibliography needs expansion with full references
- Author affiliations and contact info should be added
- Consider adding supplementary material

---

**Status:** Draft - Ready for Overleaf compilation  
**Last Updated:** January 28, 2026
