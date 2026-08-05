#!/usr/bin/env python3
"""Verify the patched Paper 1 v0.2.1 source package."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

TEX_NAME = "Angular_Projector_Normalization_and_Finite_Core_Energetics_v0.2.1.tex"
XML_NAME = "Supplementary_Data_S1_Gilbert_trefoil_record.xml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def check_manifest(root: Path) -> None:
    manifest = root / "SHA256SUMS.txt"
    if not manifest.exists():
        return
    for lineno, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, rel = line.split(" *", 1)
        except ValueError as exc:
            raise RuntimeError(f"Malformed manifest line {lineno}: {line}") from exc
        path = root / rel
        require(path.is_file(), f"Manifest file missing: {rel}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == expected, f"Checksum mismatch: {rel}")


def compile_tex(root: Path, tex: Path) -> None:
    engine = shutil.which("pdflatex")
    if not engine:
        raise RuntimeError("--compile requested but pdflatex is not installed")
    for _ in range(2):
        subprocess.run(
            [engine, "-interaction=nonstopmode", "-halt-on-error", tex.name],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    log = tex.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    require("undefined references" not in log.lower(), "LaTeX has undefined references")
    require("overfull \\hbox" not in log.lower(), "LaTeX has an overfull hbox")
    require("overfull \\vbox" not in log.lower(), "LaTeX has an overfull vbox")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--compile", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    tex = root / TEX_NAME
    xml = root / XML_NAME
    readme = root / "README.md"

    require(tex.is_file(), f"Missing {TEX_NAME}")
    require(not (root / TEX_NAME.replace("0.2.1", "0.2.0")).exists(),
            "Old v0.2.0 LaTeX source still exists")
    tex_text = tex.read_text(encoding="utf-8")
    require("manuscript version 0.2.1" in tex_text,
            "Internal manuscript version is not 0.2.1")
    require("manuscript version 0.2.0" not in tex_text,
            "Old internal manuscript version remains")
    require(r"\calL_D^{\rm rec}=16.3724604307" in tex_text,
            "Fourier reconstruction branch is missing")
    require("optimistic lower estimate" in tex_text,
            "Curvature epistemic correction is missing")
    require("$+3$ & 99.34" in tex_text,
            "Mirror framing row SL=+3 is missing")
    require("roughly $235$" in tex_text,
            "Framing-spread correction is missing")

    require(xml.is_file(), f"Missing {XML_NAME}")
    xml_text = xml.read_text(encoding="utf-8")
    require("[FILL IN" not in xml_text, "Unresolved [FILL IN] remains in XML")
    require("Redistributed verbatim" not in xml_text,
            "Incorrect 'Redistributed verbatim' wording remains")
    require("payload below is preserved verbatim" in xml_text,
            "Payload/header distinction is missing")
    # Phrase may be line-wrapped in the XML comment header (see 0004 patch).
    require(
        "redistribution status is therefore unresolved" in xml_text
        and "public" in xml_text,
        "Licence/redistribution guard is missing",
    )
    ET.parse(xml)

    require(readme.is_file(), "Missing README.md")
    readme_text = readme.read_text(encoding="utf-8")
    require("[FILL IN" not in readme_text, "Unresolved [FILL IN] remains in README")
    require("PAPER1_RELEASE_NOTE_v0.2.1" in readme_text,
            "Release-version note is missing")

    check_manifest(root)

    if args.compile:
        compile_tex(root, tex)

    print("[OK] Paper 1 v0.2.1 release checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
