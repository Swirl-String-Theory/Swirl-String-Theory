#!/usr/bin/env python3
"""Compile SST satellite papers: PDF -> out/, aux/log -> aux/."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
AUX = ROOT / "aux"

PAPERS: list[tuple[Path, str, bool]] = [
    (
        ROOT
        / "papers"
        / "SST-73_A_Poisson-Type_Gravity_Program_from_Organized_Swirl_Transport",
        "SST-73_A_Poisson-Type_Gravity_Program_from_Organized_Swirl_Transport.tex",
        False,
    ),
    (
        ROOT / "papers" / "SST-23-56-63_Vacuum_Dual_Medium" / "SST-63_Holograpic",
        "SST-63_Holograpic.tex",
        False,
    ),
    (
        ROOT / "papers" / "SST-64_Covariant",
        "SST-64_v2.tex",
        False,
    ),
    (
        ROOT / "papers" / "SST-34_Hydrogen-Gravity",
        "SST-34_Hydrogen-Gravity.tex",
        True,
    ),
]


def run(cmd: list[str], *, cwd: Path, env: dict | None = None) -> int:
    print(">", " ".join(cmd), f"(cwd={cwd.name})")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    return result.returncode


def compile_paper(workdir: Path, tex_name: str, *, use_bibtex: bool) -> bool:
    stem = Path(tex_name).stem
    aux_dir = AUX.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    AUX.mkdir(parents=True, exist_ok=True)

    pdflatex = [
        "pdflatex",
        "-interaction=nonstopmode",
        f"-output-directory={aux_dir}",
        tex_name,
    ]
    env = None
    if use_bibtex:
        env = dict(**{k: v for k, v in __import__("os").environ.items()})
        env["BIBINPUTS"] = str(workdir.resolve()) + ";;"

    rc = run(pdflatex, cwd=workdir, env=env)
    if use_bibtex:
        rc = max(rc, run(["bibtex", str(aux_dir / stem)], cwd=workdir, env=env))
        rc = max(rc, run(pdflatex, cwd=workdir, env=env))
    rc = max(rc, run(pdflatex, cwd=workdir, env=env))

    pdf_src = aux_dir / f"{stem}.pdf"
    pdf_dst = OUT / f"{stem}.pdf"
    if not pdf_src.is_file():
        print(f"FAIL: no PDF produced for {stem}")
        return False
    shutil.copy2(pdf_src, pdf_dst)
    pdf_src.unlink(missing_ok=True)
    print(f"OK: {pdf_dst.relative_to(ROOT)}")
    return True


def main() -> int:
    ok = True
    for workdir, tex_name, use_bibtex in PAPERS:
        print(f"\n=== {tex_name} ===")
        if not (workdir / tex_name).is_file():
            print(f"FAIL: missing {workdir / tex_name}")
            ok = False
            continue
        if not compile_paper(workdir, tex_name, use_bibtex=use_bibtex):
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
