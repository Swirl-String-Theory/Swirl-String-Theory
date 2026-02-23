#!/usr/bin/env python3
"""
Compare local LaTeX files with Zenodo deposits to determine:
1. Which files are already online (have DOIs that match Zenodo)
2. Which files need to be added to Zenodo
"""

import csv
import re
from pathlib import Path
from collections import defaultdict
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py

def check_if_draft_on_zenodo(doi, token=None, sandbox=False):
    """Check if a DOI exists as a draft on Zenodo."""
    if token is None:
        token = read_token_from_zenodo_py()
    if not token:
        return None
    
    try:
        automation = ZenodoAutomation(token, sandbox=sandbox)
        all_deposits = automation.list_deposits(published_only=False, limit=100)
        
        for deposit in all_deposits:
            metadata = deposit.get('metadata', {})
            deposit_doi = metadata.get('doi', '')
            if deposit_doi == doi:
                return {
                    'is_draft': not deposit.get('submitted', False),
                    'title': metadata.get('title', ''),
                    'url': deposit.get('links', {}).get('html', '')
                }
    except:
        pass
    return None

def get_local_dois():
    """Get all DOIs from local LaTeX files (only from SST-xx folders)."""
    base_dir = Path(__file__).parent.parent
    local_dois = {}
    
    # Read from DOI_Status.csv if it exists
    csv_file = base_dir / 'DOI_Status.csv'
    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Has_DOI'] == 'Yes' and row['DOI']:
                    folder = row['Folder']
                    filename = row['File']
                    
                    # Only include files from SST-xx folders
                    if folder and folder != '.':
                        # Check if folder matches SST-xx pattern
                        if not re.match(r'^SST-\d+', folder):
                            continue
                        full_path = f"{folder}\\{filename}"
                    else:
                        continue  # Skip files in root directory
                    
                    doi = row['DOI'].strip()
                    local_dois[doi] = {
                        'file': full_path,
                        'folder': folder,
                        'filename': filename
                    }
    
    return local_dois

def get_zenodo_dois(token=None, sandbox=False, use_csv=True):
    """Get all DOIs from Zenodo (prefer CSV file if available)."""
    base_dir = Path(__file__).parent.parent
    csv_file = base_dir / 'zenodo_papers.csv'
    
    # Try to read from CSV first (faster and doesn't require API call)
    if use_csv and csv_file.exists():
        zenodo_dois = {}
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row.get('doi', '').strip()
                if doi and doi != 'N/A':
                    zenodo_dois[doi] = {
                        'title': row.get('title', ''),
                        'url': row.get('url', ''),
                        'date': row.get('publication_date', ''),
                        'id': row.get('id', '')
                    }
        if zenodo_dois:
            return zenodo_dois
    
    # Fall back to API query
    if token is None:
        token = read_token_from_zenodo_py()
    
    if not token:
        print("Warning: No Zenodo token found. Cannot query Zenodo.")
        return {}
    
    automation = ZenodoAutomation(token, sandbox=sandbox)
    papers = automation.list_published_papers(limit=100)  # Zenodo max is 100
    
    zenodo_dois = {}
    for paper in papers:
        doi = paper['doi']
        if doi and doi != 'N/A':
            zenodo_dois[doi] = {
                'title': paper['title'],
                'url': paper['url'],
                'date': paper['publication_date'],
                'id': paper['id']
            }
    
    return zenodo_dois

def normalize_doi(doi):
    """Normalize DOI for comparison (remove trailing periods, etc.)."""
    if not doi:
        return None
    doi = doi.strip()
    # Remove trailing period if present
    if doi.endswith('.'):
        doi = doi[:-1]
    return doi

