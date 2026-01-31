#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if all SST-xx folders have matching .zenodo.json files for their .tex files,
and validate that all values in existing .zenodo.json files are properly set.
For missing description/keywords, extract from LaTeX abstract or first section.
"""

import json
import re
import sys
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
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

def convert_math_delimiters(text: str) -> str:
    """Convert LaTeX math delimiters to Zenodo/MathJax format.
    
    Converts:
    - $...$ to \(...\) for inline math
    - $$...$$ to \[...\] for display math
    - \[...\] to \[...\] (already correct)
    - Handles edge cases like incomplete $ at end of string
    """
    if not text:
        return text
    
    # First, convert display math $$...$$ to \[...\]
    # Handle both complete $$...$$ and incomplete $$ at end
    text = re.sub(r'\$\$([^$]*?)\$\$', r'\\[\1\\]', text, flags=re.DOTALL)
    # Handle incomplete $$ at end (shouldn't happen but just in case)
    text = re.sub(r'\$\$([^$]*?)$', r'\\[\1\\]', text, flags=re.DOTALL)
    # Remove standalone $$ (empty math)
    text = re.sub(r'\$\$', '', text)
    
    # Convert inline math $...$ to \(...\)
    # Match $...$ but avoid matching $$ (already handled above)
    # This regex matches $ not preceded or followed by $
    text = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', r'\\(\1\\)', text)
    
    # Handle incomplete $ at end of string (remove it as it's likely a typo)
    # But be careful - only remove if it's clearly incomplete (not part of text)
    text = re.sub(r'(?<!\\)\$(?!\()', '', text)
    
    return text

def extract_abstract_from_latex(tex_file: Path) -> Optional[str]:
    """Extract abstract from LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to find abstract
        abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Convert math delimiters before cleaning
            abstract = convert_math_delimiters(abstract)
            # Clean LaTeX commands (basic cleaning) - but preserve \( and \)
            # Remove LaTeX commands but keep math delimiters
            abstract = re.sub(r'\\(?!\(|\)|\[|\])([a-zA-Z]+)\{?[^}]*\}?', '', abstract)
            # Remove extra whitespace
            abstract = ' '.join(abstract.split())
            return abstract[:2000]  # Limit length
        
        return None
    except Exception as e:
        print(f"    Error reading LaTeX file: {e}")
        return None

def extract_first_section_from_latex(tex_file: Path) -> Optional[str]:
    """Extract first section content from LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find \begin{document}
        doc_start = content.find('\\begin{document}')
        if doc_start == -1:
            return None
        
        # Get content after \begin{document}
        body = content[doc_start:]
        
        # Find first \section or \section* and get content up to next section or end
        section_match = re.search(r'\\section\*?\{([^}]+)\}(.*?)(?=\\section|\\subsection|\\end\{document\}|$)', body, re.DOTALL)
        if section_match:
            section_content = section_match.group(2).strip()
            # Remove LaTeX environments and commands more carefully
            # Remove equation environments
            section_content = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', r'\1', section_content, flags=re.DOTALL)
            section_content = re.sub(r'\\begin\{align\}(.*?)\\end\{align\}', r'\1', section_content, flags=re.DOTALL)
            # Remove labels and references
            section_content = re.sub(r'\\label\{[^}]+\}', '', section_content)
            section_content = re.sub(r'\\ref\{[^}]+\}', '', section_content)
            # Remove LaTeX commands but keep text
            section_content = re.sub(r'\\[a-zA-Z]+\{?[^{}]*\}?', '', section_content)
            # Convert math delimiters before removing
            section_content = convert_math_delimiters(section_content)
            # Remove LaTeX commands but preserve \( and \)
            section_content = re.sub(r'\\(?!\(|\)|\[|\])([a-zA-Z]+)\{?[^}]*\}?', '', section_content)
            # Remove extra whitespace
            section_content = ' '.join(section_content.split())
            # Get first few sentences (up to 500 chars or first 3 sentences)
            sentences = re.split(r'[.!?]\s+', section_content)
            if sentences:
                result = '. '.join(sentences[:3]) + '.'
                if len(result) > 500:
                    result = result[:500] + '...'
                return result
        
        return None
    except Exception as e:
        print(f"    Error reading LaTeX file: {e}")
        return None

def extract_keywords_from_latex(tex_file: Path) -> List[str]:
    """Extract keywords from LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to find \keywords command
        keywords_match = re.search(r'\\keywords\{([^}]+)\}', content, re.IGNORECASE)
        if keywords_match:
            keywords_str = keywords_match.group(1).strip()
            keywords = [k.strip() for k in keywords_str.split(',')]
            return [k for k in keywords if k]  # Remove empty strings
        
        return []
    except Exception as e:
        print(f"    Error reading LaTeX file: {e}")
        return []

