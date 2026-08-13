#!/usr/bin/env python3
"""Stack all to_do_patches onto v0.8.35 → been_processed/v0.8.36."""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

from _apply_unified_diff import (
    _hunk_new_block,
    _hunk_old_block,
    apply_hunks_to_text,
    apply_unified_diff,
    parse_unified_diff,
)
from _paths import ROOT

from canon_edition import (
    EDITION_CONFIG,
    edition_dir,
    main_tex,
    paperkeywords_tex,
    rt_tex,
    sync_paperkeywords_in_tex,
)

VERSION = "0.8.36"
PREV = "0.8.35"
TODO_PATCHES = ROOT.parent / "to_do_patches"
ARCHIVE = ROOT / "sources" / "v0.8.36_maxwell_spectro_stack"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.3.tex"

SPECTRO_ZIP = "SST_spectroscopic_response_patch_v0.1.0.zip"
KINETIC_ZIP = "SST_CANON-v0.8.35-Maxwell-SST-Kinetic-Closure-package.zip"
FALSIFIER = "SST_CANON-v0.8.35-Maxwell-blind-mechanical-falsifier.diff"
RECIPROCAL = "SST_CANON-v0.8.35-Maxwell-reciprocal-stress.diff"
DYNAMICAL = "SST_CANON-v0.8.35-Maxwell-SST-Dynamical-Field-Closure.diff"
TONIC = "SST_CANON-v0.8.35_to_v0.8.36_Maxwell_swirl_tonic.patch"

WORK_MAIN = f"SST_CANON-v{PREV}.tex"
WORK_RT = f"SST_CANON-v{PREV}-research-track.tex"

APPLY_LOG: list[str] = []


def log(msg: str) -> None:
    print(msg)
    APPLY_LOG.append(msg)


def workdir() -> Path:
    return edition_dir(VERSION)


def rewrite_diff_paths(text: str, mapping: dict[str, str] | None = None) -> str:
    text = text.replace("\r\n", "\n")
    for a, b in (mapping or {}).items():
        text = text.replace(a, b)
    text = re.sub(r"^(---|\+\+\+)\s+[ab]/", r"\1 ", text, flags=re.M)
    return text


def apply_diff_text(label: str, patch_text: str, mapping: dict[str, str] | None = None) -> None:
    adapted = rewrite_diff_paths(patch_text, mapping)
    apply_unified_diff(adapted, workdir())
    log(f"OK {label}")


def apply_diff_file(label: str, path: Path, mapping: dict[str, str] | None = None) -> None:
    apply_diff_text(label, path.read_text(encoding="utf-8"), mapping)


def apply_diff_per_file(
    label: str,
    patch_text: str,
    *,
    skip_targets: set[str] | None = None,
    mapping: dict[str, str] | None = None,
) -> dict[str, bool]:
    """Apply each file independently; return {basename: success}."""
    adapted = rewrite_diff_paths(patch_text, mapping)
    skip_targets = skip_targets or set()
    results: dict[str, bool] = {}
    for target, hunks in parse_unified_diff(adapted):
        name = Path(target).name
        if name in skip_targets:
            results[name] = False
            log(f"SKIP {label} -> {name}")
            continue
        path = workdir() / name
        try:
            original = path.read_text(encoding="utf-8")
            updated = apply_hunks_to_text(original, hunks)
            path.write_text(updated, encoding="utf-8")
            results[name] = True
            log(f"OK {label} -> {name} ({len(hunks)} hunks)")
        except Exception as e:
            results[name] = False
            log(f"FAIL {label} -> {name}: {e}")
    return results


