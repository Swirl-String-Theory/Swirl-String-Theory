#!/usr/bin/env python3
"""
List all published papers from Zenodo with their DOIs.

Usage:
    python list_zenodo_papers.py [--sandbox] [--limit 100] [--csv output.csv]
"""

import argparse
import csv
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py


def main():
    parser = argparse.ArgumentParser(description='List published papers from Zenodo')
    parser.add_argument('--token', default=None, help='Zenodo API access token')
    parser.add_argument('--sandbox', action='store_true', help='Use Zenodo Sandbox')
    parser.add_argument('--limit', type=int, default=100, help='Maximum number of papers to list')
    parser.add_argument('--csv', type=Path, help='Export results to CSV file')
    parser.add_argument('--json', type=Path, help='Export results to JSON file')
    
    args = parser.parse_args()
    
    # Get token
    token = args.token or read_token_from_zenodo_py()
    if not token:
        print("Error: Zenodo API access token is required.")
        print("  Option 1: Provide --token YOUR_TOKEN")
        print("  Option 2: Create ../../zenodo.py with: key = 'YOUR_TOKEN'")
        exit(1)
    
    # Initialize
    automation = ZenodoAutomation(token, sandbox=args.sandbox)
    
    # Get papers
    print("Fetching published papers from Zenodo...")
    papers = automation.list_published_papers(limit=args.limit)
    
    if not papers:
        print("No published papers found.")
        return
    
    # Print to console
    automation.print_published_papers(limit=args.limit)
    
    # Export to CSV if requested
    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'doi', 'conceptdoi', 'url', 
                                                   'publication_date', 'creators', 'keywords'])
            writer.writeheader()
            for paper in papers:
                writer.writerow({
                    'id': paper['id'],
                    'title': paper['title'],
                    'doi': paper['doi'],
                    'conceptdoi': paper['conceptdoi'],
                    'url': paper['url'],
                    'publication_date': paper['publication_date'],
                    'creators': ', '.join(paper['creators']),
                    'keywords': ', '.join(paper['keywords'])
                })
        print(f"✓ Exported {len(papers)} papers to {args.csv}")
    
    # Export to JSON if requested
    if args.json:
        import json
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        print(f"✓ Exported {len(papers)} papers to {args.json}")


if __name__ == '__main__':
    main()
