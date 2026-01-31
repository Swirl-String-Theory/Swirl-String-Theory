#!/usr/bin/env python3
"""Process SST-23 file specifically."""

import json
import re
import subprocess
import sys
import time
import requests
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py
from create_zenodo_configs import extract_metadata_from_latex, add_doi_to_latex

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

def compile_latex(tex_file: Path, num_passes: int = 2) -> bool:
    """Compile LaTeX file to PDF."""
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
                log_file = tex_file.with_suffix('.log')
                if log_file.exists():
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                            log_content = f.read()
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
            print(f"    Pass {pass_num}: Timeout")
            return False
        except Exception as e:
            print(f"    Pass {pass_num}: Exception - {e}")
            return False
    
    pdf_file = tex_file.with_suffix('.pdf')
    if pdf_file.exists():
        print(f"  [OK] PDF created: {pdf_file.name}")
        return True
    else:
        print(f"  [ERROR] PDF not found")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    tex_file = base_dir / 'SST-23_Dual_Vacuum_Unification' / 'SST-23_Hydrodynamic_Dual-Vacuum_Unification.tex'
    
    print("=" * 80)
    print("Processing SST-23: Dual Vacuum Unification")
    print("=" * 80)
    print()
    
    # Extract metadata - manually get title from \papertitle
    with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Get title from \papertitle
    title_match = re.search(r'\\newcommand\{\\papertitle\}\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
    if title_match:
        title_text = title_match.group(1).strip()
        title_text = re.sub(r'\\\\', ' ', title_text)
        title_text = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title_text)
        title_text = ' '.join(title_text.split())
        title = title_text
    else:
        # Try \title
        title_match = re.search(r'\\title\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
        if title_match:
            title_text = title_match.group(1).strip()
            title_text = re.sub(r'\\\\', ' ', title_text)
            title_text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', title_text)
            title_text = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title_text)
            title_text = ' '.join(title_text.split())
            title = title_text
        else:
            print("Error: No title found")
            return
    
    print(f"Title: {title}")
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Create deposit
    print("\nCreating draft deposit on Zenodo...")
    url = f"{automation.base_url}/api/deposit/depositions"
    zenodo_metadata = {
        "metadata": {
            "title": title,
            "creators": [{'name': 'Omar Iskandarani'}],
            "description": "",
            "keywords": [],
            "upload_type": "publication",
            "publication_type": "article",
            "access_right": "open",
            "license": "cc-by-4.0",
        }
    }
    
    response = requests.post(url, json=zenodo_metadata, headers=automation.headers)
    
    if response.status_code == 201:
        deposit = response.json()
        deposit_id = str(deposit['id'])
        print(f"Created deposit: {deposit_id}")
        
        # Get DOI
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
            print(f"[OK] Got DOI: {doi}")
            
            # Create config
            config_file = tex_file.with_suffix('.zenodo.json')
            config_data = {
                'title': title,
                'creators': [{'name': 'Omar Iskandarani'}],
                'description': '',
                'keywords': [],
                'publication_date': '',
                'doi': doi,
                'tex_file': str(tex_file.relative_to(base_dir)),
                'upload_type': 'publication',
                'publication_type': 'article',
                'deposit_id': deposit_id
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"[OK] Created config: {config_file.name}")
            
            # Add DOI to LaTeX
            print("\nAdding DOI to LaTeX file...")
            if add_doi_to_latex(tex_file, doi):
                print(f"[OK] Added DOI to LaTeX file")
                
                # Render
                print("\nRendering LaTeX file...")
                if compile_latex(tex_file, num_passes=2):
                    print(f"\n[OK] Successfully processed and rendered SST-23")
                else:
                    print(f"\n[ERROR] Failed to render PDF (but DOI was added)")
            else:
                print(f"[ERROR] Failed to add DOI to LaTeX file")
        else:
            print("[ERROR] No DOI returned")
    else:
        print(f"[ERROR] Failed to create deposit: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == '__main__':
    main()
