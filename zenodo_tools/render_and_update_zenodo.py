#!/usr/bin/env python3
"""
Render PDFs and update Zenodo entries for all config files.
Tests with one paper first, then does bulk processing.
"""

import argparse
import json
import subprocess
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py

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

def get_pdf_creation_date(pdf_file: Path) -> str | None:
    """Get PDF creation date in YYYY-MM-DD format."""
    try:
        # Try using pypdf to read PDF metadata
        try:
            import pypdf
            with open(pdf_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                if pdf_reader.metadata and pdf_reader.metadata.get('/CreationDate'):
                    # PDF date format: D:YYYYMMDDHHmmSSOHH'mm
                    date_str = pdf_reader.metadata['/CreationDate']
                    if date_str.startswith('D:'):
                        date_str = date_str[2:]
                    # Extract YYYY-MM-DD
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

def sync_publication_date_in_config(config_file: Path, pdf_file: Path) -> str | None:
    """Update publication_date in config file from PDF creation date. Returns the date if updated."""
    try:
        # Read config
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Get PDF creation date
        pdf_date = get_pdf_creation_date(pdf_file)
        if not pdf_date:
            return None
        
        current_date = config_data.get('publication_date', '')
        
        if current_date == pdf_date:
            return pdf_date  # Already synced
        
        # Update config
        config_data['publication_date'] = pdf_date
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"    [OK] Updated publication_date: {current_date or '(empty)'} -> {pdf_date}")
        return pdf_date
        
    except Exception as e:
        return None

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

def delete_existing_files(automation: ZenodoAutomation, deposit_id: str) -> bool:
    """Delete existing files from deposit before uploading new one."""
    url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}/files"
    response = requests.get(url, headers=automation.headers)
    
    if response.status_code == 200:
        files = response.json()
        for file_info in files:
            file_id = file_info.get('id')
            if file_id:
                delete_url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}/files/{file_id}"
                delete_response = requests.delete(delete_url, headers=automation.headers)
                if delete_response.status_code == 204:
                    print(f"    Deleted old file: {file_info.get('filename', 'unknown')}")
        return True
    return False

def upload_pdf_to_zenodo(automation: ZenodoAutomation, deposit_id: str, pdf_file: Path) -> bool:
    """Upload PDF file to Zenodo deposit."""
    # Delete existing files first
    delete_existing_files(automation, deposit_id)
    
    # Get upload URL
    url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}/files"
    response = requests.get(url, headers=automation.headers)
    
    if response.status_code != 200:
        print(f"    [ERROR] Failed to get upload URL: {response.status_code}")
        return False
    
    # Create new file upload
    upload_headers = {
        "Authorization": f"Bearer {automation.access_token}"
    }
    
    with open(pdf_file, 'rb') as f:
        files = {'file': (pdf_file.name, f, 'application/pdf')}
        data = {'name': pdf_file.name}
        
        response = requests.post(url, data=data, files=files, headers=upload_headers)
    
    if response.status_code == 201:
        print(f"    [OK] Uploaded PDF to Zenodo")
        return True
    else:
        print(f"    [ERROR] Failed to upload PDF: {response.status_code}")
        print(f"      Error: {response.text}")
        return False

def update_zenodo_metadata(automation: ZenodoAutomation, deposit_id: str, config_data: dict) -> bool:
    """Update Zenodo deposit metadata from config file."""
    print(f"    Updating Zenodo metadata...")
    
    # Prepare metadata for Zenodo
    zenodo_metadata = {
        "metadata": {
            "title": config_data.get('title', 'Untitled'),
            "creators": config_data.get('creators', []),
            "description": config_data.get('description', ''),
            "keywords": config_data.get('keywords', []),
            "upload_type": config_data.get('upload_type', 'publication'),
            "publication_type": config_data.get('publication_type', 'article'),
            "access_right": config_data.get('access_right', 'open'),
            "license": config_data.get('license', 'cc-by-4.0'),
        }
    }
    
    # Add language if present
    if config_data.get('language'):
        zenodo_metadata['metadata']['language'] = config_data['language']
    
    if config_data.get('publication_date'):
        zenodo_metadata['metadata']['publication_date'] = config_data['publication_date']
    
    # Add communities if present
    if 'communities' in config_data:
        zenodo_metadata['metadata']['communities'] = config_data['communities']
    
    url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}"
    response = requests.put(url, json=zenodo_metadata, headers=automation.headers)
    
    if response.status_code == 200:
        print(f"    [OK] Updated Zenodo metadata")
        return True
    else:
        print(f"    [ERROR] Failed to update metadata: {response.status_code}")
        print(f"      Error: {response.text}")
        return False

