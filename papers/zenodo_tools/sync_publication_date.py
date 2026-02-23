#!/usr/bin/env python3
"""
Sync publication_date in .zenodo.json config files with PDF creation date.
"""

import argparse
import json
import sys
from datetime import datetime
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

def get_pdf_creation_date(pdf_file: Path) -> str | None:
    """Get PDF creation date in YYYY-MM-DD format."""
    try:
        # Try using PyPDF2 or pypdf
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

def sync_publication_date(config_file: Path, base_dir: Path, update_zenodo: bool = False) -> bool:
    """Sync publication_date in config file with PDF creation date."""
    try:
        # Read config
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Find PDF file
        tex_file_path = config_data.get('tex_file', '')
        if tex_file_path:
            tex_file = base_dir / tex_file_path
            pdf_file = tex_file.with_suffix('.pdf')
        else:
            pdf_file = config_file.with_suffix('.pdf')
        
        if not pdf_file.exists():
            print(f"  [SKIP] PDF not found: {pdf_file.name}")
            return False
        
        # Get PDF creation date
        pdf_date = get_pdf_creation_date(pdf_file)
        if not pdf_date:
            print(f"  [SKIP] Could not determine PDF date")
            return False
        
        current_date = config_data.get('publication_date', '')
        
        if current_date == pdf_date:
            print(f"  [OK] Already synced: {pdf_date}")
            return True
        
        # Update config
        config_data['publication_date'] = pdf_date
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"  [OK] Updated: {current_date or '(empty)'} -> {pdf_date}")
        
        # Optionally update Zenodo
        if update_zenodo:
            from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py
            token = read_token_from_zenodo_py()
            if token:
                automation = ZenodoAutomation(token, sandbox=False)
                deposit_id = config_data.get('deposit_id', '')
                if deposit_id:
                    # Update metadata on Zenodo
                    url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}"
                    zenodo_metadata = {
                        "metadata": {
                            "publication_date": pdf_date
                        }
                    }
                    import requests
                    response = requests.put(url, json=zenodo_metadata, headers=automation.headers)
                    if response.status_code == 200:
                        print(f"    [OK] Updated Zenodo metadata")
                    else:
                        print(f"    [WARNING] Failed to update Zenodo: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Sync publication_date with PDF creation date')
    parser.add_argument('--config', type=str, help='Specific config file to update (optional)')
    parser.add_argument('--all', action='store_true', help='Update all config files')
    parser.add_argument('--update-zenodo', action='store_true', help='Also update Zenodo metadata')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Sync Publication Date with PDF Creation Date")
    print("=" * 80)
    print()
    
    if args.config:
        # Update single config file
        config_file = base_dir / args.config
        if not config_file.exists():
            print(f"Error: Config file not found: {config_file}")
            return
        
        print(f"Updating: {config_file.relative_to(base_dir)}")
        print()
        sync_publication_date(config_file, base_dir, args.update_zenodo)
        
    elif args.all:
        # Update all config files
        config_files = list(base_dir.rglob('*.zenodo.json'))
        
        print(f"Found {len(config_files)} config files")
        print()
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for config_file in sorted(config_files):
            print(f"Processing: {config_file.relative_to(base_dir)}")
            if sync_publication_date(config_file, base_dir, args.update_zenodo):
                updated_count += 1
            else:
                skipped_count += 1
            print()
        
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Updated: {updated_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Total: {len(config_files)}")
    else:
        print("Error: Please specify --config <file> or --all")
        parser.print_help()

if __name__ == '__main__':
    main()
