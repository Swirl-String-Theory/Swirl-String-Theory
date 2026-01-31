#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Zenodo DOI creation and paper upload workflow.

This script:
1. Reads paper metadata from LaTeX file or config
2. Creates a Zenodo draft deposit
3. Adds DOI to LaTeX file
4. Compiles LaTeX to PDF
5. Uploads PDF to Zenodo
6. Sets all metadata (title, description, keywords, etc.)
"""

import os
import re
import json
import subprocess
import requests
import sys
from pathlib import Path
from typing import Dict, Optional, List
import time

# Set output encoding to handle Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class ZenodoAutomation:
    def __init__(self, access_token: str, sandbox: bool = False):
        """
        Initialize Zenodo automation.
        
        Args:
            access_token: Zenodo API access token (get from https://zenodo.org/account/settings/applications/)
            sandbox: If True, use Zenodo Sandbox (for testing). If False, use production Zenodo.
        """
        self.access_token = access_token
        self.base_url = "https://sandbox.zenodo.org" if sandbox else "https://zenodo.org"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    
    def extract_metadata_from_latex(self, tex_file: Path) -> Dict:
        """Extract metadata from LaTeX file preamble."""
        metadata = {}
        
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title
            title_match = re.search(r'\\title\{([^}]+)\}', content)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            # Extract author(s)
            author_match = re.search(r'\\author\{([^}]+)\}', content, re.DOTALL)
            if author_match:
                authors_str = author_match.group(1).strip()
                # Parse authors (simple approach - can be enhanced)
                authors = []
                for author in authors_str.split('\\and'):
                    author = author.strip()
                    # Remove \thanks and other commands
                    author = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', author)
                    if author:
                        authors.append({'name': author.strip()})
                metadata['creators'] = authors
            
            # Extract abstract
            abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
            if abstract_match:
                abstract = abstract_match.group(1).strip()
                # Clean LaTeX commands
                abstract = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', abstract)
                metadata['description'] = abstract[:500]  # Limit description length
            
            # Extract keywords (if present)
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
            print(f"Warning: Could not extract all metadata from LaTeX: {e}")
        
        return metadata
    
    def create_draft_deposit(self, metadata: Dict) -> Optional[str]:
        """Create a new draft deposit on Zenodo and return the deposit ID."""
        url = f"{self.base_url}/api/deposit/depositions"
        
        # Prepare metadata for Zenodo
        zenodo_metadata = {
            "metadata": {
                "title": metadata.get('title', 'Untitled'),
                "creators": metadata.get('creators', [{'name': 'Unknown'}]),
                "description": metadata.get('description', ''),
                "keywords": metadata.get('keywords', []),
                "upload_type": metadata.get('upload_type', 'publication'),
                "publication_type": metadata.get('publication_type', 'article'),
                "publication_date": metadata.get('publication_date', ''),
                "access_right": metadata.get('access_right', 'open'),
                "license": metadata.get('license', 'cc-by-4.0'),
            }
        }
        
        # Add optional fields
        if 'doi' in metadata:
            zenodo_metadata['metadata']['doi'] = metadata['doi']
        if 'related_identifiers' in metadata:
            zenodo_metadata['metadata']['related_identifiers'] = metadata['related_identifiers']
        
        response = requests.post(url, json=zenodo_metadata, headers=self.headers)
        
        if response.status_code == 201:
            deposit = response.json()
            deposit_id = str(deposit['id'])
            print(f"[OK] Created draft deposit: {deposit_id}")
            print(f"  Draft URL: {deposit['links']['html']}")
            return deposit_id
        else:
            print(f"[ERROR] Failed to create deposit: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
    
    def get_deposit_doi(self, deposit_id: str) -> Optional[str]:
        """Get the DOI for a draft deposit."""
        url = f"{self.base_url}/api/deposit/depositions/{deposit_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            deposit = response.json()
            # Draft deposits have a concept DOI that becomes the actual DOI on publish
            if 'doi' in deposit.get('metadata', {}):
                return deposit['metadata']['doi']
            elif 'conceptdoi' in deposit.get('metadata', {}):
                return deposit['metadata']['conceptdoi']
        return None
    
    def add_doi_to_latex(self, tex_file: Path, doi: str) -> bool:
        """Add DOI to LaTeX file in the standard format."""
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if DOI already exists
            if re.search(r'10\.5281/zenodo\.\d+', content):
                print(f"  Warning: DOI already exists in {tex_file}")
                return False
            
            # Find the preamble (before \begin{document})
            doc_start = content.find('\\begin{document}')
            if doc_start == -1:
                print(f"  Warning: Could not find \\begin{{document}} in {tex_file}")
                return False
            
            preamble = content[:doc_start]
            
            # Add DOI command if \newcommand{\paperdoi} doesn't exist
            if '\\newcommand{\\paperdoi}' not in preamble:
                # Find a good place to insert (after title/author, before document)
                insert_pos = doc_start
                
                # Try to insert after \author
                author_match = re.search(r'\\author\{[^}]+\}', preamble, re.DOTALL)
                if author_match:
                    insert_pos = author_match.end()
                
                doi_command = f"\n\\newcommand{{\\paperdoi}}{{{doi}}}\n"
                content = content[:insert_pos] + doi_command + content[insert_pos:]
            else:
                # Update existing DOI command
                content = re.sub(
                    r'\\newcommand\{\\paperdoi\}\{[^}]+\}',
                    f'\\newcommand{{\\paperdoi}}{{{doi}}}',
                    content
                )
            
            # Write back
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[OK] Added DOI to {tex_file}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to add DOI to LaTeX: {e}")
            return False
    
    def compile_latex(self, tex_file: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Compile LaTeX file to PDF."""
        if output_dir is None:
            output_dir = tex_file.parent
        
        pdf_file = output_dir / tex_file.stem + '.pdf'
        
        print(f"  Compiling LaTeX to PDF...")
        
        # Run pdflatex (you may need to adjust this based on your LaTeX setup)
        try:
            # Change to the directory containing the tex file
            work_dir = tex_file.parent
            tex_name = tex_file.name
            
            # Run pdflatex twice (for references, etc.)
            for run in [1, 2]:
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(output_dir), tex_name],
                    cwd=work_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"[ERROR] LaTeX compilation failed (run {run}):")
                    print(result.stderr)
                    return None
            
            if pdf_file.exists():
                print(f"[OK] PDF created: {pdf_file}")
                return pdf_file
            else:
                print(f"[ERROR] PDF file not found after compilation")
                return None
                
        except FileNotFoundError:
            print("[ERROR] pdflatex not found. Please install LaTeX distribution.")
            return None
        except Exception as e:
            print(f"[ERROR] Compilation error: {e}")
            return None
    
    def upload_file_to_deposit(self, deposit_id: str, file_path: Path) -> bool:
        """Upload a file to a Zenodo deposit."""
        # Get upload URL
        url = f"{self.base_url}/api/deposit/depositions/{deposit_id}/files"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to get upload URL: {response.status_code}")
            return False
        
        # Create new file upload
        data = {'name': file_path.name}
        files = {'file': open(file_path, 'rb')}
        upload_headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        # Remove Content-Type for file upload
        upload_headers.pop('Content-Type', None)
        
        response = requests.post(url, data=data, files=files, headers=upload_headers)
        files['file'].close()
        
        if response.status_code == 201:
            print(f"[OK] Uploaded {file_path.name} to deposit")
            return True
        else:
            print(f"[ERROR] Failed to upload file: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    
    def update_deposit_metadata(self, deposit_id: str, metadata: Dict) -> bool:
        """Update metadata for a deposit."""
        url = f"{self.base_url}/api/deposit/depositions/{deposit_id}"
        
        zenodo_metadata = {
            "metadata": {
                "title": metadata.get('title', 'Untitled'),
                "creators": metadata.get('creators', [{'name': 'Unknown'}]),
                "description": metadata.get('description', ''),
                "keywords": metadata.get('keywords', []),
                "upload_type": metadata.get('upload_type', 'publication'),
                "publication_type": metadata.get('publication_type', 'article'),
                "publication_date": metadata.get('publication_date', ''),
                "access_right": metadata.get('access_right', 'open'),
                "license": metadata.get('license', 'cc-by-4.0'),
            }
        }
        
        # Add language if present
        if metadata.get('language'):
            zenodo_metadata['metadata']['language'] = metadata['language']
        
        response = requests.put(url, json=zenodo_metadata, headers=self.headers)
        
        if response.status_code == 200:
            print(f"[OK] Updated deposit metadata")
            return True
        else:
            print(f"[ERROR] Failed to update metadata: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    
    def publish_deposit(self, deposit_id: str) -> bool:
        """Publish a draft deposit (makes it public and assigns final DOI)."""
        url = f"{self.base_url}/api/deposit/depositions/{deposit_id}/actions/publish"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 202:
            deposit = response.json()
            print(f"[OK] Published deposit!")
            print(f"  DOI: {deposit.get('doi', 'N/A')}")
            print(f"  URL: {deposit.get('links', {}).get('html', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Failed to publish: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    
    def full_workflow(self, tex_file: Path, metadata: Optional[Dict] = None, 
                     publish: bool = False, compile_pdf: bool = True) -> Optional[str]:
        """
        Complete workflow: create deposit, add DOI, compile, upload, set metadata.
        
        Args:
            tex_file: Path to LaTeX file
            metadata: Optional metadata dict (if None, extracted from LaTeX)
            publish: If True, publish the deposit immediately (default: False, creates draft)
            compile_pdf: If True, compile LaTeX to PDF and upload (default: True)
        
        Returns:
            Deposit ID if successful, None otherwise
        """
        print(f"\n{'='*60}")
        print(f"Zenodo Automation Workflow")
        print(f"{'='*60}\n")
        print(f"Processing: {tex_file}\n")
        
        # Step 1: Extract or use provided metadata
        if metadata is None:
            print("Step 1: Extracting metadata from LaTeX...")
            metadata = self.extract_metadata_from_latex(tex_file)
        else:
            print("Step 1: Using provided metadata...")
        
        if not metadata.get('title'):
            print("[ERROR] Error: No title found. Please provide metadata.")
            return None
        
        # Step 2: Create draft deposit
        print("\nStep 2: Creating Zenodo draft deposit...")
        deposit_id = self.create_draft_deposit(metadata)
        if not deposit_id:
            return None
        
        # Step 3: Get DOI
        print("\nStep 3: Getting DOI...")
        time.sleep(2)  # Wait a moment for DOI to be assigned
        doi = self.get_deposit_doi(deposit_id)
        if not doi:
            print("  Warning: Could not get DOI yet. It will be assigned on publish.")
            doi = f"10.5281/zenodo.{deposit_id}"  # Temporary placeholder
        
        print(f"  DOI: {doi}")
        
        # Step 4: Add DOI to LaTeX
        print("\nStep 4: Adding DOI to LaTeX file...")
        self.add_doi_to_latex(tex_file, doi)
        
        # Step 5: Compile PDF (if requested)
        pdf_file = None
        if compile_pdf:
            print("\nStep 5: Compiling LaTeX to PDF...")
            pdf_file = self.compile_latex(tex_file)
            if pdf_file:
                # Step 6: Upload PDF
                print("\nStep 6: Uploading PDF to Zenodo...")
                self.upload_file_to_deposit(deposit_id, pdf_file)
        
        # Step 7: Update metadata (in case we want to add more details)
        print("\nStep 7: Finalizing metadata...")
        self.update_deposit_metadata(deposit_id, metadata)
        
        # Step 8: Publish (if requested)
        if publish:
            print("\nStep 8: Publishing deposit...")
            self.publish_deposit(deposit_id)
        else:
            print(f"\n[OK] Draft deposit created successfully!")
            print(f"  Deposit ID: {deposit_id}")
            print(f"  Draft URL: {self.base_url}/deposit/{deposit_id}")
            print(f"  You can review and publish it manually on Zenodo.")
        
        return deposit_id
    
    def list_deposits(self, published_only: bool = False, limit: int = 100) -> List[Dict]:
        """
        List all deposits (published and/or drafts).
        
        Args:
            published_only: If True, only return published deposits. If False, return all.
            limit: Maximum number of deposits to return (default: 100)
        
        Returns:
            List of deposit dictionaries with metadata
        """
        url = f"{self.base_url}/api/deposit/depositions"
        params = {
            'size': limit,
            'sort': 'mostrecent'
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to list deposits: {response.status_code}")
            print(f"  Error: {response.text}")
            return []
        
        deposits = response.json()
        
        if published_only:
            deposits = [d for d in deposits if d.get('submitted', False)]
        
        return deposits
    
    def get_deposit_info(self, deposit_id: str) -> Optional[Dict]:
        """Get detailed information about a specific deposit."""
        url = f"{self.base_url}/api/deposit/depositions/{deposit_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] Failed to get deposit info: {response.status_code}")
            return None
    
    def list_published_papers(self, limit: int = 100) -> List[Dict]:
        """Limit is capped at 100 by Zenodo API."""
        if limit > 100:
            limit = 100
        """
        List all published papers with their DOIs.
        
        Returns:
            List of dictionaries with: id, title, doi, url, publication_date, creators
        """
        deposits = self.list_deposits(published_only=True, limit=limit)
        
        papers = []
        for deposit in deposits:
            metadata = deposit.get('metadata', {})
            paper_info = {
                'id': deposit.get('id'),
                'title': metadata.get('title', 'Untitled'),
                'doi': metadata.get('doi', 'N/A'),
                'conceptdoi': metadata.get('conceptdoi', 'N/A'),
                'url': deposit.get('links', {}).get('html', 'N/A'),
                'publication_date': metadata.get('publication_date', 'N/A'),
                'creators': [c.get('name', 'Unknown') for c in metadata.get('creators', [])],
                'keywords': metadata.get('keywords', []),
                'submitted': deposit.get('submitted', False),
                'state': deposit.get('state', 'unknown')
            }
            papers.append(paper_info)
        
        return papers
    
    def print_published_papers(self, limit: int = 100):
        """Print a formatted list of all published papers."""
        papers = self.list_published_papers(limit=limit)
        
        if not papers:
            print("No published papers found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Published Papers on Zenodo ({len(papers)} found)")
        print(f"{'='*80}\n")
        
        for i, paper in enumerate(papers, 1):
            title = paper['title']
            # Handle Unicode characters safely
            try:
                print(f"{i}. {title}")
            except UnicodeEncodeError:
                print(f"{i}. {title.encode('ascii', 'replace').decode('ascii')}")
            print(f"   DOI: {paper['doi']}")
            if paper['conceptdoi'] != 'N/A' and paper['conceptdoi'] != paper['doi']:
                print(f"   Concept DOI: {paper['conceptdoi']}")
            print(f"   Authors: {', '.join(paper['creators'])}")
            print(f"   Date: {paper['publication_date']}")
            print(f"   URL: {paper['url']}")
            if paper['keywords']:
                print(f"   Keywords: {', '.join(paper['keywords'])}")
            print()


def read_token_from_zenodo_py() -> Optional[str]:
    """Read Zenodo API token from zenodo.py file in parent directory of SwirlStringTheory."""
    # Scripts are in zenodo_tools/, so go up two levels to get to parent of SwirlStringTheory
    # zenodo_tools/ -> ../ -> SwirlStringTheory/ -> ../ -> parent of SwirlStringTheory/
    script_dir = Path(__file__).parent  # zenodo_tools/
    parent_dir = script_dir.parent.parent  # ../../ (parent of SwirlStringTheory/)
    zenodo_py = parent_dir / 'zenodo.py'
    
    if not zenodo_py.exists():
        return None
    
    try:
        # Read the file and extract the key variable
        with open(zenodo_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for key = "..." or key="..." (with or without quotes)
        match = re.search(r'key\s*=\s*["\']?([^"\'\s]+)["\']?', content)
        if match:
            return match.group(1).strip()
        
        # Alternative: try to execute and get the key (if it's a Python file)
        # This is safer than eval
        namespace = {}
        exec(compile(content, str(zenodo_py), 'exec'), namespace)
        if 'key' in namespace:
            return str(namespace['key']).strip('"\'')
        
    except Exception as e:
        print(f"Warning: Could not read token from {zenodo_py}: {e}")
    
    return None


def main():
    """Example usage."""
    import argparse
    
    # Try to read default token from zenodo.py
    default_token = read_token_from_zenodo_py()
    
    parser = argparse.ArgumentParser(description='Automate Zenodo DOI creation and paper upload')
    parser.add_argument('tex_file', type=Path, nargs='?', help='Path to LaTeX file')
    parser.add_argument('--token', default=default_token, 
                       help=f'Zenodo API access token (default: read from ../../zenodo.py)')
    parser.add_argument('--sandbox', action='store_true', help='Use Zenodo Sandbox (for testing)')
    parser.add_argument('--publish', action='store_true', help='Publish immediately (default: create draft)')
    parser.add_argument('--no-compile', action='store_true', help='Skip PDF compilation')
    parser.add_argument('--metadata', type=Path, help='Path to JSON file with metadata')
    parser.add_argument('--list', action='store_true', help='List all published papers with DOIs')
    parser.add_argument('--list-all', action='store_true', help='List all deposits (including drafts)')
    parser.add_argument('--limit', type=int, default=100, help='Limit number of results when listing (default: 100)')
    
    args = parser.parse_args()
    
    # Check if token is available
    if not args.token:
        print("Error: Zenodo API access token is required.")
        print("  Option 1: Provide --token YOUR_TOKEN")
        print("  Option 2: Create ../../zenodo.py with: key = 'YOUR_TOKEN'")
        exit(1)
    
    # Initialize automation
    automation = ZenodoAutomation(args.token, sandbox=args.sandbox)
    
    # Handle list commands
    if args.list:
        automation.print_published_papers(limit=args.limit)
        exit(0)
    
    if args.list_all:
        deposits = automation.list_deposits(published_only=False, limit=args.limit)
        print(f"\n{'='*80}")
        print(f"All Deposits ({len(deposits)} found)")
        print(f"{'='*80}\n")
        
        for i, deposit in enumerate(deposits, 1):
            metadata = deposit.get('metadata', {})
            state = 'Published' if deposit.get('submitted', False) else 'Draft'
            title = metadata.get('title', 'Untitled')
            # Handle Unicode characters safely
            try:
                print(f"{i}. [{state}] {title}")
            except UnicodeEncodeError:
                print(f"{i}. [{state}] {title.encode('ascii', 'replace').decode('ascii')}")
            if deposit.get('submitted'):
                print(f"   DOI: {metadata.get('doi', 'N/A')}")
            else:
                print(f"   Deposit ID: {deposit.get('id')}")
            print(f"   URL: {deposit.get('links', {}).get('html', 'N/A')}")
            print()
        exit(0)
    
    # Require tex_file for workflow
    if not args.tex_file:
        parser.error("tex_file is required unless using --list or --list-all")
    
    # Load metadata if provided
    metadata = None
    if args.metadata:
        with open(args.metadata, 'r') as f:
            metadata = json.load(f)
    
    # Run workflow
    deposit_id = automation.full_workflow(
        args.tex_file,
        metadata=metadata,
        publish=args.publish,
        compile_pdf=not args.no_compile
    )
    
    if deposit_id:
        print(f"\n{'='*60}")
        print("Workflow completed successfully!")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print("Workflow failed!")
        print(f"{'='*60}\n")
        exit(1)


if __name__ == '__main__':
    main()