def process_config_file(config_file: Path, automation: ZenodoAutomation, base_dir: Path) -> dict:
    """Process a single config file: render PDF and update Zenodo."""
    result = {
        'config_file': str(config_file.relative_to(base_dir)),
        'status': 'unknown',
        'message': '',
        'actions': []
    }
    
    try:
        # Read config
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        deposit_id = config_data.get('deposit_id', '')
        if not deposit_id:
            result['status'] = 'error'
            result['message'] = 'No deposit_id in config'
            return result
        
        # Find corresponding .tex file
        tex_file_path = config_data.get('tex_file', '')
        if tex_file_path:
            tex_file = base_dir / tex_file_path
        else:
            tex_file = config_file.with_suffix('.tex')
        
        if not tex_file.exists():
            result['status'] = 'error'
            result['message'] = f'LaTeX file not found: {tex_file}'
            return result
        
        print(f"  Processing: {config_file.name}")
        print(f"    Deposit ID: {deposit_id}")
        print(f"    LaTeX file: {tex_file.name}")
        
        # Check if publication_date is empty, set to today if so
        if not config_data.get('publication_date'):
            today = datetime.now().strftime('%Y-%m-%d')
            config_data['publication_date'] = today
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"    [OK] Set empty publication_date to today: {today}")
            # Re-read config to get updated date
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        
        # Render PDF
        success, pdf_file = compile_latex(tex_file, num_passes=2)
        if not success or not pdf_file:
            result['status'] = 'error'
            result['message'] = 'Failed to render PDF'
            return result
        
        result['actions'].append('Rendered PDF')
        
        # Sync publication_date from PDF (this will update if PDF has a different date)
        pdf_date = sync_publication_date_in_config(config_file, pdf_file)
        
        # Re-read config to get updated publication_date
        if pdf_date:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        
        # Update Zenodo metadata
        if update_zenodo_metadata(automation, deposit_id, config_data):
            result['actions'].append('Updated metadata')
        else:
            result['status'] = 'error'
            result['message'] = 'Failed to update metadata'
            return result
        
        # Upload PDF
        if upload_pdf_to_zenodo(automation, deposit_id, pdf_file):
            result['actions'].append('Uploaded PDF')
        else:
            result['status'] = 'error'
            result['message'] = 'Failed to upload PDF'
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
    parser = argparse.ArgumentParser(description='Render PDFs and update Zenodo entries')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation and process all files automatically')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Render PDFs and Update Zenodo Entries")
    print("=" * 80)
    print()
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Find all config files
    config_files = list(base_dir.rglob('*.zenodo.json'))
    
    # Filter to only those with deposit_id
    config_files_with_deposit = []
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            if config_data.get('deposit_id'):
                config_files_with_deposit.append(config_file)
        except:
            pass
    
    print(f"Found {len(config_files_with_deposit)} config files with deposit_id")
    print()
    
    # Test with first file
    if config_files_with_deposit:
        print("=" * 80)
        print("TESTING WITH FIRST PAPER")
        print("=" * 80)
        print()
        
        test_file = config_files_with_deposit[0]
        result = process_config_file(test_file, automation, base_dir)
        
        print()
        print("=" * 80)
        print("TEST RESULT")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        if result['actions']:
            print(f"Actions: {', '.join(result['actions'])}")
        print()
        
        if result['status'] == 'success':
            print("=" * 80)
            print("TEST SUCCESSFUL - Proceeding with bulk processing")
            print("=" * 80)
            print()
            
            # Ask for confirmation (unless --yes flag)
            if not args.yes:
                try:
                    response = input("Do you want to process all remaining files? (yes/no): ")
                    if response.lower() != 'yes':
                        print("Bulk processing cancelled.")
                        return
                except EOFError:
                    print("No input available. Use --yes flag to process automatically.")
                    return
            else:
                print("Auto-processing all remaining files (--yes flag)...")
                print()
            
            # Process remaining files
            remaining_files = config_files_with_deposit[1:]
            print(f"\nProcessing {len(remaining_files)} remaining files...\n")
            
            success_count = 0
            error_count = 0
            
            for i, config_file in enumerate(remaining_files, 2):
                print(f"\n[{i}/{len(config_files_with_deposit)}]")
                result = process_config_file(config_file, automation, base_dir)
                
                if result['status'] == 'success':
                    success_count += 1
                else:
                    error_count += 1
                    print(f"  [ERROR] {result['message']}")
                
                # Rate limiting
                time.sleep(1)
            
            print("\n" + "=" * 80)
            print("BULK PROCESSING SUMMARY")
            print("=" * 80)
            print(f"Successfully processed: {success_count + 1}")  # +1 for test file
            print(f"Errors: {error_count}")
            print(f"Total: {len(config_files_with_deposit)}")
        else:
            print("TEST FAILED - Not proceeding with bulk processing")
            print("Please fix the issue and try again.")
    else:
        print("No config files with deposit_id found.")

if __name__ == '__main__':
    main()
