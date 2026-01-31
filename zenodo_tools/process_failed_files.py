#!/usr/bin/env python3
"""Process files that failed in the initial run (those without titles found)."""

import csv
import json
import re
from pathlib import Path
from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py
from create_zenodo_configs import extract_metadata_from_latex, add_doi_to_latex

# Files that failed (from the 6 errors)
FAILED_FILES = [
    ('SST-22_Hydrodynamic_Origin_Hydrogen_Old', 'Hydrodynamic_Origin_of_the_Hydrogen_Ground_State.tex'),
    ('SST-22_Hydrodynamic_Origin_Hydrogen_Old', 'SST-22_Hydrodynamic_Origin_of_the_Hydrogen_Ground_State.tex'),
    ('SST-25_Hydrogenic_Orbitals', 'SST-25_Hydrogenic_Orbitals.tex'),
    ('SST-30_Invariant_Atom_Masses', 'SST-30_Invariant_Atom_Masses.tex'),
    ('SST-32_Canonical_Fluid_Reformulation_of_Relativity_and_Quantum_Structure', 'SST-32_Canonical_Fluid_Reformulation_of_Relativity_and_Quantum_Structure_long.tex'),
    ('SST-33_Heat_Transport', 'SST-Thermodynamics_of_the_Swirl_Condensate.tex'),
]

# Also process the files the user mentioned
USER_MENTIONED = [
    ('SST-58_vacuum_stress_energy_engineering', 'SST-58_vacuum_stress_energy_engineering.tex'),
    ('SST-57_FermionMasses', 'SST-57_FermionMasses.tex'),
    ('SST-41_Water_and_time', 'SST-41_VAM-17.7Fluid_Fine-Structure.tex'),
    ('SST-40_Photons_and_Lazers', 'SST-40_Photon_and_Lasers_EN.tex'),
    ('SST-18_Unifying_EM_Gravity', 'SST-18_Unifying_Electromagnetism_Gravity_and_Quantum_Geometry_via_Incompressible_Hydrodynamics.tex'),
]

ALL_FILES = FAILED_FILES + USER_MENTIONED

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print(f"Processing {len(ALL_FILES)} files")
    print("=" * 80)
    print()
    
    # Get Zenodo token
    token = read_token_from_zenodo_py()
    if not token:
        print("Error: No Zenodo token found in ../../zenodo.py")
        return
    
    automation = ZenodoAutomation(token, sandbox=False)
    
    success_count = 0
    error_count = 0
    
    for i, (folder, filename) in enumerate(ALL_FILES, 1):
        print(f"\n[{i}/{len(ALL_FILES)}] Processing: {folder}\\{filename}")
        
        tex_file = base_dir / folder / filename
        
        if not tex_file.exists():
            print(f"  File not found, skipping...")
            error_count += 1
            continue
        
        # Extract metadata
        print("  Extracting metadata...")
        metadata = extract_metadata_from_latex(tex_file)
        
        if not metadata.get('title'):
            print(f"  Warning: No title found, skipping...")
            error_count += 1
            continue
        
        print(f"  Title: {metadata['title']}")
        
        # Check if config already exists
        config_file = tex_file.with_suffix('.zenodo.json')
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            if config_data.get('doi'):
                print(f"  Config already exists with DOI: {config_data['doi']}")
                # Check if DOI is in LaTeX file
                with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if config_data['doi'] in content:
                    print(f"  DOI already in LaTeX file, skipping...")
                    success_count += 1
                    continue
                else:
                    # Add DOI to LaTeX
                    if add_doi_to_latex(tex_file, config_data['doi']):
                        print(f"  ✓ Added existing DOI to LaTeX file")
                        success_count += 1
                        continue
        
        # Create config file
        config_data = {
            'title': metadata['title'],
            'creators': metadata.get('creators', [{'name': 'Oscar van der Velde'}]),
            'description': metadata.get('description', ''),
            'keywords': metadata.get('keywords', []),
            'publication_date': metadata.get('publication_date', ''),
            'doi': '',
            'tex_file': str(tex_file.relative_to(base_dir)),
            'upload_type': 'publication',
            'publication_type': 'article'
        }
        
        # Create draft deposit on Zenodo
        print("  Creating draft deposit on Zenodo...")
        try:
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
                metadata_zenodo = deposit.get('metadata', {})
                prereserve = metadata_zenodo.get('prereserve_doi', {})
                if prereserve and 'doi' in prereserve:
                    doi = prereserve['doi']
                else:
                    doi = metadata_zenodo.get('conceptdoi', '') or metadata_zenodo.get('doi', '')
                
                if not doi:
                    import time
                    time.sleep(1)
                    for retry in range(3):
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
                        time.sleep(1)
                
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
                print(f"  ✗ Failed to create deposit: {response.status_code}")
                print(f"  Error: {response.text}")
                error_count += 1
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(ALL_FILES)}")

if __name__ == '__main__':
    main()
