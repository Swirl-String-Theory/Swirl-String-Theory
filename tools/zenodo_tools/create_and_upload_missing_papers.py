#!/usr/bin/env python3
"""
Create DOIs, configs, render PDFs, and upload for the 4 missing papers:
- SST-02_Knot_Classified
- SST-13_Gravitational_Modulation
- SST-26_Neutrinos
- SST-28_Time_from_Swirl
"""

import json
import re
import subprocess
import sys
import time
import requests
from datetime import datetime
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

# Standard creator
STANDARD_CREATOR = {
    "name": "Omar Iskandarani",
    "affiliation": "Independent Researcher, Groningen, The Netherlands",
    "orcid": "0009-0006-1686-3961"
}

def compile_latex(tex_file: Path, num_passes: int = 2) -> tuple[bool, Path | None]:
    """Compile LaTeX file to PDF. Returns (success, pdf_path)."""
    tex_dir = tex_file.parent
    tex_name = tex_file.name
    pdf_file = tex_file.with_suffix('.pdf')
    
    print(f"    Compiling LaTeX ({num_passes} passes)...")
    
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
                print(f"      Pass {pass_num}: Warning (return code {result.returncode})")
            else:
                print(f"      Pass {pass_num}: OK")
        except Exception as e:
            print(f"      Pass {pass_num}: Error - {e}")
            return False, None
    
    if pdf_file.exists():
        print(f"    [OK] PDF created: {pdf_file.name}")
        return True, pdf_file
    else:
        print(f"    [ERROR] PDF not found after compilation")
        return False, None

