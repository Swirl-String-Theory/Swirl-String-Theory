from pathlib import Path
import csv, json, re

FILES = [
    Path('SST_CANON-v0.8.31.tex'),
    Path('SST_CANON-v0.8.31-research-track.tex'),
]

records = []
for path in FILES:
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    section = subsection = paragraph = ''
    for lineno, line in enumerate(lines, 1):
        match = re.search(r'\\section\*?\{([^}]*)\}', line)
        if match:
            section, subsection, paragraph = match.group(1), '', ''
        match = re.search(r'\\subsection\*?\{([^}]*)\}', line)
        if match:
            subsection, paragraph = match.group(1), ''
        match = re.search(r'\\paragraph\*?\{([^}]*)\}', line)
        if match:
            paragraph = match.group(1)
        if '\\rhoF' in line or 'rho_{\\!f}' in line or '\\rho_{\\!f}' in line:
            records.append({
                'file': path.name,
                'line': lineno,
                'section': section,
                'subsection': subsection,
                'paragraph': paragraph,
                'text': line.strip(),
            })

Path('rho_occurrences.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
with Path('rho_occurrences.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

print(f'Wrote {len(records)} occurrences.')
