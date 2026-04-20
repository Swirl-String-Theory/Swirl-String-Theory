#!/usr/bin/env python3
"""
Generate a markdown overview of all SST and VAM papers with titles and abstracts.
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Tuple

def extract_title_from_latex(tex_file: Path) -> Optional[str]:
    """Extract title from LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try \title{...}
        title_match = re.search(r'\\title\{([^}]+)\}', content, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Clean LaTeX commands
            title = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title)
            title = ' '.join(title.split())
            return title
        
        # Try \papertitle{...}
        title_match = re.search(r'\\papertitle\{([^}]+)\}', content, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            title = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title)
            title = ' '.join(title.split())
            return title
        
        # Try \section*{...} as title
        title_match = re.search(r'\\section\*\{([^}]+)\}', content)
        if title_match:
            title = title_match.group(1).strip()
            title = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title)
            title = ' '.join(title.split())
            return title
        
        return None
    except Exception as e:
        print(f"    Error reading LaTeX file {tex_file}: {e}")
        return None

def extract_abstract_from_latex(tex_file: Path) -> Optional[str]:
    """Extract abstract from LaTeX file."""
    try:
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to find abstract
        abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Clean LaTeX commands but preserve math delimiters
            abstract = re.sub(r'\\(?!\(|\)|\[|\])([a-zA-Z]+)\{?[^}]*\}?', '', abstract)
            # Remove extra whitespace
            abstract = ' '.join(abstract.split())
            return abstract[:2000]  # Limit length
        
        # Try to find first section as fallback
        doc_start = content.find('\\begin{document}')
        if doc_start != -1:
            body = content[doc_start:]
            section_match = re.search(r'\\section\*?\{([^}]+)\}(.*?)(?=\\section|\\subsection|\\end\{document\}|$)', body, re.DOTALL)
            if section_match:
                section_content = section_match.group(2).strip()
                # Remove LaTeX environments
                section_content = re.sub(r'\\begin\{[^}]+\}(.*?)\\end\{[^}]+\}', r'\1', section_content, flags=re.DOTALL)
                section_content = re.sub(r'\\[a-zA-Z]+\{?[^{}]*\}?', '', section_content)
                section_content = ' '.join(section_content.split())
                # Get first few sentences
                sentences = re.split(r'[.!?]\s+', section_content)
                if sentences:
                    result = '. '.join(sentences[:3]) + '.'
                    if len(result) > 500:
                        result = result[:500] + '...'
                    return result
        
        return None
    except Exception as e:
        print(f"    Error reading LaTeX file {tex_file}: {e}")
        return None

def find_main_tex_file(folder: Path) -> Optional[Path]:
    """Find the main .tex file in a folder."""
    # Look for files matching folder name pattern
    folder_name = folder.name
    
    # Try SST-xx.tex or VAM-xx.tex pattern
    patterns = [
        folder / f"{folder_name}.tex",
        folder / f"{folder_name.replace('_', '-')}.tex",
    ]
    
    # Also try common variations
    if folder_name.startswith('SST-'):
        base = folder_name.replace('_', '-')
        patterns.extend([
            folder / f"{base}.tex",
            folder / f"SST-{folder_name.split('_', 1)[1] if '_' in folder_name else folder_name[4:]}.tex",
        ])
    elif folder_name.startswith('VAM_'):
        base = folder_name.replace('_', '-')
        patterns.extend([
            folder / f"{base}.tex",
            folder / f"VAM-{folder_name.split('_', 1)[1] if '_' in folder_name else folder_name[4:]}.tex",
        ])
    
    # Find all .tex files and pick the main one
    tex_files = list(folder.glob("*.tex"))
    
    # Exclude cover letters and drafts
    exclude_patterns = ['coverletter', 'Coverletter', 'Cover_Letter', 'EditorialResponse', 'Old version', 'DIFFERNCE']
    tex_files = [f for f in tex_files if not any(pat in f.name for pat in exclude_patterns)]
    
    if not tex_files:
        return None
    
    # Prefer files matching folder name
    for pattern in patterns:
        if pattern.exists():
            return pattern
    
    # If no exact match, prefer the largest .tex file (likely the main one)
    if tex_files:
        return max(tex_files, key=lambda f: f.stat().st_size)
    
    return None

