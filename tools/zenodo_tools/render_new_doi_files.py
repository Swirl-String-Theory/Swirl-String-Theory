#!/usr/bin/env python3
"""
Render (compile to PDF) all LaTeX files that have new DOIs added.
Only renders files where the DOI is actually embedded in the LaTeX file.
Compiles each file 2 times (standard LaTeX compilation).
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

# Handle encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_doi_in_latex(tex_file: Path, doi: str) -> bool:
    """Check if DOI is present in LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return doi in content
    except:
        return False

def compile_latex(tex_file: Path, num_passes: int = 2) -> bool:
    """Compile LaTeX file to PDF (multiple passes for references)."""
    tex_dir = tex_file.parent
    tex_name = tex_file.name
    
    print(f"  Compiling {tex_name} ({num_passes} passes)...")
    
    for pass_num in range(1, num_passes + 1):
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(tex_dir), tex_name],
                cwd=tex_dir,
                capture_output=True,
                timeout=120,  # 2 minute timeout per pass
                encoding='utf-8',
                errors='replace'  # Replace encoding errors
            )
            
            if result.returncode != 0:
                print(f"    Pass {pass_num}: Error (return code {result.returncode})")
                # Check log file for errors
                log_file = tex_file.with_suffix('.log')
                if log_file.exists():
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                            log_content = f.read()
                            # Find error messages
                            error_lines = [line for line in log_content.split('\n') if 'Error' in line or 'Fatal' in line][:5]
                            for line in error_lines:
                                if line.strip():
                                    print(f"      {line.strip()[:100]}")
                    except:
                        pass
                return False
            else:
                print(f"    Pass {pass_num}: OK")
        
        except subprocess.TimeoutExpired:
            print(f"    Pass {pass_num}: Timeout (>2 minutes)")
            return False
        except Exception as e:
            print(f"    Pass {pass_num}: Exception - {e}")
            return False
    
    # Check if PDF was created
    pdf_file = tex_file.with_suffix('.pdf')
    if pdf_file.exists():
        print(f"  ✓ PDF created: {pdf_file.name}")
        return True
    else:
        print(f"  ✗ PDF not found after compilation")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Rendering LaTeX Files with New DOIs")
    print("=" * 80)
    print()
    
    # Find all .zenodo.json files
    config_files = list(base_dir.rglob('*.zenodo.json'))
    
    files_to_render = []
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            doi = config_data.get('doi', '')
            tex_file_path = config_data.get('tex_file', '')
            
            if not doi:
                continue
            
            # Construct full path to tex file
            if tex_file_path:
                tex_file = base_dir / tex_file_path
            else:
                # Try to find tex file in same directory
                tex_file = config_file.with_suffix('.tex')
            
            if not tex_file.exists():
                print(f"Warning: LaTeX file not found for {config_file.name}")
                continue
            
            # Check if DOI is in LaTeX file
            if check_doi_in_latex(tex_file, doi):
                files_to_render.append({
                    'tex_file': tex_file,
                    'config_file': config_file,
                    'doi': doi,
                    'title': config_data.get('title', 'Unknown')
                })
            else:
                print(f"Skipping {tex_file.name}: DOI not found in LaTeX file")
        
        except Exception as e:
            print(f"Error reading {config_file}: {e}")
            continue
    
    print(f"Found {len(files_to_render)} files with DOIs embedded in LaTeX")
    print()
    
    if not files_to_render:
        print("No files to render.")
        return
    
    # Group by folder for better output
    by_folder = defaultdict(list)
    for item in files_to_render:
        folder = str(item['tex_file'].parent.relative_to(base_dir))
        by_folder[folder].append(item)
    
    success_count = 0
    error_count = 0
    
    for folder in sorted(by_folder.keys()):
        print(f"\n[{folder}]")
        print("-" * 80)
        
        for item in by_folder[folder]:
            tex_file = item['tex_file']
            doi = item['doi']
            title = item['title']
            
            print(f"\n{tex_file.name}")
            print(f"  Title: {title}")
            print(f"  DOI: {doi}")
            
            if compile_latex(tex_file, num_passes=2):
                success_count += 1
            else:
                error_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully compiled: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(files_to_render)}")

if __name__ == '__main__':
    main()