def generate_keywords_from_text(text: str) -> List[str]:
    """Generate keywords from text content (simple approach)."""
    if not text:
        return []
    
    # Common stop words to exclude
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'we', 'our', 'their', 'its', 'it', 'they', 'them', 'which', 'what', 'where', 'when', 'why', 'how'}
    
    # Extract potential keywords (words with capital letters or technical terms)
    words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]+[A-Z][a-z]+\b', text)
    
    # Filter and count
    keywords = []
    word_count = {}
    for word in words:
        word_lower = word.lower()
        if word_lower not in stop_words and len(word) > 3:
            word_count[word_lower] = word_count.get(word_lower, 0) + 1
    
    # Get top keywords (appearing at least 2 times)
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, count in sorted_words[:10] if count >= 2]
    
    return keywords[:10]  # Limit to 10 keywords

def find_all_sst_folders(base_dir: Path) -> List[Path]:
    """Find all SST-xx folders."""
    sst_folders = []
    for folder in base_dir.iterdir():
        if folder.is_dir() and re.match(r'^SST-\d+', folder.name):
            sst_folders.append(folder)
    return sorted(sst_folders)

def find_tex_files_in_folder(folder: Path) -> List[Path]:
    """Find all .tex files in a folder that match SST-xx pattern."""
    tex_files = []
    # Skip cover letters and similar files
    skip_patterns = [
        r'coverletter',
        r'Coverletter',
        r'CoverLetter',
        r'EditorialResponse',
        r'DIFFERNCE',
        r'Old version',
    ]
    
    for tex_file in folder.glob('*.tex'):
        # Check if it matches SST-xx pattern (not cover letters, etc.)
        if re.match(r'^SST-\d+', tex_file.stem):
            # Skip cover letters
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, tex_file.stem, re.IGNORECASE):
                    should_skip = True
                    break
            if not should_skip:
                tex_files.append(tex_file)
    return tex_files

