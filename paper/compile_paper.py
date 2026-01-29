#!/usr/bin/env python3
"""
Compile LaTeX paper to PDF
Uses available LaTeX installation or provides instructions
"""

import subprocess
import sys
from pathlib import Path

def check_latex():
    """Check if LaTeX is available."""
    commands = ['pdflatex', 'latex', 'xelatex', 'lualatex']
    for cmd in commands:
        try:
            result = subprocess.run(['which', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                return cmd, result.stdout.strip()
        except:
            continue
    return None, None

def compile_latex(tex_file, compiler='pdflatex'):
    """Compile LaTeX file to PDF."""
    tex_path = Path(tex_file)
    if not tex_path.exists():
        print(f"Error: {tex_file} not found")
        return False
    
    print(f"Compiling {tex_file} with {compiler}...")
    
    # First pass
    result = subprocess.run(
        [compiler, '-interaction=nonstopmode', str(tex_path)],
        cwd=tex_path.parent,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("First pass had errors:")
        print(result.stderr[-1000:])  # Last 1000 chars
        return False
    
    # BibTeX if needed
    if Path(tex_path.stem + '.aux').exists():
        print("Running BibTeX...")
        subprocess.run(['bibtex', tex_path.stem], cwd=tex_path.parent, capture_output=True)
    
    # Second pass
    print("Second pass...")
    result = subprocess.run(
        [compiler, '-interaction=nonstopmode', str(tex_path)],
        cwd=tex_path.parent,
        capture_output=True,
        text=True
    )
    
    # Third pass (for references)
    print("Third pass (for references)...")
    subprocess.run(
        [compiler, '-interaction=nonstopmode', str(tex_path)],
        cwd=tex_path.parent,
        capture_output=True
    )
    
    pdf_file = tex_path.with_suffix('.pdf')
    if pdf_file.exists():
        print(f"\n✅ PDF created: {pdf_file}")
        print(f"   Size: {pdf_file.stat().st_size / 1024:.1f} KB")
        return True
    else:
        print("\n❌ PDF not created")
        return False

def main():
    """Main function."""
    tex_file = Path(__file__).parent / "main.tex"
    
    print("="*60)
    print("LaTeX Paper Compiler")
    print("="*60)
    print(f"Source: {tex_file}\n")
    
    # Check for LaTeX
    compiler, path = check_latex()
    
    if compiler:
        print(f"✅ Found LaTeX compiler: {compiler}")
        print(f"   Path: {path}\n")
        
        if compile_latex(tex_file, compiler):
            print("\n✅ Compilation successful!")
            return 0
        else:
            print("\n❌ Compilation failed")
            return 1
    else:
        print("❌ LaTeX not found on system")
        print("\nTo compile the paper, you need LaTeX installed:")
        print("\n  macOS:")
        print("    brew install --cask mactex")
        print("\n  Linux:")
        print("    sudo apt-get install texlive-full")
        print("\n  Windows:")
        print("    Install MiKTeX or TeX Live")
        print("\n  Or use Overleaf:")
        print("    https://www.overleaf.com")
        print("    Upload the paper/ directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())
