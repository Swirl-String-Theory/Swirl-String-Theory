#!/usr/bin/env python3
"""Check recent Zenodo deposits to see what was created."""

import sys
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

def main():
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    print("=" * 80)
    print("Checking Recent Zenodo Deposits")
    print("=" * 80)
    print()
    
    # Get all deposits (including drafts)
    print("Fetching all deposits...")
    all_deposits = automation.list_deposits(published_only=False, limit=100)
    
    print(f"Total deposits found: {len(all_deposits)}")
    print()
    
    # Count by status
    published = [d for d in all_deposits if d.get('submitted', False)]
    drafts = [d for d in all_deposits if not d.get('submitted', False)]
    
    print(f"Published: {len(published)}")
    print(f"Drafts: {len(drafts)}")
    print()
    
    # Show recent drafts (last 20)
    print("=" * 80)
    print("Recent Draft Deposits (last 20)")
    print("=" * 80)
    print()
    
    # Sort by ID (higher = newer)
    drafts_sorted = sorted(drafts, key=lambda x: int(x.get('id', 0)), reverse=True)
    
    for i, deposit in enumerate(drafts_sorted[:20], 1):
        deposit_id = deposit.get('id', 'N/A')
        metadata = deposit.get('metadata', {})
        title = metadata.get('title', 'Untitled')
        doi = metadata.get('prereserve_doi', {}).get('doi', '') or metadata.get('conceptdoi', '') or metadata.get('doi', 'N/A')
        created = deposit.get('created', 'N/A')
        
        print(f"{i}. ID: {deposit_id}")
        print(f"   Title: {title[:80]}...")
        print(f"   DOI: {doi}")
        print(f"   Created: {created}")
        print()
    
    if len(drafts_sorted) > 20:
        print(f"... and {len(drafts_sorted) - 20} more drafts")
    
    print("=" * 80)
    print("Note: Drafts can be deleted from Zenodo if they were created incorrectly.")
    print("=" * 80)

if __name__ == '__main__':
    main()
