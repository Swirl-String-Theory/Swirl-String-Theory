#!/usr/bin/env python3
"""
Create Zenodo config files for all NEEDS_DOI files and get DOIs.
Excludes specified files from the CSV.
"""

import csv
import json
import re
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py

# Files to exclude (by line number in CSV, 1-indexed)
EXCLUDED_LINES = {52, 57, 58, 59, 60, 63, 67, 68, 72, 74, 75, 85, 86, 89, 90, 91}

def extract_metadata_from_latex(tex_file: Path) -> dict:
    """Extract metadata from LaTeX file."""
    metadata = {
        'title': '',
        'creators': [],
        'description': '',
        'keywords': [],
        'publication_date': ''
    }
    
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract title - try multiple formats
        # First try \title with potential line breaks and nested braces
        title_match = re.search(r'\\title\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
        if not title_match:
            # Try \papertitle command
            title_match = re.search(r'\\newcommand\{\\papertitle\}\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
        
        if title_match:
            title_text = title_match.group(1).strip()
            # Handle line breaks (\\)
            title_text = re.sub(r'\\\\', ' ', title_text)
            # Remove LaTeX commands but preserve their content
            # Remove \textbf{}, \textit{}, etc. but keep the content
            title_text = re.sub(r'\\(?:textbf|textit|emph|textsc|textmd|textup)\{([^}]+)\}', r'\1', title_text)
            # Remove other LaTeX commands
            title_text = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title_text)
            # Remove extra whitespace and newlines
            title_text = ' '.join(title_text.split())
            metadata['title'] = title_text
        
        # Extract author(s)
        author_match = re.search(r'\\author\{([^}]+)\}', content, re.DOTALL)
        if author_match:
            authors_str = author_match.group(1).strip()
            authors = []
            for author in authors_str.split('\\and'):
                author = author.strip()
                # Remove \thanks and other commands
                author_clean = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', author)
                if author_clean:
                    authors.append({'name': author_clean.strip()})
            if authors:
                metadata['creators'] = authors
        
        # Extract abstract
        abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Clean LaTeX commands (basic)
            abstract = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', abstract)
            metadata['description'] = abstract[:2000]  # Limit description
        
        # Extract keywords
        keywords_match = re.search(r'\\keywords\{([^}]+)\}', content, re.IGNORECASE)
        if keywords_match:
            keywords_str = keywords_match.group(1).strip()
            keywords = [k.strip() for k in keywords_str.split(',')]
            metadata['keywords'] = keywords
        
        # Extract date
        date_match = re.search(r'\\date\{([^}]+)\}', content)
        if date_match:
            metadata['publication_date'] = date_match.group(1).strip()
    
    except Exception as e:
        print(f"  Warning: Could not extract metadata: {e}")
    
    return metadata

def add_doi_to_latex(tex_file: Path, doi: str) -> bool:
    """Add DOI to LaTeX file as \\newcommand{\\paperdoi}{...}."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if DOI already exists (with placeholder or real DOI)
        doi_pattern = r'\\newcommand\{\\paperdoi\}\{[^}]+\}'
        if re.search(doi_pattern, content):
            # Replace existing DOI command
            replacement = r'\\newcommand{\\paperdoi}{' + doi + r'}'
            content = re.sub(
                doi_pattern,
                replacement,
                content,
                count=1  # Only replace first occurrence
            )
        else:
            # Find a good place to insert (after \documentclass or before \begin{document})
            doc_start = content.find('\\begin{document}')
            if doc_start != -1:
                # Insert before \begin{document}
                insert_pos = doc_start
                new_command = f'\\newcommand{{\\paperdoi}}{{{doi}}}\n\n'
                content = content[:insert_pos] + new_command + content[insert_pos:]
            else:
                # Append at end of file
                content += f'\n\\newcommand{{\\paperdoi}}{{{doi}}}\n'
        
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  Error adding DOI to LaTeX: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    base_dir = Path(__file__).parent.parent
    csv_file = base_dir / 'zenodo_comparison.csv'
    
    # Read CSV to get NEEDS_DOI files
    files_to_process = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2):  # Start at 2 (line 1 is header)
            if row['Status'] == 'NEEDS_DOI' and line_num not in EXCLUDED_LINES:
                folder = row['Folder']
                filename = row['File']
                if folder and folder != '.':
                    full_path = base_dir / folder / filename
                else:
                    full_path = base_dir / filename
                
                if full_path.exists():
                    files_to_process.append({
                        'folder': folder,
                        'filename': filename,
                        'path': full_path,
                        'line_num': line_num
                    })
    
    print("=" * 80)
    print(f"Creating Zenodo Config Files and Getting DOIs")
    print("=" * 80)
    print(f"\nFound {len(files_to_process)} files to process")
    print(f"Excluded {len(EXCLUDED_LINES)} files as requested\n")
    
    # Get Zenodo token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found in ../../zenodo.py")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for i, file_info in enumerate(files_to_process, 1):
        print(f"\n[{i}/{len(files_to_process)}] Processing: {file_info['folder']}\\{file_info['filename']}")
        
        tex_file = file_info['path']
        
        # Extract metadata
        print("  Extracting metadata...")
        metadata = extract_metadata_from_latex(tex_file)
        
        if not metadata.get('title'):
            print(f"  Warning: No title found, skipping...")
            error_count += 1
            continue
        
        # Create config file
        config_file = tex_file.with_suffix('.zenodo.json')
        config_data = {
            'title': metadata['title'],
            'creators': metadata.get('creators', [{'name': 'Oscar van der Velde'}]),
            'description': metadata.get('description', ''),
            'keywords': metadata.get('keywords', []),
            'publication_date': metadata.get('publication_date', ''),
            'doi': '',  # Will be filled after creating deposit
            'tex_file': str(tex_file.relative_to(base_dir)),
            'upload_type': 'publication',
            'publication_type': 'article'
        }
        
        # Save initial config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"  Created config: {config_file.name}")
        
        # Create draft deposit on Zenodo
        print("  Creating draft deposit on Zenodo...")
        try:
            # Create deposit and get full response
            url = f"{automation.base_url}/api/deposit/depositions"
            zenodo_metadata = {
                "metadata": {
                    "title": config_data['title'],
                    "creators": config_data['creators'],
                    "description": config_data['description'],
                    "keywords": config_data['keywords'],
                    "upload_type": "publication",
                    "publication_type": "article",
                    "access_right": "open",
                    "license": "cc-by-4.0",
                }
            }
            if config_data.get('publication_date'):
                zenodo_metadata['metadata']['publication_date'] = config_data['publication_date']
            
            import requests
            response = requests.post(url, json=zenodo_metadata, headers=automation.headers)
            
            if response.status_code == 201:
                deposit = response.json()
                deposit_id = str(deposit['id'])
                print(f"  Created deposit: {deposit_id}")
                
                # Get DOI from response
                # Drafts have prereserve_doi with doi field, or conceptdoi
                metadata = deposit.get('metadata', {})
                prereserve = metadata.get('prereserve_doi', {})
                if prereserve and 'doi' in prereserve:
                    doi = prereserve['doi']
                else:
                    doi = metadata.get('conceptdoi', '') or metadata.get('doi', '')
                
                # If still no DOI, try fetching again with retries
                if not doi:
                    import time
                    for retry in range(3):
                        time.sleep(1)
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
                
                if doi:
                    print(f"  ✓ Got DOI: {doi}")
                    
                    # Update config file with DOI
                    config_data['doi'] = doi
                    config_data['deposit_id'] = deposit_id
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2, ensure_ascii=False)
                    print(f"  Updated config with DOI")
                    
                    # Add DOI to LaTeX file
                    if add_doi_to_latex(tex_file, doi):
                        print(f"  ✓ Added DOI to LaTeX file")
                        success_count += 1
                    else:
                        print(f"  ✗ Failed to add DOI to LaTeX file")
                        error_count += 1
                else:
                    print(f"  Warning: No DOI returned from deposit")
                    error_count += 1
            else:
                print(f"  ✗ Failed to create deposit")
                error_count += 1
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(files_to_process)}")

if __name__ == '__main__':
    main()
