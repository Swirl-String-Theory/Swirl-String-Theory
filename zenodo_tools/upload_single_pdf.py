#!/usr/bin/env python3
"""
Upload a single PDF to Zenodo for a specific config file.
"""

import argparse
import json
import sys
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
        print(f"    Warning: Could not get PDF date: {e}")
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
        
        print(f"  [OK] Updated publication_date: {current_date or '(empty)'} -> {pdf_date}")
        return pdf_date
        
    except Exception as e:
        print(f"  [WARNING] Could not sync publication_date: {e}")
        return None

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
                    print(f"  Deleted old file: {file_info.get('filename', 'unknown')}")
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
        print(f"  [ERROR] Failed to get upload URL: {response.status_code}")
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
        print(f"  [OK] Uploaded PDF to Zenodo")
        return True
    else:
        print(f"  [ERROR] Failed to upload PDF: {response.status_code}")
        print(f"    Error: {response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload a single PDF to Zenodo')
    parser.add_argument('config_file', type=str, help='Path to .zenodo.json config file (relative to SwirlStringTheory root)')
    parser.add_argument('--pdf', type=str, help='Path to PDF file (optional, will try to find automatically)')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    # Get token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Find config file
    config_file = base_dir / args.config_file
    if not config_file.exists():
        print(f"Error: Config file not found: {config_file}")
        return
    
    # Read config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        return
    
    deposit_id = config_data.get('deposit_id', '')
    if not deposit_id:
        print("Error: No deposit_id in config file")
        return
    
    # Find PDF file
    if args.pdf:
        pdf_file = base_dir / args.pdf
    else:
        # Try to find PDF based on tex_file or config file name
        tex_file_path = config_data.get('tex_file', '')
        if tex_file_path:
            tex_file = base_dir / tex_file_path
            pdf_file = tex_file.with_suffix('.pdf')
        else:
            pdf_file = config_file.with_suffix('.pdf')
    
    if not pdf_file.exists():
        print(f"Error: PDF file not found: {pdf_file}")
        return
    
    print("=" * 80)
    print("Upload Single PDF to Zenodo")
    print("=" * 80)
    print()
    print(f"Config file: {config_file.relative_to(base_dir)}")
    print(f"PDF file: {pdf_file.relative_to(base_dir)}")
    print(f"Deposit ID: {deposit_id}")
    print()
    
    # Check if publication_date is empty, set to today if so (only when uploading)
    if not config_data.get('publication_date'):
        today = datetime.now().strftime('%Y-%m-%d')
        config_data['publication_date'] = today
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Set empty publication_date to today: {today}")
        # Re-read config to get updated date
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    
    # Sync publication_date from PDF
    pdf_date = sync_publication_date_in_config(config_file, pdf_file)
    
    # Re-read config to get updated publication_date
    if pdf_date:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    
    # Upload PDF
    if upload_pdf_to_zenodo(automation, deposit_id, pdf_file):
        # Update Zenodo metadata with publication_date if it was synced
        if pdf_date:
            print(f"  Updating Zenodo metadata with publication_date...")
            url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}"
            zenodo_metadata = {
                "metadata": {
                    "publication_date": pdf_date
                }
            }
            response = requests.put(url, json=zenodo_metadata, headers=automation.headers)
            if response.status_code == 200:
                print(f"  [OK] Updated Zenodo publication_date")
            else:
                print(f"  [WARNING] Failed to update Zenodo publication_date: {response.status_code}")
        
        print()
        print("=" * 80)
        print("SUCCESS")
        print("=" * 80)
        print(f"PDF uploaded successfully to deposit {deposit_id}")
    else:
        print()
        print("=" * 80)
        print("FAILED")
        print("=" * 80)
        print("Failed to upload PDF")

if __name__ == '__main__':
    main()