def compare_local_zenodo():
    """Compare local files with Zenodo deposits."""
    print("=" * 80)
    print("Comparing Local Files with Zenodo Deposits")
    print("=" * 80)
    print()
    
    # Get local DOIs
    print("Step 1: Reading local DOIs from files...")
    local_dois = get_local_dois()
    print(f"  Found {len(local_dois)} local files with DOIs\n")
    
    # Get Zenodo DOIs
    print("Step 2: Querying Zenodo for published papers...")
    zenodo_dois = get_zenodo_dois()
    print(f"  Found {len(zenodo_dois)} published papers on Zenodo\n")
    
    # Normalize DOIs for comparison
    local_normalized = {normalize_doi(doi): info for doi, info in local_dois.items()}
    zenodo_normalized = {normalize_doi(doi): info for doi, info in zenodo_dois.items()}
    
    # Find matches
    matched = {}
    local_only = {}
    zenodo_only = {}
    
    for doi, local_info in local_normalized.items():
        if doi in zenodo_normalized:
            matched[doi] = {
                'local': local_info,
                'zenodo': zenodo_normalized[doi]
            }
        else:
            local_only[doi] = local_info
    
    for doi, zenodo_info in zenodo_normalized.items():
        if doi not in local_normalized:
            zenodo_only[doi] = zenodo_info
    
    # Print results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    print(f"✓ Files ALREADY ONLINE (matched): {len(matched)}")
    print(f"⚠ Files with DOI but NOT on Zenodo: {len(local_only)}")
    print(f"ℹ Papers on Zenodo but not in local files: {len(zenodo_only)}")
    print()
    
    # Files already online
    if matched:
        print("=" * 80)
        print("FILES ALREADY ONLINE (Local file matches Zenodo deposit)")
        print("=" * 80)
        for doi, info in sorted(matched.items(), key=lambda x: x[1]['zenodo']['date'], reverse=True):
            print(f"\nDOI: {doi}")
            print(f"  Local file: {info['local']['file']}")
            print(f"  Zenodo title: {info['zenodo']['title']}")
            print(f"  Published: {info['zenodo']['date']}")
            print(f"  URL: {info['zenodo']['url']}")
    
    # Files with DOI but not on Zenodo (might be drafts or wrong DOI)
    if local_only:
        print("\n" + "=" * 80)
        print("FILES WITH DOI BUT NOT FOUND ON ZENODO")
        print("=" * 80)
        print("(These might be drafts, or the DOI might not be published yet)")
        for doi, info in sorted(local_only.items()):
            print(f"\nDOI: {doi}")
            print(f"  File: {info['file']}")
    
    # Papers on Zenodo but not in local files
    if zenodo_only:
        print("\n" + "=" * 80)
        print("PAPERS ON ZENODO BUT NOT IN LOCAL FILES")
        print("=" * 80)
        print("(These are published on Zenodo but not found in local directory)")
        for doi, info in sorted(zenodo_only.items(), key=lambda x: x[1]['date'], reverse=True):
            print(f"\nDOI: {doi}")
            print(f"  Title: {info['title']}")
            print(f"  Published: {info['date']}")
            print(f"  URL: {info['url']}")
    
    # Now find files that need DOIs by scanning actual files
    print("\n" + "=" * 80)
    print("FILES THAT NEED TO BE ADDED TO ZENODO")
    print("=" * 80)
    print()
    
    # Scan all LaTeX files to find ones without DOIs
    base_dir = Path(__file__).parent.parent
    files_needing_doi = []
    
    # Get all .tex files
    tex_files = list(base_dir.rglob('*.tex'))
    
    for tex_file in tex_files:
        relative_path = tex_file.relative_to(base_dir)
        
        # Only process files in SST-xx folders
        folder_parts = relative_path.parts
        if len(folder_parts) > 1:
            folder_name = folder_parts[0]
            # Check if folder matches SST-xx pattern (SST followed by digits)
            if not re.match(r'^SST-\d+', folder_name):
                continue
        
        # Only process files with \begin{document}
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if '\\begin{document}' not in content:
                continue
        except:
            continue
        
        # Exclude cover letters
        filename_lower = relative_path.name.lower()
        if 'coverletter' in filename_lower or 'cover_letter' in filename_lower:
            continue
        
        # Check if file has \title command
        if '\\title' not in content:
            continue
        
        # Check if file has DOI
        has_doi = False
        # Check preamble and abstract
        doc_start = content.find('\\begin{document}')
        abstract_end = content.find('\\end{abstract}')
        
        if abstract_end != -1 and (doc_start == -1 or abstract_end > doc_start):
            search_area = content[:abstract_end + len('\\end{abstract}')]
        elif doc_start != -1:
            search_area = content[:doc_start]
        else:
            search_area = content
        
        # Look for DOI pattern
        if re.search(r'10\.5281/zenodo\.\d+', search_area, re.IGNORECASE):
            # Check it's not a placeholder
            if not re.search(r'zenodo\.(xxx+|xxxx+|xxxxxxxx+)', search_area, re.IGNORECASE):
                has_doi = True
        
        if not has_doi:
            folder = str(relative_path.parent) if relative_path.parent != Path('.') else '.'
            # Skip files in root directory (not in SST-xx folder)
            if folder == '.':
                continue
            files_needing_doi.append({
                'folder': folder,
                'file': str(relative_path),
                'filename': relative_path.name
            })
    
    # Group by folder
    by_folder = defaultdict(list)
    for item in files_needing_doi:
        by_folder[item['folder']].append(item)
    
    print(f"Total files needing DOI: {len(files_needing_doi)}\n")
    
    for folder in sorted(by_folder.keys()):
        files = by_folder[folder]
        print(f"[{folder}]")
        for item in sorted(files, key=lambda x: x['filename']):
            print(f"  - {item['filename']}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Local files with DOI: {len(local_dois)}")
    print(f"Published on Zenodo: {len(zenodo_dois)}")
    print(f"Matched (already online): {len(matched)}")
    print(f"Files needing DOI: {len(files_needing_doi)}")
    print(f"Folders needing DOI: {len(by_folder)}")
    print()
    
    # Export to CSV
    output_csv = base_dir / 'zenodo_comparison.csv'
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Status', 'Folder', 'File', 'DOI', 'Zenodo_Title', 'Zenodo_URL', 'Published_Date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Matched files
        for doi, info in matched.items():
            writer.writerow({
                'Status': 'ONLINE',
                'Folder': info['local']['folder'],
                'File': info['local']['filename'],
                'DOI': doi,
                'Zenodo_Title': info['zenodo']['title'],
                'Zenodo_URL': info['zenodo']['url'],
                'Published_Date': info['zenodo']['date']
            })
        
        # Local only (DOI but not on Zenodo)
        # Check if they're drafts
        print("Checking which files with DOI are drafts on Zenodo...")
        token = read_token_from_zenodo_py()
        for doi, info in local_only.items():
            draft_info = check_if_draft_on_zenodo(doi, token) if token else None
            status = 'HAS_DOI_DRAFT' if draft_info and draft_info['is_draft'] else 'HAS_DOI_NOT_ONLINE'
            writer.writerow({
                'Status': status,
                'Folder': info['folder'],
                'File': info['filename'],
                'DOI': doi,
                'Zenodo_Title': draft_info['title'] if draft_info else '',
                'Zenodo_URL': draft_info['url'] if draft_info else '',
                'Published_Date': ''
            })
        
        # Files needing DOI
        for item in files_needing_doi:
            writer.writerow({
                'Status': 'NEEDS_DOI',
                'Folder': item['folder'],
                'File': item['filename'],
                'DOI': '',
                'Zenodo_Title': '',
                'Zenodo_URL': '',
                'Published_Date': ''
            })
    
    print(f"✓ Comparison exported to: {output_csv}")


if __name__ == '__main__':
    compare_local_zenodo()
