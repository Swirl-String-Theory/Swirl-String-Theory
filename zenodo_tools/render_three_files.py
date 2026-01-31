#!/usr/bin/env python3
"""Render the three specific files that now have DOIs."""

import subprocess
import sys
from pathlib import Path

# Handle encoding
if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

FILES_TO_RENDER = [
    'SST-23_Dual_Vacuum_Unification/SST-23_Hydrodynamic_Dual-Vacuum_Unification.tex',
    'SST-55_Delay-Induced_Mode_Selection_in_Circulating_Feedback_Systems/SST-55_Delay-Induced_Mode_Selection_in_Circulating_Feedback_Systems.tex',
    'SST-59_Atomic_Masses_from_Topological_Invariants_of_Knotted_Field_Configurations/SST-59_Atomic_Masses_from_Topological_Invariants_of_Knotted_Field_Configurations.tex',
]

def compile_latex(tex_file: Path, num_passes: int = 2) -> bool:
    """Compile LaTeX file to PDF."""
    tex_dir = tex_file.parent
    tex_name = tex_file.name
    
    print(f"  Compiling {tex_name} ({num_passes} passes)...")
    
    success = True
    for pass_num in range(1, num_passes + 1):
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(tex_dir), tex_name],
                cwd=tex_dir,
                capture_output=True,
                timeout=120,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                print(f"    Pass {pass_num}: Warning (return code {result.returncode})")
                # Check if PDF was still created despite errors
                pdf_file = tex_file.with_suffix('.pdf')
                if not pdf_file.exists():
                    success = False
            else:
                print(f"    Pass {pass_num}: OK")
        
        except subprocess.TimeoutExpired:
            print(f"    Pass {pass_num}: Timeout")
            success = False
        except Exception as e:
            print(f"    Pass {pass_num}: Exception - {e}")
            success = False
    
    # Check if PDF was created
    pdf_file = tex_file.with_suffix('.pdf')
    if pdf_file.exists():
        print(f"  [OK] PDF created: {pdf_file.name}")
        return True
    else:
        print(f"  [ERROR] PDF not found after compilation")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Rendering Files with New DOIs (2 passes each)")
    print("=" * 80)
    print()
    
    success_count = 0
    error_count = 0
    
    for i, file_path_str in enumerate(FILES_TO_RENDER, 1):
        print(f"\n[{i}/{len(FILES_TO_RENDER)}] {file_path_str}")
        print("-" * 80)
        
        tex_file = base_dir / file_path_str
        
        if not tex_file.exists():
            print(f"  [ERROR] File not found")
            error_count += 1
            continue
        
        if compile_latex(tex_file, num_passes=2):
            success_count += 1
        else:
            error_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully rendered: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(FILES_TO_RENDER)}")

if __name__ == '__main__':
    main()