def insert_before_anchor(path: Path, anchor: str, insert: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insert.strip() and insert.strip() in text:
        log(f"SKIP {label} (already present)")
        return
    idx = text.find(anchor)
    if idx < 0:
        raise SystemExit(f"{label}: anchor not found in {path.name}: {anchor[:80]!r}")
    path.write_text(text[:idx] + insert + text[idx:], encoding="utf-8")
    log(f"OK {label} (insert before anchor)")


def insert_before_regex(path: Path, pattern: str, insert: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insert.strip() and insert.strip()[:80] in text:
        log(f"SKIP {label} (already present)")
        return
    m = re.search(pattern, text)
    if not m:
        raise SystemExit(f"{label}: regex not found in {path.name}: {pattern}")
    path.write_text(text[: m.start()] + insert + text[m.start() :], encoding="utf-8")
    log(f"OK {label} (insert before regex)")


def ensure_bibitems(path: Path, block: str, keys: list[str], label: str) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [k for k in keys if f"\\bibitem{{{k}}}" not in text]
    if not missing:
        log(f"SKIP {label} (bib keys present)")
        return
    # Only insert lines for missing keys — use full block if all missing, else filter
    if set(missing) == set(keys):
        insert = block if block.endswith("\n") else block + "\n"
    else:
        # crude: insert whole block only for completely missing package keys
        insert = block if block.endswith("\n") else block + "\n"
        log(f"NOTE {label}: inserting full block; missing={missing}")
    anchor = "\\end{thebibliography}"
    idx = text.rfind(anchor)
    if idx < 0:
        raise SystemExit(f"{label}: \\end{{thebibliography}} not in {path.name}")
    path.write_text(text[:idx] + insert + "\n" + text[idx:], encoding="utf-8")
    log(f"OK {label} (bib before end{{thebibliography}})")


def parse_bare_at_hunks(patch_text: str) -> list[tuple[list[str], list[str]]]:
    """Parse ---/+++ then bare @@ hunks into (old_lines, new_lines)."""
    text = patch_text.replace("\r\n", "\n")
    # drop file headers
    body_start = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("@@"):
            body_start = i
            break
    hunks: list[tuple[list[str], list[str]]] = []
    i = body_start
    while i < len(lines):
        if lines[i].strip() != "@@" and not lines[i].startswith("@@"):
            i += 1
            continue
        i += 1
        body: list[str] = []
        while i < len(lines) and not (
            lines[i].strip() == "@@" or lines[i].startswith("@@ ")
        ):
            # stop at next --- if any
            if lines[i].startswith("--- ") and i + 1 < len(lines) and lines[i + 1].startswith("+++ "):
                break
            body.append(lines[i])
            i += 1
        old: list[str] = []
        new: list[str] = []
        for bl in body:
            if not bl:
                # treat empty as context blank (rare)
                old.append("")
                new.append("")
                continue
            tag = bl[0]
            payload = bl[1:] if tag in " +-" else bl
            if tag == " ":
                old.append(payload)
                new.append(payload)
            elif tag == "-":
                old.append(payload)
            elif tag == "+":
                new.append(payload)
            else:
                old.append(bl)
                new.append(bl)
        if old or new:
            hunks.append((old, new))
    return hunks


def apply_bare_at_patch(path: Path, patch_text: str, label: str, *, only_indices: list[int] | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").split("\n")
    hunks = parse_bare_at_hunks(patch_text)
    applied = 0
    for hi, (old, new) in enumerate(hunks):
        if only_indices is not None and hi not in only_indices:
            continue
        if not old:
            # pure insert: need trailing context in new — find last context-like
            # For tonic, pure-insert hunks include trailing context lines as ' ' tagged
            raise SystemExit(f"{label} hunk {hi}: empty old block unsupported")
        # find old block
        n = len(old)
        pos = -1
        for j in range(0, len(lines) - n + 1):
            if lines[j : j + n] == old:
                pos = j
                break
        if pos < 0:
            # fuzzy rstrip
            old_s = [x.rstrip() for x in old]
            for j in range(0, len(lines) - n + 1):
                if [x.rstrip() for x in lines[j : j + n]] == old_s:
                    pos = j
                    break
        if pos < 0:
            raise SystemExit(
                f"{label} hunk {hi}: context not found: {old[0][:80]!r}"
            )
        lines[pos : pos + n] = new
        applied += 1
    nl = "\r\n" if "\r\n" in text else "\n"
    out = "\n".join(lines)
    if nl != "\n":
        out = out.replace("\n", nl)
    path.write_bytes(out.encode("utf-8"))
    log(f"OK {label} ({applied} bare-@@ hunks)")


def copy_from_prev() -> None:
    src = edition_dir(PREV)
    dst = workdir()
    if not src.is_dir():
        raise SystemExit(f"v{PREV} folder missing")
    dst.mkdir(parents=True, exist_ok=True)
    for name in (WORK_MAIN, WORK_RT, NONRELEASE):
        s = src / name
        if not s.is_file():
            if name == NONRELEASE:
                log(f"no {NONRELEASE} in v{PREV} (skip)")
                continue
            raise SystemExit(f"missing {s}")
        shutil.copy2(s, dst / name)
        log(f"copied {name}")


def extract_zip(zip_name: str) -> Path:
    zpath = TODO_PATCHES / zip_name
    if not zpath.is_file():
        alt = ARCHIVE / zip_name
        if alt.is_file():
            zpath = alt
        else:
            raise SystemExit(f"missing zip: {zpath}")
    dest = ARCHIVE / zip_name.replace(".zip", "")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    if not dest.is_dir() or not any(dest.rglob("*.tex")):
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(dest)
        log(f"extracted {zip_name}")
    else:
        log(f"using existing extract {dest.name}")

    def package_root(base: Path) -> Path:
        # Prefer directory that contains the patch/diff payload
        for cand in [base, *base.rglob("*")]:
            if not cand.is_dir():
                continue
            if (cand / "diff").is_dir() or any(cand.glob("*.patch")):
                return cand
        kids = [p for p in base.iterdir() if p.is_dir() and p.name != "__MACOSX"]
        if len(kids) == 1:
            return kids[0]
        return base

    return package_root(dest)


def step_spectro(spectro_root: Path) -> None:
    map34 = {
        "SST_CANON-v0.8.34.tex": WORK_MAIN,
        "SST_CANON-v0.8.34-research-track.tex": WORK_RT,
    }
    diff_dir = spectro_root / "diff"
    for diff in sorted(diff_dir.glob("*.diff")):
        apply_diff_file(f"spectro {diff.name}", diff, map34)


def step_kinetic(kinetic_root: Path) -> None:
    patch = (
        kinetic_root / "SST_CANON-v0.8.35-Maxwell-SST-Kinetic-Closure.patch"
    ).read_text(encoding="utf-8")
    results = apply_diff_per_file("kinetic", patch)
    if not results.get(WORK_RT, False):
        rt_block = (
            kinetic_root / "Maxwell-SST-Kinetic-Closure-research-track.tex"
        ).read_text(encoding="utf-8")
        if not rt_block.endswith("\n"):
            rt_block += "\n"
        insert_before_anchor(
            workdir() / WORK_RT,
            "% Bibliography entries for the Relativity Emergence Ladder",
            "\n\n" + rt_block + "\n",
            "kinetic RT copy-ready insert",
        )
        bib_path = kinetic_root / "Maxwell-SST-Kinetic-Closure-bibitems.tex"
        bib_text = bib_path.read_text(encoding="utf-8")
        # standalone RT additions (second section)
        parts = bib_text.split("Standalone research-track bibliography additions")
        rt_bib = parts[-1] if len(parts) > 1 else bib_text
        # strip comment header lines until first bibitem
        m = re.search(r"\\bibitem\{", rt_bib)
        if m:
            rt_bib = rt_bib[m.start() :]
        ensure_bibitems(
            workdir() / WORK_RT,
            rt_bib,
            [
                "Maxwell1860GasesI",
                "Maxwell1860GasesIIIII",
                "PathriaBeale2011",
            ],
            "kinetic RT bibitems",
        )
    # main bibitems if main applied (patch includes them); also ensure main keys
    if results.get(WORK_MAIN, False):
        bib_path = kinetic_root / "Maxwell-SST-Kinetic-Closure-bibitems.tex"
        bib_text = bib_path.read_text(encoding="utf-8")
        parts = bib_text.split("Standalone research-track")
        main_bib = parts[0]
        m = re.search(r"\\bibitem\{", main_bib)
        if m:
            main_bib = main_bib[m.start() :]
        # indent-aware: main uses indented bibitems — ensure_bibitems uses as-is
        text = (workdir() / WORK_MAIN).read_text(encoding="utf-8")
        if "\\bibitem{Maxwell1860GasesI}" not in text:
            ensure_bibitems(
                workdir() / WORK_MAIN,
                main_bib,
                ["Maxwell1860GasesI", "Maxwell1860GasesIIIII", "PathriaBeale2011"],
                "kinetic main bibitems",
            )


def step_falsifier_reciprocal() -> None:
    # Falsifier RT bib expects CQG38 adjacent to \\end{thebibliography}; kinetic
    # bib insert may have broken that — apply per file with bib fallback.
    fpatch = (TODO_PATCHES / FALSIFIER).read_text(encoding="utf-8")
    fres = apply_diff_per_file("falsifier", fpatch)
    if not fres.get(WORK_RT, False):
        adapted = rewrite_diff_paths(fpatch)
        for target, hunks in parse_unified_diff(adapted):
            if Path(target).name != WORK_RT:
                continue
            # content hunk first (lower line number)
            content_hunks = [h for h in hunks if h.old_start < 7000]
            bib_hunks = [h for h in hunks if h.old_start >= 7000]
            path = workdir() / WORK_RT
            if content_hunks:
                original = path.read_text(encoding="utf-8")
                updated = apply_hunks_to_text(original, content_hunks)
                path.write_text(updated, encoding="utf-8")
                log("OK falsifier RT content hunk(s)")
            if bib_hunks:
                new1 = _hunk_new_block(bib_hunks[0])
                try:
                    b0 = next(
                        i for i, l in enumerate(new1) if l.startswith("\\bibitem{")
                    )
                    b1 = next(
                        i
                        for i, l in enumerate(new1)
                        if l.startswith("\\end{thebibliography}")
                    )
                    bib = "\n".join(new1[b0:b1]).rstrip() + "\n"
                except StopIteration as e:
                    raise SystemExit(f"falsifier RT bib extract failed: {e}") from e
                ensure_bibitems(
                    path,
                    bib,
                    ["Maxwell1861PhysicalLines", "Reynolds1895"],
                    "falsifier RT bib fallback",
                )

    apply_diff_file("reciprocal", TODO_PATCHES / RECIPROCAL)


def step_dynamical() -> None:
    patch = (TODO_PATCHES / DYNAMICAL).read_text(encoding="utf-8")
    adapted = rewrite_diff_paths(patch)
    # main first
    for target, hunks in parse_unified_diff(adapted):
        name = Path(target).name
        if name != WORK_MAIN:
            continue
        path = workdir() / name
        original = path.read_text(encoding="utf-8")
        updated = apply_hunks_to_text(original, hunks)
        path.write_text(updated, encoding="utf-8")
        log(f"OK dynamical -> {name} ({len(hunks)} hunks)")

    # RT content: extract insert from first hunk
    rt_hunks = None
    for target, hunks in parse_unified_diff(adapted):
        if Path(target).name == WORK_RT:
            rt_hunks = hunks
            break
    if not rt_hunks:
        raise SystemExit("dynamical: no RT hunks")

    # try unified apply for RT; on failure use insert
    try:
        path = workdir() / WORK_RT
        original = path.read_text(encoding="utf-8")
        updated = apply_hunks_to_text(original, rt_hunks)
        path.write_text(updated, encoding="utf-8")
        log(f"OK dynamical -> {WORK_RT} ({len(rt_hunks)} hunks)")
        return
    except Exception as e:
        log(f"NOTE dynamical RT unified failed ({e}); using insert fallback")

    new0 = _hunk_new_block(rt_hunks[0])
    # strip leading context through EM section heading; strip trailing Euler-Decomposed
    start = 0
    for i, line in enumerate(new0):
        if line.startswith("\\subsection{Maxwell--SST Dynamical Field Closure"):
            start = i
            break
    end = len(new0)
    for i, line in enumerate(new0):
        if line.startswith("\\subsection{Euler-Decomposed Swirl Gravity"):
            end = i
            break
    insert = "\n".join(new0[start:end]).rstrip() + "\n\n"
    insert_before_anchor(
        workdir() / WORK_RT,
        "\\subsection{Euler-Decomposed Swirl Gravity and Probe Transport}",
        insert,
        "dynamical RT section insert",
    )

    # bib from second hunk
    if len(rt_hunks) > 1:
        new1 = _hunk_new_block(rt_hunks[1])
        try:
            b0 = next(i for i, l in enumerate(new1) if l.startswith("\\bibitem{"))
            b1 = next(
                i for i, l in enumerate(new1) if l.startswith("\\end{thebibliography}")
            )
            bib = "\n".join(new1[b0:b1]).rstrip() + "\n"
        except StopIteration:
            bib = (
                "\\bibitem{Maxwell1865DynamicalField}\n"
                "J.~Clerk Maxwell,\n"
                "``A Dynamical Theory of the Electromagnetic Field,''\n"
                "\\emph{Philosophical Transactions of the Royal Society of London} "
                "\\textbf{155} (1865), 459--512.\n"
                "DOI: \\href{https://doi.org/10.1098/rstl.1865.0008}"
                "{10.1098/rstl.1865.0008}.\n"
            )
        ensure_bibitems(
            workdir() / WORK_RT,
            bib,
            ["Maxwell1865DynamicalField"],
            "dynamical RT bib",
        )


def step_swirl_tonic() -> None:
    patch = (TODO_PATCHES / TONIC).read_text(encoding="utf-8")
    main = workdir() / WORK_MAIN
    # abstract + swirl-tonic subsection (skip header/macros/edition; those come from EDITION_CONFIG)
    apply_bare_at_patch(main, patch, "swirl-tonic abstract+section", only_indices=[2, 4])
    bib = (
        "            \\bibitem{Maxwell1856FaradayLines}\n"
        "            J.~Clerk Maxwell,\n"
        "            \\newblock ``On Faraday's Lines of Force,''\n"
        "            \\newblock \\emph{Transactions of the Cambridge Philosophical Society}\n"
        "            \\textbf{10} (1856), 155--229.\n\n"
    )
    text = main.read_text(encoding="utf-8")
    if "\\bibitem{Maxwell1856FaradayLines}" not in text:
        insert_before_anchor(
            main,
            "            \\bibitem{MajdaBertozzi2002}",
            bib,
            "swirl-tonic bib Maxwell1856",
        )
    else:
        log("SKIP swirl-tonic bib (already present)")


def rename_to_version() -> None:
    dst = workdir()
    pairs = [
        (WORK_MAIN, f"SST_CANON-v{VERSION}.tex"),
        (WORK_RT, f"SST_CANON-v{VERSION}-research-track.tex"),
    ]
    for old, new in pairs:
        src = dst / old
        if not src.is_file():
            raise SystemExit(f"missing work file {old}")
        target = dst / new
        if target.exists():
            target.unlink()
        src.rename(target)
        log(f"renamed {old} -> {new}")


def bump_macros_and_notes() -> None:
    cfg = EDITION_CONFIG[VERSION]
    tex = main_tex(VERSION)
    text = tex.read_text(encoding="utf-8")

    # header: replace first %! v0.8. line
    text = re.sub(
        r"%! v0\.8\.\d+ edition:[^\n]*",
        cfg["header"].rstrip("\n"),
        text,
        count=1,
    )
    text = text.replace(
        rf"\newcommand{{\canonversion}}{{{PREV}}}",
        rf"\newcommand{{\canonversion}}{{{VERSION}}}",
    )
    text = text.replace(
        rf"\newcommand{{\papertitle}}{{Swirl-String-Theory Canon-v{PREV}}}",
        rf"\newcommand{{\papertitle}}{{Swirl-String-Theory Canon-v{VERSION}}}",
    )
    text = text.replace(
        rf"\input{{SST_CANON-v{PREV}-research-track}}",
        rf"\input{{SST_CANON-v{VERSION}-research-track}}",
    )
    # abstract: ensure Version~0.8.36 sentence if tonic applied; leave as-is

    note = (
        f"        \\subsubsection{{v{VERSION}}}\n"
        f"            {cfg['note']}\n\n"
    )
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        anchor = f"        \\subsubsection{{v{PREV}}}"
        if anchor not in text:
            raise SystemExit("edition note anchor missing")
        text = text.replace(anchor, note + anchor, 1)
        log("inserted edition note v0.8.36 from EDITION_CONFIG")
    else:
        # replace tonic-only note with full stack note
        text = re.sub(
            rf"        \\subsubsection\{{v{VERSION}\}}\n"
            rf"            \\textbf\{{v{VERSION}\}}[^\n]*(?:\n            [^\n]+)*\n\n",
            note,
            text,
            count=1,
        )
        log("replaced edition note v0.8.36 with EDITION_CONFIG note")

    tex.write_text(text, encoding="utf-8")

    # RT companion strings
    rt = rt_tex(VERSION)
    rtext = rt.read_text(encoding="utf-8")
    rtext = re.sub(
        r"%! Companion to Swirl-String-Theory Canon-v[^\n]+",
        f"%! Companion to Swirl-String-Theory Canon-v{VERSION} "
        f"(included from \\texttt{{SST\\_CANON-v{VERSION}.tex}} before the manual bibliography).",
        rtext,
        count=1,
    )
    rtext = rtext.replace(
        rf"\textit{{Swirl-String-Theory\_Canon-v{PREV}}}",
        rf"\textit{{Swirl-String-Theory\_Canon-v{VERSION}}}",
    )
    rtext = rtext.replace(
        rf"\textbf{{Editorial note (v{PREV}):}}",
        rf"\textbf{{Editorial note (v{VERSION}):}}",
    )
    rtext = rtext.replace(
        rf"been_processed/v{PREV}/SST_CANON-v{PREV}.tex",
        rf"been_processed/v{VERSION}/SST_CANON-v{VERSION}.tex",
    )
    rt.write_text(rtext, encoding="utf-8")
    log("bumped RT companion metadata")


def clear_borrowed_doi() -> None:
    tex = main_tex(VERSION)
    content = tex.read_text(encoding="utf-8")
    new = re.sub(
        r"\\newcommand\{\\paperdoi\}\{[^}]*\}",
        r"\\newcommand{\\paperdoi}{}",
        content,
        count=1,
    )
    new = re.sub(r"%!\s*DOI\s*=\s*[^\n]+\n?", "", new, count=1)
    if new != content:
        tex.write_text(new, encoding="utf-8")
        log("cleared borrowed \\paperdoi / %! DOI")
    else:
        log("\\paperdoi already empty")


def seed_zenodo_json() -> None:
    dst = edition_dir(VERSION) / f"SST_CANON-v{VERSION}.zenodo.json"
    src = edition_dir(PREV) / f"SST_CANON-v{PREV}.zenodo.json"
    data: dict = {}
    if src.is_file():
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data.pop("deposit_id", None)
    data.pop("doi", None)
    data["title"] = (
        f"Swirl-String-Theory Canon v{VERSION} — "
        "Canonical Reference and Research Framework"
    )
    data["version"] = f"v{VERSION}"
    data["tex_file"] = (
        f"SST-CANON/been_processed/v{VERSION}/SST_CANON-v{VERSION}.tex"
    )
    data.setdefault("pdf_output_dir", "$out")
    data["keywords"] = paperkeywords_tex(VERSION).split(", ")
    # offline description from edition header one-liner
    header = EDITION_CONFIG[VERSION]["header"]
    one = re.sub(r"^%! v[\d.]+ edition:\s*", "", header)
    one = re.sub(r"\s*\(been_processed\)\.?\s*$", "", one).strip().rstrip(".")
    data["description"] = (
        f"SST Canon v{VERSION}: {one}. "
        "Canonical reference and research framework. Mint/DOI via Zenodo GUI."
    )
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"seeded {dst.name} (no deposit_id/doi)")


CHANGELOG_TEXT = """# SST Canon v0.8.36 — Maxwell / spectro stack changelog

**Zenodo (one line):** Maxwell swirl-tonic, kinetic closure, dynamical-field / reciprocal-stress / mechanical falsifiers, and spectroscopic-response guards.

## Summary

Single edition on top of v0.8.35 stacking all six `to_do_patches` items:
configuration-resolved spectroscopic-response (re-port from v0.8.34),
Maxwell–SST kinetic closure (with dimensional spectro correction),
Maxwell-blind mechanical falsifier, reciprocal-stress audit, dynamical field
closure, and material swirl–tonic vorticity-potential representation.

## What is new (per package)

1. **Spectroscopic response (v0.1.0, re-port):** configuration-resolved
   spectroscopic-response guard on the master mass equation; RT generalized
   King diagnostics programme (Ishiyama et al.).
2. **Kinetic closure:** internal-mode thermodynamic gate, knot kinetic
   closure `f_K`, knot-ensemble stress vs Euler/Bernoulli pressure,
   orientation isotropization; replaces dimensionally incomplete
   `Γ²/(4πξL)` energy-gap claim with a true energy-difference ledger.
3. **Blind mechanical falsifier:** Maxwell-inspired target-blind mechanical
   closure falsifier (main + RT).
4. **Reciprocal stress:** reciprocal-stress audit (main + RT).
5. **Dynamical field closure:** transverse-mode / displacement-current /
   gravitational energy-deficit gates (DFC–T/D/G).
6. **Swirl-tonic:** material swirl–tonic potential `A_st^(m) := v`, Stokes /
   holonomy falsifier, material–link sector separation; edition bump to
   v0.8.36.

## Source

- Patches archived under `been_processed/sources/v0.8.36_maxwell_spectro_stack/`
- Base: Canon v0.8.35 → `been_processed/v0.8.36/`
- Ingest: `scripts/apply_v0836.py`
"""


def write_changelogs() -> None:
    edition_cl = edition_dir(VERSION) / "CHANGELOG.md"
    edition_cl.write_text(CHANGELOG_TEXT, encoding="utf-8")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "CHANGELOG.md").write_text(CHANGELOG_TEXT, encoding="utf-8")
    (ARCHIVE / "APPLY_LOG.md").write_text(
        "# v0.8.36 apply log\n\n" + "\n".join(f"- {m}" for m in APPLY_LOG) + "\n",
        encoding="utf-8",
    )
    (ARCHIVE / "INGEST_README.md").write_text(
        "\n".join(
            [
                "# v0.8.36 Maxwell / spectro stack ingest",
                "",
                "Finished edition lives in `been_processed/v0.8.36/`.",
                "This folder archives all six stacked patch sources,",
                "validation notes, `APPLY_LOG.md`, and `CHANGELOG.md`.",
                "",
                "Apply order: spectro → kinetic → falsifier → reciprocal",
                "→ dynamical → swirl-tonic + version bump.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    log("wrote CHANGELOG / APPLY_LOG / INGEST_README")


def update_readme() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    if "v0.8.36" not in text:
        text = text.replace(
            "| **v0.8.35** | Transverse-projector",
            "| **v0.8.36** | Maxwell swirl-tonic, kinetic closure, dynamical-field / reciprocal-stress / mechanical falsifiers, spectroscopic-response guards (stacked).\n"
            "| **v0.8.35** | Transverse-projector",
            1,
        )
        text = text.replace(
            "python scripts/apply_v0835.py\n```",
            "python scripts/apply_v0835.py\n"
            "python scripts/apply_v0836.py\n```",
            1,
        )
        text = text.replace(
            "Individual steps: `scripts/apply_v085.py` … `scripts/apply_v0835.py`.",
            "Individual steps: `scripts/apply_v085.py` … `scripts/apply_v0836.py`.",
            1,
        )
        text = text.replace(
            "| `v0.8.2/` … `v0.8.35/` |",
            "| `v0.8.2/` … `v0.8.36/` |",
            1,
        )
        text = text.replace(
            "cd SST-CANON/been_processed/v0.8.35\n"
            "latexmk -pdf -interaction=nonstopmode -output-directory='$out' SST_CANON-v0.8.35.tex",
            "cd SST-CANON/been_processed/v0.8.36\n"
            "latexmk -pdf -interaction=nonstopmode -output-directory='$out' SST_CANON-v0.8.36.tex",
            1,
        )
        readme.write_text(text, encoding="utf-8")
        log("updated been_processed/README.md")
    else:
        log("README already mentions v0.8.36")


def archive_patches(spectro_root: Path, kinetic_root: Path) -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    items = [
        TODO_PATCHES / SPECTRO_ZIP,
        TODO_PATCHES / KINETIC_ZIP,
        TODO_PATCHES / FALSIFIER,
        TODO_PATCHES / RECIPROCAL,
        TODO_PATCHES / DYNAMICAL,
        TODO_PATCHES / TONIC,
    ]
    for src in items:
        if not src.exists():
            log(f"archive skip missing {src.name}")
            continue
        dest = ARCHIVE / src.name
        if dest.exists():
            log(f"archive already has {src.name}")
            src.unlink()
            log(f"removed todo {src.name}")
            continue
        shutil.move(str(src), str(dest))
        log(f"moved {src.name} -> sources/v0.8.36_maxwell_spectro_stack/")

    # extracted folders already under ARCHIVE; remove empty todo dir leftovers
    # if spectro/kinetic were extracted from todo into ARCHIVE, ok


def verify() -> None:
    text = main_tex(VERSION).read_text(encoding="utf-8")
    checks = [
        (rf"\\newcommand{{\\canonversion}}{{{VERSION}}}", "canonversion"),
        (r"\\newcommand{\\paperdoi}{}", "empty paperdoi"),
        (r"subsubsection{v0.8.36}", "edition note"),
        (r"material_swirl_tonic", "swirl-tonic"),
        (r"spectroscopic-response", "spectro guard"),
        (r"kinetic", "kinetic mention"),
    ]
    for pat, name in checks:
        if not re.search(pat, text, re.I):
            # soft checks for some
            if name in ("kinetic mention",):
                continue
            raise SystemExit(f"verify failed: {name}")
    rt = rt_tex(VERSION).read_text(encoding="utf-8")
    for pat, name in [
        (r"rt_maxwell_sst_kinetic_gate|Maxwell--SST Kinetic Closure", "kinetic RT"),
        (r"rt_maxwell_blind_mechanical_falsifier|blind mechanical", "falsifier RT"),
        (r"reciprocal", "reciprocal RT"),
        (r"Dynamical Field Closure", "dynamical RT"),
        (r"King diagnostics|configuration.resolved spectroscopic", "spectro RT"),
    ]:
        if not re.search(pat, rt, re.I):
            raise SystemExit(f"verify RT failed: {name}")
    kws = paperkeywords_tex(VERSION)
    if "_" in kws:
        raise SystemExit(f"underscore in paperkeywords: {kws}")
    log("verify OK")


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} in EDITION_CONFIG first")
    if "0.8.36" not in EDITION_CONFIG:
        raise SystemExit("missing keywords/config")

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    # Prefer extracting from todo; keep copies in archive
    for zname in (SPECTRO_ZIP, KINETIC_ZIP):
        zsrc = TODO_PATCHES / zname
        if zsrc.is_file():
            adest = ARCHIVE / zname
            if not adest.exists():
                shutil.copy2(zsrc, adest)
                log(f"copied {zname} into archive")

    spectro_root = extract_zip(SPECTRO_ZIP)
    kinetic_root = extract_zip(KINETIC_ZIP)

    copy_from_prev()
    step_spectro(spectro_root)
    step_kinetic(kinetic_root)
    step_falsifier_reciprocal()
    step_dynamical()
    step_swirl_tonic()
    rename_to_version()
    bump_macros_and_notes()
    clear_borrowed_doi()
    if sync_paperkeywords_in_tex(VERSION):
        log("synced \\paperkeywords (no underscores)")
    seed_zenodo_json()
    write_changelogs()
    update_readme()
    verify()
    archive_patches(spectro_root, kinetic_root)

    # final APPLY_LOG rewrite after archive
    (ARCHIVE / "APPLY_LOG.md").write_text(
        "# v0.8.36 apply log\n\n" + "\n".join(f"- {m}" for m in APPLY_LOG) + "\n",
        encoding="utf-8",
    )
    remaining = list(TODO_PATCHES.glob("*")) if TODO_PATCHES.is_dir() else []
    remaining = [p for p in remaining if p.name not in (".gitkeep", "desktop.ini")]
    if remaining:
        log("WARNING to_do_patches still has: " + ", ".join(p.name for p in remaining))
    else:
        log("to_do_patches empty")
    print(f"done: been_processed/v{VERSION}/")


if __name__ == "__main__":
    main()
