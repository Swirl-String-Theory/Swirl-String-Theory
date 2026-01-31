#!/usr/bin/env python3
"""Quick verification of which SST-xx.tex files have configs."""

import re
from pathlib import Path

base_dir = Path(__file__).parent.parent

folders = [f for f in base_dir.iterdir() if f.is_dir() and re.match(r'^SST-\d+', f.name)]
folders.sort()

missing = []
has_config = []

for folder in folders:
    folder_name = folder.name
    tex = folder / f"{folder_name}.tex"
    cfg = folder / f"{folder_name}.zenodo.json"
    
    if tex.exists():
        if cfg.exists():
            has_config.append(folder_name)
        else:
            missing.append(folder_name)

print(f"Total SST-xx folders with .tex files: {len(has_config) + len(missing)}")
print(f"Has config: {len(has_config)}")
print(f"Missing config: {len(missing)}")
print()
if missing:
    print("Missing configs:")
    for m in missing:
        print(f"  - {m}")