def get_pdf_creation_date(pdf_file: Path) -> str | None:
    """Get PDF creation date in YYYY-MM-DD format."""
    try:
        # Try using pypdf to read PDF metadata
        try:
            import pypdf
            with open(pdf_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                if pdf_reader.metadata and pdf_reader.metadata.get('/CreationDate'):
                    date_str = pdf_reader.metadata['/CreationDate']
                    if date_str.startswith('D:'):
                        date_str = date_str[2:]
                    if len(date_str) >= 8:
                        year = date_str[0:4]
                        month = date_str[4:6]
                        day = date_str[6:8]
                        return f"{year}-{month}-{day}"
        except ImportError:
            pass
        
        # Fallback: use file modification time
        mtime = pdf_file.stat().st_mtime
        date_obj = datetime.fromtimestamp(mtime)
        return date_obj.strftime('%Y-%m-%d')
    except Exception as e:
        return None

def process_paper(folder_name: str, automation: ZenodoAutomation, base_dir: Path) -> dict:
    """Process a single paper: create DOI, config, render, upload."""
    result = {
        'folder': folder_name,
        'status': 'unknown',
        'message': '',
        'doi': '',
        'deposit_id': ''
    }
    
    try:
        folder = base_dir / folder_name
        tex_file = folder / f"{folder_name}.tex"
        config_file = folder / f"{folder_name}.zenodo.json"
        
        if not tex_file.exists():
            result['status'] = 'error'
            result['message'] = f'LaTeX file not found: {tex_file}'
            return result
        
        print(f"\n{'='*80}")
        print(f"Processing: {folder_name}")
        print(f"{'='*80}")
        print()
        
        # Extract metadata from LaTeX
        print("  Extracting metadata from LaTeX...")
        metadata = extract_metadata_from_latex(tex_file)
        
        # If no title found, try to extract from first section
        if not metadata.get('title'):
            try:
                with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                section_match = re.search(r'\\section\{([^}]+)\}', content)
                if section_match:
                    metadata['title'] = section_match.group(1).strip()
                    print(f"    Using first section as title: {metadata['title']}")
            except Exception:
                pass
        
        if not metadata.get('title'):
            result['status'] = 'error'
            result['message'] = 'Could not extract title from LaTeX'
            return result
        
        # Ensure creators
        if not metadata.get('creators'):
            metadata['creators'] = [STANDARD_CREATOR.copy()]
        else:
            # Ensure standard creator format
            metadata['creators'] = [STANDARD_CREATOR.copy()]
        
        # Set publication_date to today if empty
        if not metadata.get('publication_date'):
            metadata['publication_date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"    Title: {metadata['title'][:80]}...")
        print()
        
        # Create draft deposit on Zenodo
        print("  Creating draft deposit on Zenodo...")
        zenodo_metadata = {
            "metadata": {
                "title": metadata['title'],
                "creators": metadata['creators'],
                "description": metadata.get('description', ''),
                "keywords": metadata.get('keywords', []),
                "upload_type": "publication",
                "publication_type": "preprint",
                "publication_date": metadata['publication_date'],
                "language": "eng",
                "access_right": "open",
                "license": "cc-by-4.0",
            }
        }
        
        # Add communities
        zenodo_metadata['metadata']['communities'] = [{"identifier": "SST"}]
        
        url = f"{automation.base_url}/api/deposit/depositions"
        response = requests.post(url, json=zenodo_metadata, headers=automation.headers)
        
        if response.status_code != 201:
            result['status'] = 'error'
            result['message'] = f'Failed to create deposit: {response.status_code} - {response.text}'
            return result
        
        deposit = response.json()
        deposit_id = str(deposit['id'])
        
        # Get DOI (may need to wait a bit)
        time.sleep(2)
        deposit_info = automation.get_deposit_info(deposit_id)
        if deposit_info:
            prereserve = deposit_info.get('metadata', {}).get('prereserve_doi', {})
            doi = prereserve.get('doi', '') if prereserve else ''
            if not doi:
                # Try again after a delay
                time.sleep(2)
                deposit_info = automation.get_deposit_info(deposit_id)
                if deposit_info:
                    prereserve = deposit_info.get('metadata', {}).get('prereserve_doi', {})
                    doi = prereserve.get('doi', '') if prereserve else ''
        
        if not doi:
            result['status'] = 'error'
            result['message'] = 'DOI not available after deposit creation'
            return result
        
        print(f"    [OK] Created deposit: {deposit_id}")
        print(f"    [OK] DOI: {doi}")
        result['doi'] = doi
        result['deposit_id'] = deposit_id
        print()
        
        # Add DOI to LaTeX file
        print("  Adding DOI to LaTeX file...")
        if add_doi_to_latex(tex_file, doi):
            print(f"    [OK] Added DOI to LaTeX")
        else:
            print(f"    [WARNING] Could not add DOI to LaTeX")
        print()
        
        # Create config file
        print("  Creating config file...")
        config_data = {
            "title": metadata['title'],
            "creators": metadata['creators'],
            "description": metadata.get('description', ''),
            "keywords": metadata.get('keywords', []),
            "publication_date": metadata['publication_date'],
            "doi": doi,
            "tex_file": str(tex_file.relative_to(base_dir)),
            "upload_type": "publication",
            "publication_type": "preprint",
            "access_right": "open",
            "license": "cc-by-4.0",
            "language": "eng",
            "deposit_id": deposit_id,
            "communities": [{"identifier": "SST"}]
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"    [OK] Created config file: {config_file.name}")
        print()
        
        # Render PDF
        print("  Rendering PDF...")
        success, pdf_file = compile_latex(tex_file, num_passes=2)
        if not success or not pdf_file:
            result['status'] = 'error'
            result['message'] = 'Failed to render PDF'
            return result
        
        # Sync publication_date from PDF
        pdf_date = get_pdf_creation_date(pdf_file)
        if pdf_date:
            config_data['publication_date'] = pdf_date
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"    [OK] Updated publication_date from PDF: {pdf_date}")
        
        # Update Zenodo metadata with final publication_date
        if pdf_date:
            zenodo_metadata['metadata']['publication_date'] = pdf_date
            url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}"
            requests.put(url, json=zenodo_metadata, headers=automation.headers)
        
        print()
        
        # Upload PDF to Zenodo
        print("  Uploading PDF to Zenodo...")
        upload_url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}/files"
        upload_response = requests.get(upload_url, headers=automation.headers)
        
        if upload_response.status_code == 200:
            upload_headers = {
                "Authorization": f"Bearer {automation.access_token}"
            }
            
            with open(pdf_file, 'rb') as f:
                files = {'file': (pdf_file.name, f, 'application/pdf')}
                data = {'name': pdf_file.name}
                
                upload_response = requests.post(upload_url, data=data, files=files, headers=upload_headers)
            
            if upload_response.status_code == 201:
                print(f"    [OK] Uploaded PDF to Zenodo")
            else:
                result['status'] = 'error'
                result['message'] = f'Failed to upload PDF: {upload_response.status_code}'
                return result
        else:
            result['status'] = 'error'
            result['message'] = f'Failed to get upload URL: {upload_response.status_code}'
            return result
        
        result['status'] = 'success'
        result['message'] = 'Completed successfully'
        
    except Exception as e:
        result['status'] = 'error'
        result['message'] = f'Exception: {e}'
        import traceback
        traceback.print_exc()
    
    return result

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Create DOIs and Upload Missing Papers")
    print("=" * 80)
    print()
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Papers to process
    papers = [
        "SST-02_Knot_Classified",
        "SST-13_Gravitational_Modulation",
        "SST-26_Neutrinos",
        "SST-28_Time_from_Swirl"
    ]
    
    print(f"Processing {len(papers)} papers:")
    for paper in papers:
        print(f"  - {paper}")
    print()
    
    results = []
    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}]")
        result = process_paper(paper, automation, base_dir)
        results.append(result)
        
        if result['status'] == 'success':
            print(f"\n✓ {paper}: Success")
            print(f"  DOI: {result['doi']}")
            print(f"  Deposit ID: {result['deposit_id']}")
        else:
            print(f"\n✗ {paper}: Failed")
            print(f"  Error: {result['message']}")
        
        # Rate limiting
        if i < len(papers):
            time.sleep(2)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = len(results) - success_count
    
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print()
    
    if success_count > 0:
        print("Successfully processed papers:")
        for r in results:
            if r['status'] == 'success':
                print(f"  ✓ {r['folder']}: {r['doi']}")
        print()
    
    if error_count > 0:
        print("Failed papers:")
        for r in results:
            if r['status'] != 'success':
                print(f"  ✗ {r['folder']}: {r['message']}")

if __name__ == '__main__':
    main()