def extract_doi_from_latex(tex_file: Path) -> Optional[str]:
    """Extract DOI from LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Look for \paperdoi{10.5281/zenodo.xxx}
        doi_match = re.search(r'\\paperdoi\{([^}]+)\}', content)
        if doi_match:
            return doi_match.group(1)
        
        # Look for \newcommand{\paperdoi}{10.5281/zenodo.xxx}
        doi_match = re.search(r'\\newcommand\{\\paperdoi\}\{([^}]+)\}', content)
        if doi_match:
            return doi_match.group(1)
        
        # Look for 10.5281/zenodo.xxx pattern
        doi_match = re.search(r'10\.5281/zenodo\.(\d+)', content)
        if doi_match:
            return f"10.5281/zenodo.{doi_match.group(1)}"
        
        return None
    except Exception as e:
        print(f"    Error reading LaTeX file: {e}")
        return None

def get_deposit_from_doi(automation: ZenodoAutomation, doi: str) -> Optional[dict]:
    """Get deposit information from DOI."""
    try:
        # Extract record ID from DOI (10.5281/zenodo.1234567 -> 1234567)
        record_id = doi.split('.')[-1]
        
        # Try published record first
        url = f"{automation.base_url}/api/records/{record_id}"
        response = requests.get(url, headers=automation.headers)
        
        if response.status_code == 200:
            return response.json()
        
        # If not found, try draft deposit
        url = f"{automation.base_url}/api/deposit/depositions/{record_id}"
        response = requests.get(url, headers=automation.headers)
        
        if response.status_code == 200:
            deposit = response.json()
            # Convert deposit format to record-like format
            return {
                'id': deposit.get('id'),
                'metadata': deposit.get('metadata', {})
            }
        
        return None
    except Exception as e:
        print(f"    Error fetching deposit: {e}")
        return None

def create_config_from_zenodo(zenodo_record: dict, tex_file: Path, base_dir: Path) -> bool:
    """Create config file from Zenodo record."""
    try:
        metadata = zenodo_record.get('metadata', {})
        
        # Extract deposit ID (for drafts) or record ID (for published)
        record_id = zenodo_record.get('id', '')
        deposit_id = zenodo_record.get('id', '')  # Same for published records
        
        # Get DOI
        doi = metadata.get('doi', '')
        if not doi:
            prereserve = metadata.get('prereserve_doi', {})
            doi = prereserve.get('doi', '') if prereserve else ''
        
        # Create config data
        config_data = {
            "title": metadata.get('title', 'Untitled'),
            "creators": metadata.get('creators', []),
            "description": metadata.get('description', ''),
            "keywords": metadata.get('keywords', []),
            "publication_date": metadata.get('publication_date', ''),
            "doi": doi,
            "tex_file": str(tex_file.relative_to(base_dir)),
            "upload_type": metadata.get('upload_type', 'publication'),
            "publication_type": metadata.get('publication_type', 'preprint'),
            "access_right": metadata.get('access_right', 'open'),
            "license": metadata.get('license', 'cc-by-4.0'),
            "deposit_id": str(deposit_id)
        }
        
        # Add language if present
        if metadata.get('language'):
            config_data['language'] = metadata['language']
        else:
            config_data['language'] = 'eng'
        
        # Add communities if present
        if metadata.get('communities'):
            config_data['communities'] = metadata['communities']
        
        # Write config file
        config_file = tex_file.with_suffix('.zenodo.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"    Error creating config: {e}")
        return False

def extract_metadata_from_latex(tex_file: Path) -> dict:
    """Extract metadata from LaTeX file for creating new config."""
    metadata = {
        'title': '',
        'creators': [{'name': 'Omar Iskandarani', 'affiliation': 'Independent Researcher, Groningen, The Netherlands', 'orcid': '0009-0006-1686-3961'}],
        'description': '',
        'keywords': [],
        'publication_date': ''
    }
    
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract title - try multiple formats
        # First, try to find \papertitle definition
        # Need to handle nested braces properly - find the command and extract balanced braces
        papertitle_start = content.find('\\newcommand{\\papertitle}{')
        if papertitle_start != -1:
            # Find the opening brace after the command
            brace_start = content.find('{', papertitle_start + len('\\newcommand{\\papertitle}'))
            if brace_start != -1:
                # Count braces to find the matching closing brace
                brace_count = 0
                i = brace_start
                while i < len(content):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found the matching closing brace
                            title_text = content[brace_start + 1:i].strip()
                            # Handle line breaks (\\)
                            title_text = re.sub(r'\\\\', ' ', title_text)
                            # Remove LaTeX commands but preserve their content - handle nested braces
                            # First pass: remove formatting commands like \textbf{}, \textit{}, etc.
                            while True:
                                new_text = re.sub(r'\\(?:textbf|textit|emph|textsc|textmd|textup)\{([^{}]+)\}', r'\1', title_text)
                                if new_text == title_text:
                                    break
                                title_text = new_text
                            # Handle \A command (which might be a special character) - replace with " A "
                            title_text = re.sub(r'\\A\b', ' A ', title_text)
                            # Remove other LaTeX commands (but be careful with nested braces)
                            title_text = re.sub(r'\\[a-zA-Z]+\{?[^{}]*\}?', '', title_text)
                            # Remove extra whitespace and newlines
                            title_text = ' '.join(title_text.split())
                            metadata['title'] = title_text
                            break
                    i += 1
        
        # If not found, try \title directly
        if not metadata.get('title'):
            title_match = re.search(r'\\title\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
            if title_match:
                title_text = title_match.group(1).strip()
                # Handle line breaks (\\)
                title_text = re.sub(r'\\\\', ' ', title_text)
                # Remove LaTeX commands but preserve their content
                title_text = re.sub(r'\\(?:textbf|textit|emph|textsc|textmd|textup|A)\{([^}]+)\}', r'\1', title_text)
                # Remove other LaTeX commands
                title_text = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title_text)
                # Remove extra whitespace and newlines
                title_text = ' '.join(title_text.split())
                metadata['title'] = title_text
        
        # If still not found, try \section*{title} at the beginning of document
        if not metadata.get('title'):
            doc_start = content.find('\\begin{document}')
            if doc_start != -1:
                body = content[doc_start:]
                section_match = re.search(r'\\section\*\{([^}]+)\}', body)
                if section_match:
                    title_text = section_match.group(1).strip()
                    # Clean LaTeX commands
                    title_text = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title_text)
                    title_text = ' '.join(title_text.split())
                    metadata['title'] = title_text
        
        if title_match:
            title_text = title_match.group(1).strip()
            # Handle line breaks (\\)
            title_text = re.sub(r'\\\\', ' ', title_text)
            # Remove LaTeX commands but preserve their content
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
            # Convert math delimiters
            abstract = convert_math_delimiters(abstract)
            # Clean LaTeX commands (basic) - but preserve \( and \)
            abstract = re.sub(r'\\(?!\(|\)|\[|\])([a-zA-Z]+)\{?[^}]*\}?', '', abstract)
            metadata['description'] = abstract[:2000]  # Limit description
        else:
            # Try first section if no abstract
            first_section = extract_first_section_from_latex(tex_file)
            if first_section:
                metadata['description'] = convert_math_delimiters(first_section[:2000])
        
        # Extract keywords
        keywords = extract_keywords_from_latex(tex_file)
        if not keywords:
            # Generate from abstract or first section
            if metadata.get('description'):
                keywords = generate_keywords_from_text(metadata['description'])
        metadata['keywords'] = keywords
        
        # Extract date
        date_match = re.search(r'\\date\{([^}]+)\}', content)
        if date_match:
            date_str = date_match.group(1).strip()
            # Skip if it's \today or similar
            if date_str not in ['\\today', '']:
                metadata['publication_date'] = date_str
    
    except Exception as e:
        print(f"  Warning: Could not extract metadata: {e}")
    
    return metadata

def create_config_from_latex(tex_file: Path, base_dir: Path) -> bool:
    """Create config file from LaTeX metadata."""
    try:
        metadata = extract_metadata_from_latex(tex_file)
        
        if not metadata.get('title'):
            print(f"    Warning: No title found in LaTeX file")
            return False
        
        # Extract DOI if present
        doi = extract_doi_from_latex(tex_file)
        
        # Create config data
        config_data = {
            "title": metadata['title'],
            "creators": metadata.get('creators', []),
            "description": metadata.get('description', ''),
            "keywords": metadata.get('keywords', []),
            "publication_date": metadata.get('publication_date', ''),
            "doi": doi or '',
            "tex_file": str(tex_file.relative_to(base_dir)),
            "upload_type": "publication",
            "publication_type": "preprint",
            "access_right": "open",
            "license": "cc-by-4.0",
            "language": "eng"
        }
        
        if doi:
            # Extract deposit ID from DOI
            record_id = doi.split('.')[-1]
            config_data['deposit_id'] = record_id
        
        # Write config file
        config_file = tex_file.with_suffix('.zenodo.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"    Error creating config from LaTeX: {e}")
        return False

def check_missing_configs(base_dir: Path) -> Tuple[List[Tuple[Path, Path]], List[Tuple[Path, Path]]]:
    """Check which .tex files have corresponding .zenodo.json files."""
    sst_folders = find_all_sst_folders(base_dir)
    
    missing = []
    found = []
    
    for folder in sst_folders:
        tex_files = find_tex_files_in_folder(folder)
        
        for tex_file in tex_files:
            # Expected config file name matches tex file name
            config_file = tex_file.with_suffix('.zenodo.json')
            
            if config_file.exists():
                found.append((tex_file, config_file))
            else:
                missing.append((tex_file, config_file))
    
    return found, missing

def validate_zenodo_config(config_file: Path, tex_file: Optional[Path] = None) -> Tuple[bool, Dict, List[str]]:
    """Validate a .zenodo.json file and return issues found."""
    issues = []
    needs_update = False
    updates = {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        return False, {}, [f"Error reading config file: {e}"]
    
    # Check required fields
    required_fields = ['title', 'creators', 'description', 'keywords', 'publication_date']
    
    for field in required_fields:
        if field not in config:
            issues.append(f"Missing field: {field}")
            needs_update = True
        elif field == 'creators':
            if not config[field] or (isinstance(config[field], list) and len(config[field]) == 0):
                issues.append(f"Empty {field}")
                needs_update = True
        elif field == 'keywords':
            if not config[field] or (isinstance(config[field], list) and len(config[field]) == 0):
                # Keywords can be empty, but we'll try to generate them
                if tex_file:
                    keywords = extract_keywords_from_latex(tex_file)
                    if not keywords:
                        # Try to generate from abstract or first section
                        abstract = extract_abstract_from_latex(tex_file)
                        if abstract:
                            keywords = generate_keywords_from_text(abstract)
                        else:
                            first_section = extract_first_section_from_latex(tex_file)
                            if first_section:
                                keywords = generate_keywords_from_text(first_section)
                    
                    if keywords:
                        updates['keywords'] = keywords
                        needs_update = True
        elif isinstance(config[field], str) and config[field].strip() == '':
            issues.append(f"Empty string for {field}")
            needs_update = True
            
            # Try to fill from LaTeX if description is empty
            if field == 'description' and tex_file:
                abstract = extract_abstract_from_latex(tex_file)
                if abstract:
                    updates['description'] = convert_math_delimiters(abstract)
                else:
                    first_section = extract_first_section_from_latex(tex_file)
                    if first_section:
                        updates['description'] = convert_math_delimiters(first_section)
    
    # Check for empty strings in nested structures
    if isinstance(config.get('creators'), list):
        for i, creator in enumerate(config['creators']):
            if isinstance(creator, dict):
                for key, value in creator.items():
                    if isinstance(value, str) and value.strip() == '':
                        issues.append(f"Empty string in creators[{i}].{key}")
    
    return needs_update, updates, issues

def update_zenodo_config(config_file: Path, updates: Dict) -> bool:
    """Update a .zenodo.json file with new values."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Apply updates
        for key, value in updates.items():
            # Convert math delimiters in description field
            if key == 'description' and isinstance(value, str):
                value = convert_math_delimiters(value)
            config[key] = value
        
        # Also fix existing description if present
        if 'description' in config and isinstance(config['description'], str):
            config['description'] = convert_math_delimiters(config['description'])
        
        # Write back
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"    Error updating config file: {e}")
        return False

