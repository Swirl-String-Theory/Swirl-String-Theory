#!/usr/bin/env python3
"""Build v0.8.27 hygiene edition from v0.8.26 (dedup, labels, canonversion, benchmarks)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from _paths import ROOT

from canon_edition import (
    EDITION_CONFIG,
    apply_metadata,
    copy_edition,
    edition_dir,
    main_tex,
    rt_tex,
)

VERSION = "0.8.27"
PREV = "0.8.26"
ARCHIVE = ROOT / "sources" / "v0.8.27_hygiene"
NONRELEASE = "SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1.tex"


def _write_tex_crlf(path: Path, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))


def _read_tex(path: Path) -> str:
    """Read tex as LF-normalized Unicode (write back via _write_tex_crlf)."""
    return (
        path.read_bytes()
        .decode("utf-8")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


def _is_crlf(path: Path) -> bool:
    data = path.read_bytes()
    return data.count(b"\r\n") > 0 and (data.count(b"\n") - data.count(b"\r\n")) == 0


def copy_nonrelease() -> None:
    src = edition_dir(PREV) / NONRELEASE
    if src.is_file():
        shutil.copy2(src, edition_dir(VERSION) / NONRELEASE)
        print(f"copied {NONRELEASE}")


def add_main_section_labels(text: str) -> str:
    """Add missing Selective-Recovery subsection labels for RT stubs to ref."""
    replacements = [
        (
            "    \\subsection{Thermodynamic Radiation Interface}\n\n",
            "    \\subsection{Thermodynamic Radiation Interface}\n"
            "        \\label{subsec:integration_thermo}\n\n",
        ),
        (
            "    \\subsection{Minimal Coupling Interface to Quantum Electrodynamics}\n\n",
            "    \\subsection{Minimal Coupling Interface to Quantum Electrodynamics}\n"
            "        \\label{subsec:integration_qed}\n\n",
        ),
        (
            "    \\subsection{Ribbon-Invariant Chirality Refinement}\n\n",
            "    \\subsection{Ribbon-Invariant Chirality Refinement}\n"
            "        \\label{subsec:integration_ribbon}\n\n",
        ),
    ]
    for old, new in replacements:
        if "\\label{subsec:integration_" in text and old not in text:
            continue
        if old not in text:
            raise SystemExit(f"main label anchor missing: {old!r}")
        text = text.replace(old, new, 1)
    return text


def strip_commented_duplicate_labels(text: str) -> str:
    """Remove commented % ... \\label{sec:...} lines that duplicate active labels."""
    labels = (
        "sec:consistency",
        "sec:delay",
        "sec:atomic",
        "sec:spectroscopy",
        "sec:unification",
    )
    for lab in labels:
        pattern = rf"^%+[ \t]*\\label\{{{re.escape(lab)}\}}[ \t]*\r?\n"
        text, n = re.subn(pattern, "", text, count=1, flags=re.MULTILINE)
        if n != 1:
            raise SystemExit(f"expected one commented label for {lab}, got {n}")
    return text


def fill_main_benchmark_table(text: str) -> str:
    """Populate empty predictive cells from archived exact-closure identity (MeV)."""
    old = r"""        \begin{tabular}{lrrrrc}
        \hline
        Particle & $m_{\mathrm{exp}}$ (MeV) & $m_{\mathrm{SST}}$ (MeV) & rel.\ error & mode & class \\
        \hline
        $e$   & 0.51099895 & 0.51099895 & 0 & predictive/closure & $3_1$ \\
        $\mu$ & 105.6583745 & \dots & \dots & predictive & candidate torus class \\
        $\tau$& 1776.86 & \dots & \dots & predictive & candidate torus class \\
        $p$   & 938.272088 & \dots & \dots & predictive or closure & composite class \\
        $n$   & 939.565420 & \dots & \dots & predictive or closure & composite class \\
        \hline
        \end{tabular}"""
    new = r"""        \begin{tabular}{lrrrrc}
        \hline
        Particle & $m_{\mathrm{exp}}$ (MeV) & $m_{\mathrm{SST}}$ (MeV) & rel.\ error & mode & class \\
        \hline
        $e$   & 0.51099895 & 0.51099895 & 0 & exact-closure & $3_1$ \\
        $\mu$ & 105.6583745 & 105.6583745 & 0 & exact-closure & candidate torus class \\
        $\tau$& 1776.86 & 1776.86 & 0 & exact-closure & candidate torus class \\
        $p$   & 938.272088 & 938.272088 & 0 & exact-closure & composite class \\
        $n$   & 939.565420 & 939.565420 & 0 & exact-closure & composite class \\
        \hline
        \end{tabular}"""
    if old not in text:
        raise SystemExit("main benchmark tabular block not found")
    text = text.replace(old, new, 1)
    note_old = (
        "        \\textbf{[CRITICAL NOTE]} A future v0.8.x benchmark appendix should include:"
    )
    note_new = (
        "        \\textbf{[CRITICAL NOTE]} Table~\\ref{tab:benchmark_summary_structure} "
        "is populated from the archived exact-closure identity "
        "\\texttt{SST-CANON/archive/proofs/figures/"
        "SST\\_invariant\\_kernel\\_benchmarks\\_exact\\_closure.csv} "
        "(and the companion "
        "\\texttt{SST\\_benchmarks\\_table\\_exact\\_closure.tex}): "
        "for the listed leptons/nucleons the SST column equals the experimental "
        "mass at machine precision in that archive (mode \\emph{exact-closure}, "
        "not an independent mass prediction). A future expanded benchmark appendix "
        "should still include:"
    )
    if note_old not in text:
        raise SystemExit("main benchmark CRITICAL NOTE anchor missing")
    return text.replace(note_old, note_new, 1)


def replace_rt_span(text: str, start: str, end: str, replacement: str) -> str:
    """Replace from start marker through the character before end marker."""
    i0 = text.find(start)
    if i0 < 0:
        raise SystemExit(f"RT start not found: {start!r}")
    i1 = text.find(end, i0 + len(start))
    if i1 < 0:
        raise SystemExit(f"RT end not found after start: {end!r}")
    return text[:i0] + replacement + text[i1:]


def stub_rt_duplicates(text: str) -> str:
    """Replace the seven duplicated RT subsections with main-canon pointers."""
    stubs = {
        "thermo": (
            "\\subsection{Thermodynamic Radiation Interface}\n"
            "\\noindent\n"
            "Authoritative text: main-canon Selective Recovery, "
            "\\S\\ref{subsec:integration_thermo}. "
            "This research-track full-text copy is retired in v0.8.27 "
            "(de-duplication; main canon is Level~1).\n\n"
        ),
        "qed": (
            "\\subsection{Minimal Coupling Interface to QED}\n"
            "\\noindent\n"
            "Authoritative text: main-canon Selective Recovery, "
            "\\S\\ref{subsec:integration_qed}. "
            "This research-track full-text copy is retired in v0.8.27.\n\n"
        ),
        "ribbon": (
            "\\subsection{Ribbon-Invariant Chirality Refinement}\n"
            "\\noindent\n"
            "Authoritative text: main-canon Selective Recovery, "
            "\\S\\ref{subsec:integration_ribbon}. "
            "This research-track full-text copy is retired in v0.8.27. "
            "RT-only framed-tube / twist-ladder modules below remain.\n\n"
        ),
        "particle": (
            "\\subsection{Particle-Candidate Mapping Layer}\n"
            "\\noindent\n"
            "Authoritative dictionary: main-canon "
            "\\S\\ref{subsec:integration_knotmap} / "
            "Table~\\ref{tab:particle_candidate_mapping}. "
            "The former research-track duplicate table "
            "\\texttt{tab:particle-candidates} is retired in v0.8.27. "
            "RT-only extensions that follow (quark-like twist knots, "
            "twist-ladder, baryon analogues, parked Higgs hypothesis) are retained.\n\n"
        ),
        "pauli": (
            "\\subsection{Hydrodynamic Exchange and the Pauli Barrier}\n"
            "\\noindent\n"
            "Authoritative text: main-canon Selective Recovery, "
            "\\S\\ref{subsec:integration_pauli}. "
            "This research-track full-text copy is retired in v0.8.27 "
            "(Pauli label already harmonised to [ORTHODOX] in v0.8.26).\n\n"
        ),
        "bench": (
            "\\subsection{Numerical Benchmark Layer}\n"
            "\\noindent\n"
            "Authoritative benchmark layer: main-canon "
            "\\S\\ref{subsec:integration_benchmarks} / "
            "Table~\\ref{tab:benchmark_summary_structure}, "
            "populated in v0.8.27 from the archived exact-closure CSV "
            "\\texttt{SST-CANON/archive/proofs/figures/"
            "SST\\_invariant\\_kernel\\_benchmarks\\_exact\\_closure.csv}. "
            "This research-track duplicate table with empty predictive-candidate "
            "cells is retired. Diagnostic archives that follow "
            "(helicity-by-base, trefoil-closure, G7) remain research-track.\n\n"
        ),
        "gauge": (
            "\\subsection{Gauge-Sector Roadmap}\n"
            "\\noindent\n"
            "Authoritative text: main-canon Selective Recovery, "
            "\\S\\ref{subsec:integration_gauge}. "
            "This research-track full-text copy is retired in v0.8.27. "
            "Contact-channel / rank-nine diagnostics remain in later RT sections.\n\n"
        ),
    }

    text = replace_rt_span(
        text,
        "\\subsection{Thermodynamic Radiation Interface}\n",
        "\\subsection{Minimal Coupling Interface to QED}\n",
        stubs["thermo"],
    )
    text = replace_rt_span(
        text,
        "\\subsection{Minimal Coupling Interface to QED}\n",
        "\\subsection{Ribbon-Invariant Chirality Refinement}\n",
        stubs["qed"],
    )
    text = replace_rt_span(
        text,
        "\\subsection{Ribbon-Invariant Chirality Refinement}\n",
        "\\subsection{Particle-Candidate Mapping Layer}\n",
        stubs["ribbon"],
    )
    text = replace_rt_span(
        text,
        "\\subsection{Particle-Candidate Mapping Layer}\n",
        "\\subsection{Quark-Like Twist Knots as Quasi-Unknot Defects}\n",
        stubs["particle"],
    )
    text = replace_rt_span(
        text,
        "\\subsection{Hydrodynamic Exchange and the Pauli Barrier}\n",
        "\\subsection{Numerical Benchmark Layer}\n",
        stubs["pauli"],
    )
    text = replace_rt_span(
        text,
        "\\subsection{Numerical Benchmark Layer}\n",
        "\\subsection{Helicity-by-base archive (diagnostic layer)}\n",
        stubs["bench"],
    )
    text = replace_rt_span(
        text,
        "\\subsection{Gauge-Sector Roadmap}\n",
        "\\section{Dark-sector and galactic canonization execution package (v0.8.x)}\n",
        stubs["gauge"],
    )

    old_guard = (
        "\\textbf{[CRITICAL NOTE] (duplication guard):} several subsections of this part "
        "(\\emph{Thermodynamic Radiation Interface}, \\emph{Minimal Coupling Interface to QED}, "
        "\\emph{Ribbon-Invariant Chirality Refinement}, \\emph{Particle-Candidate Mapping Layer}, "
        "\\emph{Hydrodynamic Exchange and the Pauli Barrier}, \\emph{Numerical Benchmark Layer}, "
        "\\emph{Gauge-Sector Roadmap}) currently still have full-text counterparts inside the main "
        "canon (Selective Recovery layer). Until de-duplication is executed, the main-canon "
        "versions are authoritative (Level~1 of the source hierarchy) and any label divergence "
        "must be resolved in favour of the main canon."
    )
    new_guard = (
        "\\textbf{[CRITICAL NOTE] (duplication resolved in v0.8.27):} the seven Selective-Recovery "
        "subsections formerly duplicated here are now main-canon only "
        "(Level~1); this companion retains pointer stubs plus RT-only extensions "
        "(quark-like / twist-ladder / baryon-analogue / diagnostic-archive modules)."
    )
    if old_guard not in text:
        raise SystemExit("RT duplication guard text not found")
    return text.replace(old_guard, new_guard, 1)


def insert_canonversion_macro(text: str) -> str:
    """Define \\canonversion near other paper macros."""
    if "\\newcommand{\\canonversion}" in text:
        return text
    anchor = f"\\newcommand{{\\papertitle}}{{Swirl-String-Theory Canon-v{VERSION}}}"
    if anchor not in text:
        # before metadata bump, title still has PREV
        anchor = f"\\newcommand{{\\papertitle}}{{Swirl-String-Theory Canon-v{PREV}}}"
    if anchor not in text:
        raise SystemExit("papertitle anchor for canonversion missing")
    injection = (
        f"\\newcommand{{\\canonversion}}{{{VERSION}}}\n"
        + anchor
    )
    return text.replace(anchor, injection, 1)


def hygiene_stale_version_strings(main: str, rt: str) -> tuple[str, str]:
    """Retarget misleading 'present v0.8.x architecture' wording; keep historical notes."""
    main = main.replace(
        "In the present v0.8.10 architecture,",
        "In the present \\canonversion{} architecture,",
        1,
    )
    main = main.replace(
        "algebraically closed under the v0.8.18 calibration chain,",
        "algebraically closed under the present (\\canonversion{}) calibration chain,",
        1,
    )
    main = main.replace(
        "In v0.8.1, the benchmark layer is retained as a reproducibility requirement",
        "In the present canon, the benchmark layer is retained as a reproducibility requirement",
        1,
    )
    main = main.replace(
        "The gauge layer is retained in v0.8.1 only as a roadmap statement.",
        "The gauge layer is retained only as a roadmap statement.",
        1,
    )
    # RT editorial note may still cite old main filename after copy.
    rt = rt.replace(
        f"SST\\_CANON-v{PREV}.tex",
        f"SST\\_CANON-v{VERSION}.tex",
    )
    rt = rt.replace(
        "SST\\_CANON-v0.8.25.tex",
        f"SST\\_CANON-v{VERSION}.tex",
    )
    return main, rt


def insert_edition_note() -> None:
    cfg = EDITION_CONFIG[VERSION]
    main = main_tex(VERSION)
    text = _read_tex(main)
    if f"\\subsubsection{{v{VERSION}}}" in text:
        print(f"SKIP edition note v{VERSION}")
        return
    anchor = f"        \\subsubsection{{v{cfg['prev']}}}"
    if anchor not in text:
        raise SystemExit(f"edition-note anchor not found: {anchor}")
    block = (
        f"        \\subsubsection{{v{VERSION}}}\n"
        f"            {cfg['note']}\n\n"
    )
    _write_tex_crlf(main, text.replace(anchor, block + anchor, 1))
    print(f"Inserted edition note v{VERSION}")


def apply_metadata_crlf(version: str) -> None:
    apply_metadata(version)
    for path in (main_tex(version), rt_tex(version)):
        raw = path.read_bytes()
        if b"\r\n" in raw and (raw.count(b"\n") - raw.count(b"\r\n")) == 0:
            continue
        text = raw.decode("utf-8")
        _write_tex_crlf(path, text)
        print(f"restored CRLF: {path.name}")


def clear_borrowed_doi() -> None:
    tex = main_tex(VERSION)
    content = _read_tex(tex)
    new = re.sub(
        r"\\newcommand\{\\paperdoi\}\{[^}]+\}",
        r"\\newcommand{\\paperdoi}{}",
        content,
        count=1,
    )
    new = re.sub(r"%!\s*DOI\s*=\s*[^\n]+\n?", "", new, count=1)
    if new != content:
        _write_tex_crlf(tex, new)
        print("cleared borrowed \\paperdoi")


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
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"seeded {dst.name} (mint-ready local only)")


def write_audit_archive(audit_body: str) -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "SECTION_DEDUP_AUDIT.md").write_text(audit_body, encoding="utf-8")
    (ARCHIVE / "INGEST_README.md").write_text(
        "\n".join(
            [
                "# v0.8.27 hygiene (archived)",
                "",
                "Built from `been_processed/v0.8.26/` via `scripts/apply_v0827.py`.",
                "User owns Zenodo mint/push.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"archived under {ARCHIVE.relative_to(ROOT)}")


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} first")
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} missing; build v0.8.26 first")

    copy_edition(PREV, VERSION)
    copy_nonrelease()

    main = _read_tex(main_tex(VERSION))
    rt = _read_tex(rt_tex(VERSION))

    audit = "\n".join(
        [
            "# v0.8.27 section dedup audit",
            "",
            "Main Selective Recovery remains Level-1. RT full-text of the seven",
            "guarded subsections is replaced by pointer stubs. RT-only modules",
            "between Particle-Candidate and Hydrodynamic (quark-like, twist-ladder,",
            "baryon analogues, Higgs parked) are retained.",
            "",
            "| Section | Main label | RT action |",
            "|---------|------------|-----------|",
            "| Thermodynamic Radiation | subsec:integration_thermo (added) | stub |",
            "| Minimal Coupling QED | subsec:integration_qed (added) | stub |",
            "| Ribbon-Invariant Chirality | subsec:integration_ribbon (added) | stub |",
            "| Particle-Candidate Mapping | subsec:integration_knotmap | stub; keep RT extensions |",
            "| Hydrodynamic / Pauli | subsec:integration_pauli | stub |",
            "| Numerical Benchmark | subsec:integration_benchmarks | stub; main table filled |",
            "| Gauge-Sector Roadmap | subsec:integration_gauge | stub |",
            "",
            "Conflicts: none material; main already had richer Pauli/gauge notes.",
            "Benchmark: archived exact-closure CSV used (identity masses, not new predictions).",
            "",
        ]
    )

    main = add_main_section_labels(main)
    main = strip_commented_duplicate_labels(main)
    main = fill_main_benchmark_table(main)
    rt = stub_rt_duplicates(rt)
    main = insert_canonversion_macro(main)
    main, rt = hygiene_stale_version_strings(main, rt)

    _write_tex_crlf(main_tex(VERSION), main)
    _write_tex_crlf(rt_tex(VERSION), rt)

    apply_metadata_crlf(VERSION)
    # Re-assert canonversion after metadata (papertitle rewrite may run first).
    main2 = _read_tex(main_tex(VERSION))
    if "\\newcommand{\\canonversion}" not in main2:
        main2 = insert_canonversion_macro(main2)
        _write_tex_crlf(main_tex(VERSION), main2)
    # Ensure Version line can also mention macro optionally — leave Version vX.Y.Z explicit.
    insert_edition_note()
    clear_borrowed_doi()
    seed_zenodo_json()
    write_audit_archive(audit)

    main_f = _read_tex(main_tex(VERSION))
    rt_f = _read_tex(rt_tex(VERSION))
    checks = [
        (f"\\subsubsection{{v{VERSION}}}" in main_f, "edition note"),
        (f"\\newcommand{{\\canonversion}}{{{VERSION}}}" in main_f, "canonversion"),
        ("duplication resolved in v0.8.27" in rt_f, "dedup guard"),
        ("\\label{subsec:integration_thermo}" in main_f, "thermo label"),
        ("%        \\label{sec:consistency}" not in main_f, "commented consistency gone"),
        ("105.6583745 & 105.6583745 & 0 & exact-closure" in main_f, "benchmark filled"),
        ("predictive candidate" not in rt_f, "RT empty predictive cells gone"),
        ("SST_NONRELEASE_SPECULATIVE_RESEARCH" not in main_f, "no nonrelease input"),
        (_is_crlf(main_tex(VERSION)) and _is_crlf(rt_tex(VERSION)), "CRLF"),
        ("\\subsection{Quark-Like Twist Knots" in rt_f, "RT-only quark module kept"),
    ]
    for ok, name in checks:
        if not ok:
            raise SystemExit(f"verify failed: {name}")
        print(f"OK {name}")

    print(f"v{VERSION} hygiene build complete.")


if __name__ == "__main__":
    main()
