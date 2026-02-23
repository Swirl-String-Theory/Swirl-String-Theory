#!/usr/bin/env python3
"""
Smart Zenodo workflow that:
1. Checks if config already has DOI before creating new entry
2. Checks if title already exists on Zenodo before creating
3. Updates metadata if title exists
4. Renders and uploads PDF if both config and LaTeX have DOI
"""

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

def has_doi_in_latex(tex_file: Path) -> tuple[bool, str]:
    """Check if LaTeX file has a valid DOI. Returns (has_doi, doi_or_empty)."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        doi_match = re.search(r'10\.5281/zenodo\.(\d+)', content)
        if doi_match:
            doi = doi_match.group(0)
            if re.match(r'10\.5281/zenodo\.\d+$', doi):
                return True, doi
        return False, ''
    except:
        return False, ''

def find_deposit_by_title(automation: ZenodoAutomation, title: str) -> dict | None:
    """Find a deposit on Zenodo by title (case-insensitive, partial match)."""
    deposits = automation.list_deposits(published_only=False, limit=100)
    
    # Normalize title for comparison (lowercase, remove extra spaces)
    title_normalized = ' '.join(title.lower().split())
    
    for deposit in deposits:
        deposit_title = deposit.get('metadata', {}).get('title', '')
        deposit_title_normalized = ' '.join(deposit_title.lower().split())
        
        # Check for exact match or very similar (allowing for minor differences)
        if title_normalized == deposit_title_normalized:
            return deposit
        # Also check if one contains the other (for partial matches)
        if len(title_normalized) > 20 and len(deposit_title_normalized) > 20:
            if title_normalized in deposit_title_normalized or deposit_title_normalized in title_normalized:
                return deposit
    
    return None

def metadata_needs_update(local_metadata: dict, zenodo_metadata: dict) -> bool:
    """Check if local metadata differs from Zenodo metadata."""
    # Compare key fields
    fields_to_check = ['title', 'description', 'keywords', 'creators']
    
    for field in fields_to_check:
        local_val = local_metadata.get(field, '')
        zenodo_val = zenodo_metadata.get(field, '')
        
        # Normalize for comparison
        if isinstance(local_val, list) and isinstance(zenodo_val, list):
            local_val = sorted([str(x) for x in local_val])
            zenodo_val = sorted([str(x) for x in zenodo_val])
        
        if str(local_val).strip() != str(zenodo_val).strip():
            return True
    
    return False

def compile_latex(tex_file: Path, num_passes: int = 2) -> bool:
    """Compile LaTeX file to PDF."""
    tex_dir = tex_file.parent
    tex_name = tex_file.name
    
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
        except Exception as e:
            print(f"    Error compiling: {e}")
            return False
    
    pdf_file = tex_file.with_suffix('.pdf')
    return pdf_file.exists()

def upload_pdf_to_zenodo(automation: ZenodoAutomation, deposit_id: str, pdf_file: Path) -> bool:
    """Upload PDF file to Zenodo deposit."""
    return automation.upload_file_to_deposit(deposit_id, pdf_file)

def process_paper(tex_file: Path, automation: ZenodoAutomation, base_dir: Path) -> dict:
    """Process a single paper through the smart workflow."""
    result = {
        'file': str(tex_file.relative_to(base_dir)),
        'status': 'unknown',
        'message': '',
        'doi': '',
        'action_taken': []
    }
    
    config_file = tex_file.with_suffix('.zenodo.json')
    
    # Step 1: Check if config exists and has DOI
    config_doi = ''
    config_data = {}
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            config_doi = config_data.get('doi', '')
        except:
            pass
    
    # Step 2: Check if LaTeX has DOI
    has_latex_doi, latex_doi = has_doi_in_latex(tex_file)
    
    # Step 3: Extract metadata from LaTeX
    metadata = extract_metadata_from_latex(tex_file)
    if not metadata.get('title'):
        result['status'] = 'error'
        result['message'] = 'No title found in LaTeX file'
        return result
    
    title = metadata['title']
    
    # Step 4: Check if title exists on Zenodo
    existing_deposit = find_deposit_by_title(automation, title)
    
    # Decision logic
    if config_doi:
        # Config has DOI - check if it matches LaTeX
        if has_latex_doi:
            if config_doi == latex_doi:
                # Both match - render and upload if needed
                result['status'] = 'ready'
                result['doi'] = config_doi
                result['message'] = 'Config and LaTeX have matching DOI'
                
                # Check if we need to render and upload
                pdf_file = tex_file.with_suffix('.pdf')
                if pdf_file.exists():
                    # Check if PDF needs to be uploaded
                    deposit_id = config_data.get('deposit_id', '')
                    if deposit_id:
                        result['action_taken'].append('PDF exists, ready to upload')
                    else:
                        result['action_taken'].append('PDF exists but no deposit_id in config')
                else:
                    result['action_taken'].append('Need to render PDF')
            else:
                # Mismatch - update LaTeX with config DOI
                result['status'] = 'updated'
                result['doi'] = config_doi
                result['message'] = 'Updated LaTeX with config DOI'
                if add_doi_to_latex(tex_file, config_doi):
                    result['action_taken'].append('Updated LaTeX DOI')
        else:
            # Config has DOI but LaTeX doesn't - add to LaTeX
            result['status'] = 'updated'
            result['doi'] = config_doi
            result['message'] = 'Added DOI from config to LaTeX'
            if add_doi_to_latex(tex_file, config_doi):
                result['action_taken'].append('Added DOI to LaTeX')
        
        # Check if metadata needs updating
        if existing_deposit:
            deposit_metadata = existing_deposit.get('metadata', {})
            if metadata_needs_update(metadata, deposit_metadata):
                deposit_id = str(existing_deposit.get('id', ''))
                if deposit_id:
                    automation.update_deposit_metadata(deposit_id, metadata)
                    result['action_taken'].append('Updated Zenodo metadata')
    
    elif existing_deposit:
        # Title exists on Zenodo but no config DOI
        deposit_metadata = existing_deposit.get('metadata', {})
        prereserve = deposit_metadata.get('prereserve_doi', {})
        existing_doi = prereserve.get('doi', '') if prereserve else ''
        if not existing_doi:
            existing_doi = deposit_metadata.get('conceptdoi', '') or deposit_metadata.get('doi', '')
        
        if existing_doi:
            # Use existing DOI
            result['status'] = 'found'
            result['doi'] = existing_doi
            result['message'] = 'Found existing deposit on Zenodo'
            
            # Create/update config
            config_data = {
                'title': metadata['title'],
                'creators': metadata.get('creators', []),
                'description': metadata.get('description', ''),
                'keywords': metadata.get('keywords', []),
                'publication_date': metadata.get('publication_date', ''),
                'doi': existing_doi,
                'tex_file': str(tex_file.relative_to(base_dir)),
                'upload_type': 'publication',
                'publication_type': 'article',
                'deposit_id': str(existing_deposit.get('id', ''))
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            result['action_taken'].append('Created config with existing DOI')
            
            # Add DOI to LaTeX if not present
            if not has_latex_doi:
                if add_doi_to_latex(tex_file, existing_doi):
                    result['action_taken'].append('Added DOI to LaTeX')
            
            # Update metadata if needed
            if metadata_needs_update(metadata, deposit_metadata):
                automation.update_deposit_metadata(str(existing_deposit.get('id', '')), metadata)
                result['action_taken'].append('Updated Zenodo metadata')
        else:
            result['status'] = 'error'
            result['message'] = 'Found deposit but no DOI available'
    
    else:
        # No config DOI and title doesn't exist - create new deposit
        result['status'] = 'new'
        result['message'] = 'Creating new deposit on Zenodo'
        
        # Create deposit
        url = f"{automation.base_url}/api/deposit/depositions"
        zenodo_metadata = {
            "metadata": {
                "title": metadata['title'],
                "creators": metadata.get('creators', [{'name': 'Oscar van der Velde'}]),
                "language": metadata.get('language', 'eng'),
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
        
        response = requests.post(url, json=zenodo_metadata, headers=automation.headers)
        
        if response.status_code == 201:
            deposit = response.json()
            deposit_id = str(deposit['id'])
            
            # Get DOI
            deposit_metadata = deposit.get('metadata', {})
            prereserve = deposit_metadata.get('prereserve_doi', {})
            if prereserve and 'doi' in prereserve:
                doi = prereserve['doi']
            else:
                doi = deposit_metadata.get('conceptdoi', '') or deposit_metadata.get('doi', '')
            
            if not doi:
                time.sleep(1)
                for retry in range(3):
                    deposit_info = automation.get_deposit_info(deposit_id)
                    if deposit_info:
                        deposit_metadata = deposit_info.get('metadata', {})
                        prereserve = deposit_metadata.get('prereserve_doi', {})
                        if prereserve and 'doi' in prereserve:
                            doi = prereserve['doi']
                            break
                        doi = deposit_metadata.get('conceptdoi', '') or deposit_metadata.get('doi', '')
                        if doi:
                            break
                    time.sleep(1)
            
            if doi:
                result['doi'] = doi
                result['action_taken'].append('Created new deposit')
                
                # Create config
                config_data = {
                    'title': metadata['title'],
                    'creators': metadata.get('creators', []),
                    'description': metadata.get('description', ''),
                    'keywords': metadata.get('keywords', []),
                    'publication_date': metadata.get('publication_date', ''),
                    'doi': doi,
                    'tex_file': str(tex_file.relative_to(base_dir)),
                    'upload_type': 'publication',
                    'publication_type': 'article',
                    'deposit_id': deposit_id
                }
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                result['action_taken'].append('Created config file')
                
                # Add DOI to LaTeX
                if add_doi_to_latex(tex_file, doi):
                    result['action_taken'].append('Added DOI to LaTeX')
            else:
                result['status'] = 'error'
                result['message'] = 'Created deposit but no DOI returned'
        else:
            result['status'] = 'error'
            result['message'] = f'Failed to create deposit: {response.status_code}'
    
    # Step 5: If both config and LaTeX have DOI, render and upload
    if result['doi'] and has_doi_in_latex(tex_file)[0]:
        pdf_file = tex_file.with_suffix('.pdf')
        deposit_id = config_data.get('deposit_id', '')
        
        if not pdf_file.exists() or pdf_file.stat().st_mtime < tex_file.stat().st_mtime:
            # Need to render
            if compile_latex(tex_file, num_passes=2):
                result['action_taken'].append('Rendered PDF')
            else:
                result['action_taken'].append('Failed to render PDF')
        
        if pdf_file.exists() and deposit_id:
            # Upload PDF
            if upload_pdf_to_zenodo(automation, deposit_id, pdf_file):
                result['action_taken'].append('Uploaded PDF to Zenodo')
            else:
                result['action_taken'].append('Failed to upload PDF')
    
    return result

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Smart Zenodo Workflow")
    print("=" * 80)
    print()
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Find all SST-xx .tex files
    tex_files = []
    for folder in base_dir.iterdir():
        if folder.is_dir() and re.match(r'^SST-\d+', folder.name):
            for tex_file in folder.rglob('*.tex'):
                if tex_file.is_file():
                    try:
                        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        if '\\begin{document}' not in content:
                            continue
                        if '\\title' not in content and '\\papertitle' not in content:
                            continue
                        if 'coverletter' in tex_file.name.lower() or 'cover_letter' in tex_file.name.lower():
                            continue
                        tex_files.append(tex_file)
                    except:
                        continue
    
    print(f"Found {len(tex_files)} papers to process\n")
    
    results = []
    for i, tex_file in enumerate(tex_files, 1):
        print(f"[{i}/{len(tex_files)}] {tex_file.relative_to(base_dir)}")
        result = process_paper(tex_file, automation, base_dir)
        results.append(result)
        print(f"  Status: {result['status']} - {result['message']}")
        if result['doi']:
            print(f"  DOI: {result['doi']}")
        if result['action_taken']:
            for action in result['action_taken']:
                print(f"  - {action}")
        print()
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")
    print(f"Total: {len(results)}")

if __name__ == '__main__':
    main()