def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Check and Validate Zenodo Config Files")
    print("=" * 80)
    print()
    
    # Step 1: Check for missing config files
    print("Step 1: Checking for missing .zenodo.json files...")
    print("-" * 80)
    
    found, missing = check_missing_configs(base_dir)
    
    print(f"Found {len(found)} .tex files with .zenodo.json files")
    print(f"Found {len(missing)} .tex files missing .zenodo.json files")
    print()
    
    if missing:
        print("Missing .zenodo.json files:")
        for tex_file, config_file in missing:
            print(f"  - {tex_file.relative_to(base_dir)}")
        print()
        
        # Step 1b: Try to fetch missing configs from Zenodo or create from LaTeX
        print("Step 1b: Attempting to create missing .zenodo.json files...")
        print("-" * 80)
        
        # Get Zenodo token for fetching
        token = read_token_from_zenodo_py()
        automation = None
        if token:
            automation = ZenodoAutomation(token, sandbox=False)
        else:
            print("  Warning: No Zenodo token found. Will only create configs from LaTeX metadata.")
        
        created_from_zenodo = 0
        created_from_latex = 0
        failed = 0
        
        for tex_file, config_file in missing:
            print(f"Processing: {tex_file.relative_to(base_dir)}")
            created = False
            
            # Try to fetch from Zenodo first
            if automation:
                doi = extract_doi_from_latex(tex_file)
                if doi:
                    print(f"  Found DOI: {doi}")
                    print(f"  Fetching from Zenodo...")
                    record = get_deposit_from_doi(automation, doi)
                    if record:
                        if create_config_from_zenodo(record, tex_file, base_dir):
                            print(f"  [OK] Created config from Zenodo")
                            created_from_zenodo += 1
                            created = True
                        else:
                            print(f"  [ERROR] Failed to create config from Zenodo record")
                    else:
                        print(f"  [WARNING] Record not found on Zenodo")
            
            # Fall back to creating from LaTeX metadata
            if not created:
                print(f"  Creating config from LaTeX metadata...")
                if create_config_from_latex(tex_file, base_dir):
                    print(f"  [OK] Created config from LaTeX")
                    created_from_latex += 1
                else:
                    print(f"  [ERROR] Failed to create config from LaTeX")
                    failed += 1
            print()
        
        print(f"Created from Zenodo: {created_from_zenodo}")
        print(f"Created from LaTeX: {created_from_latex}")
        print(f"Failed: {failed}")
        print()
        
        # Re-check after creation
        found, missing = check_missing_configs(base_dir)
        print(f"After creation: {len(found)} with configs, {len(missing)} still missing")
        print()
    
    # Step 2: Convert math delimiters in all descriptions
    print("Step 2: Converting math delimiters in all descriptions...")
    print("-" * 80)
    
    math_fixed_count = 0
    for tex_file, config_file in found:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'description' in config and isinstance(config['description'], str):
                original = config['description']
                converted = convert_math_delimiters(original)
                if original != converted:
                    config['description'] = converted
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    math_fixed_count += 1
        except Exception as e:
            print(f"  Warning: Could not process {config_file.name}: {e}")
    
    print(f"Fixed math delimiters in {math_fixed_count} files")
    print()
    
    # Step 3: Validate existing config files
    print("Step 3: Validating existing .zenodo.json files...")
    print("-" * 80)
    
    files_needing_update = []
    files_valid = []
    
    for tex_file, config_file in found:
        print(f"Checking: {config_file.relative_to(base_dir)}")
        needs_update, updates, issues = validate_zenodo_config(config_file, tex_file)
        
        if issues:
            print(f"  Issues found:")
            for issue in issues:
                print(f"    - {issue}")
        
        if needs_update:
            if updates:
                print(f"  Will update: {', '.join(updates.keys())}")
            files_needing_update.append((config_file, tex_file, updates, issues))
        else:
            files_valid.append(config_file)
            print(f"  [OK] Valid")
        print()
    
    # Step 4: Update files that need updates
    if files_needing_update:
        print("Step 4: Updating .zenodo.json files...")
        print("-" * 80)
        
        updated_count = 0
        for config_file, tex_file, updates, issues in files_needing_update:
            print(f"Updating: {config_file.relative_to(base_dir)}")
            if update_zenodo_config(config_file, updates):
                print(f"  [OK] Updated successfully")
                updated_count += 1
            else:
                print(f"  [ERROR] Failed to update")
            print()
        
        print(f"Updated {updated_count} out of {len(files_needing_update)} files")
    else:
        print("Step 3: No files need updating.")
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total .tex files found: {len(found) + len(missing)}")
    print(f"  - With .zenodo.json: {len(found)}")
    print(f"  - Missing .zenodo.json: {len(missing)}")
    print(f"Valid config files: {len(files_valid)}")
    print(f"Config files needing update: {len(files_needing_update)}")
    if files_needing_update:
        # Count how many were actually updated (already done in Step 3)
        updated_count = sum(1 for _, _, updates, _ in files_needing_update if updates)
        print(f"Config files with updates applied: {updated_count}")

if __name__ == '__main__':
    main()
