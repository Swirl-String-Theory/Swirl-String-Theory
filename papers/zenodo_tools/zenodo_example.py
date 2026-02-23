#!/usr/bin/env python3
"""
Example script showing how to use the Zenodo automation programmatically.
"""

from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py

# Configuration
# Try to read token from ../../zenodo.py, otherwise use hardcoded value
ZENODO_TOKEN = read_token_from_zenodo_py() or "YOUR_TOKEN_HERE"  # Replace with your actual token if not in zenodo.py
USE_SANDBOX = True  # Set to False for production

if ZENODO_TOKEN == "YOUR_TOKEN_HERE":
    print("Warning: Using placeholder token. Please set key in ../../zenodo.py or update this script.")

# Initialize
automation = ZenodoAutomation(ZENODO_TOKEN, sandbox=USE_SANDBOX)

# Example 1: Full automated workflow
tex_file = Path("SST-40_Photons_and_Lazers/SST-40_Photon_and_Lasers_EN.tex")

# Option A: Let it extract metadata from LaTeX
deposit_id = automation.full_workflow(
    tex_file,
    metadata=None,  # Will extract from LaTeX
    publish=False,  # Create draft (set to True to publish immediately)
    compile_pdf=True
)

# Option B: Provide custom metadata
custom_metadata = {
    "title": "Photons and Lasers: A Swirl-String Theory Perspective",
    "creators": [
        {
            "name": "Omar Iskandarani",
            "affiliation": "Independent Researcher, Groningen, The Netherlands",
            "orcid": "0009-0006-1686-3961"
        }
    ],
    "description": "This paper explores the nature of photons and lasers from the perspective of Swirl-String Theory...",
    "keywords": ["physics", "optics", "photons", "lasers", "swirl-string theory"],
    "publication_type": "article",
    "publication_date": "2026-01-27",
    "access_right": "open",
    "license": "cc-by-4.0"
}

deposit_id = automation.full_workflow(
    tex_file,
    metadata=custom_metadata,
    publish=False,
    compile_pdf=True
)

# Example 2: Step-by-step workflow (more control)
if deposit_id:
    # Get the DOI
    doi = automation.get_deposit_doi(deposit_id)
    print(f"DOI: {doi}")
    
    # Add DOI to LaTeX (if not already done)
    automation.add_doi_to_latex(tex_file, doi)
    
    # Compile PDF
    pdf_file = automation.compile_latex(tex_file)
    
    # Upload PDF
    if pdf_file:
        automation.upload_file_to_deposit(deposit_id, pdf_file)
    
    # Update metadata
    automation.update_deposit_metadata(deposit_id, custom_metadata)
    
    # When ready, publish
    # automation.publish_deposit(deposit_id)

print(f"\nDraft deposit created: {deposit_id}")
print(f"Review at: https://sandbox.zenodo.org/deposit/{deposit_id}")
