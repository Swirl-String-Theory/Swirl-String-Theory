#!/usr/bin/env python3
"""
Process specific files: create config, get DOI, add to LaTeX, and render.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py
from create_zenodo_configs import extract_metadata_from_latex, add_doi_to_latex

# Handle encoding on Windows
if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# Files to process
FILES_TO_PROCESS = [
    'SST-23_Dual_Vacuum_Unification/SST-23_Hydrodynamic_Dual-Vacuum_Unification.tex',
    'SST-55_Delay-Induced_Mode_Selection_in_Circulating_Feedback_Systems/SST-55_Delay-Induced_Mode_Selection_in_Circulating_Feedback_Systems.tex',
    'SST-59_Atomic_Masses_from_Topological_Invariants_of_Knotted_Field_Configurations/SST-59_Atomic_Masses_from_Topological_Invariants_of_Knotted_Field_Configurations.tex',
]

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
                timeout=120,
                encoding='utf-8',
                errors='replace'
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
        print(f"  [OK] PDF created: {pdf_file.name}")
        return True
    else:
        print(f"  [ERROR] PDF not found after compilation")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Processing Specific Files: Create DOI and Render")
    print("=" * 80)
    print()
    
    # Get Zenodo token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found in ../../zenodo.py")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    success_count = 0
    error_count = 0
    
    for i, file_path_str in enumerate(FILES_TO_PROCESS, 1):
        print(f"\n[{i}/{len(FILES_TO_PROCESS)}] Processing: {file_path_str}")
        print("-" * 80)
        
        tex_file = base_dir / file_path_str
        
        if not tex_file.exists():
            print(f"  [ERROR] File not found: {tex_file}")
            error_count += 1
            continue
        
        # Step 1: Extract metadata
        print("  Step 1: Extracting metadata...")
        metadata = extract_metadata_from_latex(tex_file)
        
        if not metadata.get('title'):
            print(f"  [ERROR] No title found, skipping...")
            error_count += 1
            continue
        
        print(f"  Title: {metadata['title']}")
        
        # Step 2: Check if config already exists
        config_file = tex_file.with_suffix('.zenodo.json')
        doi = ''
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            doi = config_data.get('doi', '')
            if doi:
                print(f"  Found existing config with DOI: {doi}")
        
        # Step 3: Create or update config and get DOI
        if not doi:
            print("  Step 2: Creating draft deposit on Zenodo...")
            try:
                url = f"{automation.base_url}/api/deposit/depositions"
                zenodo_metadata = {
                    "metadata": {
                        "title": metadata['title'],
                        "creators": metadata.get('creators', [{'name': 'Oscar van der Velde'}]),
                        "description": metadata.get('description', ''),
                        "keywords": metadata.get('keywords', []),
                        "upload_type": "publication",
                        "publication_type": "article",
                        "access_right": "open",
                        "license": "cc-by-4.0",
                    }
                }
                if metadata.get('publication_date'):
                    zenodo_metadata['metadata']['publication_date'] = metadata['publication_date']
                
                import requests
                response = requests.post(url, json=zenodo_metadata, headers=automation.headers)
                
                if response.status_code == 201:
                    deposit = response.json()
                    deposit_id = str(deposit['id'])
                    print(f"  Created deposit: {deposit_id}")
                    
                    # Get DOI from response
                    metadata_zenodo = deposit.get('metadata', {})
                    prereserve = metadata_zenodo.get('prereserve_doi', {})
                    if prereserve and 'doi' in prereserve:
                        doi = prereserve['doi']
                    else:
                        doi = metadata_zenodo.get('conceptdoi', '') or metadata_zenodo.get('doi', '')
                    
                    if not doi:
                        time.sleep(1)
                        for retry in range(3):
                            deposit_info = automation.get_deposit_info(deposit_id)
                            if deposit_info:
                                metadata_zenodo = deposit_info.get('metadata', {})
                                prereserve = metadata_zenodo.get('prereserve_doi', {})
                                if prereserve and 'doi' in prereserve:
                                    doi = prereserve['doi']
                                    break
                                doi = metadata_zenodo.get('conceptdoi', '') or metadata_zenodo.get('doi', '')
                                if doi:
                                    break
                            time.sleep(1)
                    
                    if doi:
                        print(f"  [OK] Got DOI: {doi}")
                    else:
                        print(f"  [ERROR] No DOI returned from deposit")
                        error_count += 1
                        continue
                else:
                    print(f"  [ERROR] Failed to create deposit: {response.status_code}")
                    print(f"  Error: {response.text}")
                    error_count += 1
                    continue
            
            except Exception as e:
                print(f"  [ERROR] Exception: {e}")
                import traceback
                traceback.print_exc()
                error_count += 1
                continue
        
        # Step 4: Update config file
        config_data = {
            'title': metadata['title'],
            'creators': metadata.get('creators', [{'name': 'Oscar van der Velde'}]),
            'description': metadata.get('description', ''),
            'keywords': metadata.get('keywords', []),
            'publication_date': metadata.get('publication_date', ''),
            'doi': doi,
            'tex_file': str(tex_file.relative_to(base_dir)),
            'upload_type': 'publication',
            'publication_type': 'article'
        }
        if 'deposit_id' in locals():
            config_data['deposit_id'] = deposit_id
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Updated config: {config_file.name}")
        
        # Step 5: Add DOI to LaTeX file
        print("  Step 3: Adding DOI to LaTeX file...")
        if add_doi_to_latex(tex_file, doi):
            print(f"  [OK] Added DOI to LaTeX file")
        else:
            print(f"  [ERROR] Failed to add DOI to LaTeX file")
            error_count += 1
            continue
        
        # Step 6: Render (compile) LaTeX file
        print("  Step 4: Rendering LaTeX file...")
        if compile_latex(tex_file, num_passes=2):
            success_count += 1
            print(f"  [OK] Successfully processed and rendered")
        else:
            error_count += 1
            print(f"  [ERROR] Failed to render PDF")
        
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(FILES_TO_PROCESS)}")

if __name__ == '__main__':
    main()
