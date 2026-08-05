#!/usr/bin/env python3
"""Finalize Paper 1 after applying patches 0001--0004.

Actions:
- updates the manuscript's internal version to 0.2.1;
- renames the LaTeX source from v0.2.0 to v0.2.1;
- appends an idempotent README release note;
- intentionally leaves frozen v0.2.0 numerical-artifact filenames unchanged.

Run from the source-package directory:
    python 0005-release-hygiene.py --root .
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

OLD_NAME = "Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.0.tex"
NEW_NAME = "Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.1.tex"
MARKER = "<!-- PAPER1_RELEASE_NOTE_v0.2.1 -->"


def update_version(text: str) -> str:
    if "manuscript version 0.2.1" in text:
        return text

    count = text.count("manuscript version 0.2.0")
    if count == 1:
        return text.replace(
            "manuscript version 0.2.0",
            "manuscript version 0.2.1",
            1,
        )
    if count > 1:
        raise RuntimeError(
            "Found multiple 'manuscript version 0.2.0' strings; "
            "refusing an ambiguous replacement."
        )

    # Conservative fallback for a simple one-line \date{...}.
    date_re = re.compile(r"\\date\{([^{}\n]*)\}")
    match = date_re.search(text)
    if not match:
        raise RuntimeError(
            "Could not find an internal version string or a simple one-line "
            "\\date{...} declaration."
        )
    current = match.group(1).strip()
    replacement = rf"\date{{{current}; manuscript version 0.2.1}}"
    return text[:match.start()] + replacement + text[match.end():]


def append_release_note(readme: Path) -> None:
    note = f"""
{MARKER}
## Release version note

The manuscript source is release **v0.2.1**. Files whose names still contain
`v0.2.0`, including numerical JSON/validation artifacts, are frozen outputs of
the v0.2.0 computational run and intentionally retain their original names.
They must not be silently relabelled as regenerated v0.2.1 results.
"""
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if MARKER not in text:
            readme.write_text(text.rstrip() + "\n\n" + note.lstrip(), encoding="utf-8")
    else:
        readme.write_text("# Supplementary material\n\n" + note.lstrip(), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    old_path = root / OLD_NAME
    new_path = root / NEW_NAME

    if new_path.exists() and old_path.exists():
        raise RuntimeError(f"Both {OLD_NAME} and {NEW_NAME} exist.")

    source = new_path if new_path.exists() else old_path
    if not source.exists():
        raise FileNotFoundError(
            f"Neither {OLD_NAME} nor {NEW_NAME} exists in {root}."
        )

    updated = update_version(source.read_text(encoding="utf-8"))
    target = new_path
    target.write_text(updated, encoding="utf-8")

    if source != target and source.exists():
        source.unlink()

    append_release_note(root / "README.md")

    print(f"[OK] manuscript source: {target.name}")
    print("[OK] internal manuscript version: 0.2.1")
    print("[OK] frozen v0.2.0 computational artifact names retained")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