def find_sst_papers(base_dir: Path) -> List[Tuple[str, Path, Optional[str], Optional[str]]]:
    """Find all SST papers."""
    papers = []
    sst_folders = sorted([d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith('SST-')])
    
    for folder in sst_folders:
        tex_file = find_main_tex_file(folder)
        if not tex_file:
            print(f"  Warning: No main .tex file found in {folder.name}")
            continue
        
        title = extract_title_from_latex(tex_file)
        abstract = extract_abstract_from_latex(tex_file)
        
        papers.append((folder.name, tex_file, title, abstract))
        print(f"  Found: {folder.name}")
    
    return papers

def find_vam_papers(base_dir: Path) -> List[Tuple[str, Path, Optional[str], Optional[str]]]:
    """Find all VAM papers."""
    papers = []
    
    # VAM folders
    vam_folders = sorted([d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith('VAM_')])
    
    for folder in vam_folders:
        tex_file = find_main_tex_file(folder)
        if not tex_file:
            # Some VAM folders might have different structure
            tex_files = list(folder.glob("*.tex"))
            exclude_patterns = ['coverletter', 'Coverletter', 'Cover_Letter']
            tex_files = [f for f in tex_files if not any(pat in f.name for pat in exclude_patterns)]
            if tex_files:
                tex_file = max(tex_files, key=lambda f: f.stat().st_size)
            else:
                print(f"  Warning: No main .tex file found in {folder.name}")
                continue
        
        title = extract_title_from_latex(tex_file)
        abstract = extract_abstract_from_latex(tex_file)
        
        papers.append((folder.name, tex_file, title, abstract))
        print(f"  Found: {folder.name}")
    
    # Also check VAM - Appendix All for specific papers mentioned
    appendix_dir = base_dir / "VAM - Appendix All"
    if appendix_dir.exists():
        specific_files = [
            "Appendix_X-filesExplanationsFoundationalPhysicsAnomalies.tex",
            "Appendix_VAM_Pressure_Shells_Snapshot.tex",
            "Appendix_2FluidÆther.tex",
        ]
        for filename in specific_files:
            tex_file = appendix_dir / filename
            if tex_file.exists():
                title = extract_title_from_latex(tex_file)
                abstract = extract_abstract_from_latex(tex_file)
                papers.append((f"Appendix: {filename.replace('.tex', '')}", tex_file, title, abstract))
                print(f"  Found: {filename}")
    
    return papers

def generate_markdown(sst_papers: List[Tuple], vam_papers: List[Tuple], output_file: Path):
    """Generate markdown overview file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Papers Overview\n\n")
        f.write("This document provides an overview of all SST (Swirl String Theory) and VAM (Vortex Æther Model) papers.\n\n")
        
        # SST Papers
        f.write("## SST Papers\n\n")
        for folder_name, tex_file, title, abstract in sst_papers:
            f.write(f"### {folder_name}\n\n")
            if title:
                f.write(f"**Title:** {title}\n\n")
            else:
                f.write(f"**Title:** (Not found)\n\n")
            
            if abstract:
                f.write(f"**Abstract:**\n\n{abstract}\n\n")
            else:
                f.write(f"**Abstract:** (Not found)\n\n")
            
            f.write(f"**File:** `{tex_file.relative_to(tex_file.parent.parent)}`\n\n")
            f.write("---\n\n")
        
        # VAM Papers
        f.write("## VAM Papers\n\n")
        for folder_name, tex_file, title, abstract in vam_papers:
            f.write(f"### {folder_name}\n\n")
            if title:
                f.write(f"**Title:** {title}\n\n")
            else:
                f.write(f"**Title:** (Not found)\n\n")
            
            if abstract:
                f.write(f"**Abstract:**\n\n{abstract}\n\n")
            else:
                f.write(f"**Abstract:** (Not found)\n\n")
            
            f.write(f"**File:** `{tex_file.relative_to(tex_file.parent.parent)}`\n\n")
            f.write("---\n\n")

def main():
    """Main function."""
    # Base directories
    sst_base = Path(__file__).parent
    vam_base = sst_base.parent / "VAM"
    
    print("Finding SST papers...")
    sst_papers = find_sst_papers(sst_base)
    print(f"Found {len(sst_papers)} SST papers\n")
    
    print("Finding VAM papers...")
    vam_papers = find_vam_papers(vam_base)
    print(f"Found {len(vam_papers)} VAM papers\n")
    
    # Generate markdown
    output_file = sst_base / "PAPERS_OVERVIEW.md"
    print(f"Generating markdown file: {output_file}")
    generate_markdown(sst_papers, vam_papers, output_file)
    print(f"Done! Overview saved to {output_file}")

if __name__ == '__main__':
    main()
