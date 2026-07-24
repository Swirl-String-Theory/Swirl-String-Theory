#!/usr/bin/env python3
"""Build v0.8.26 from v0.8.25 by applying the audit patch pack (CRLF-preserving)."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
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

VERSION = "0.8.26"
PREV = "0.8.25"
PACKAGE = ROOT.parent / "to_do_patches" / "0.8.25-to-0.8.26"
PATCH_DIR = PACKAGE / "patches"
ARCHIVE = ROOT / "sources" / "v0.8.26_audit_patch_pack"
NONRELEASE = f"SST_NONRELEASE_SPECULATIVE_RESEARCH-v0.1.tex"

PATCHES: list[tuple[str, str]] = [
    ("01_fmax_rydberg_factor2.diff", "ERRATUM"),
    ("02_rho_calc_retirement.diff", "NOTATION RETIREMENT"),
    ("03_M0_transparency_guard.diff", "eq:M0_me_quarter_reduction"),
    ("04_rhof_provenance_guard.diff", "PROVENANCE GUARD"),
    ("05_label_discipline.diff", "DERIVED within the calibrated chain"),
    ("06_rt_dedup_and_label.diff", "duplication guard"),
]


def _is_crlf(path: Path) -> bool:
    data = path.read_bytes()
    return data.count(b"\r\n") > 0 and (data.count(b"\n") - data.count(b"\r\n")) == 0


def rewrite_patch_bytes(src: Path) -> bytes:
    """Rewrite underscore patch paths to dotted v0.8.26 filenames; keep CRLF."""
    raw = src.read_bytes()
    # Drop git headers that can cause silent skips (line-wise, preserve endings).
    out_lines: list[bytes] = []
    for line in raw.splitlines(keepends=True):
        if line.startswith(b"diff --git ") or line.startswith(b"index "):
            continue
        out_lines.append(
            line.replace(b"SST_CANON-v0_8_25", f"SST_CANON-v{VERSION}".encode("ascii"))
        )
    return b"".join(out_lines)


def git_apply_bytes(patch_body: bytes, target: Path) -> None:
    with tempfile.NamedTemporaryFile(suffix=".diff", delete=False) as tmp:
        tmp.write(patch_body)
        tmp_path = Path(tmp.name)
    try:
        for mode in ("--check", None):
            args = ["git", "apply", "--whitespace=nowarn"]
            if mode:
                args.append(mode)
            args.append(str(tmp_path))
            proc = subprocess.run(args, cwd=target, capture_output=True, text=True)
            combined = (proc.stdout or "") + (proc.stderr or "")
            if proc.returncode != 0 or "Skipped patch" in combined:
                raise SystemExit(
                    f"{' '.join(args)} failed (rc={proc.returncode}):\n{combined}"
                )
    finally:
        tmp_path.unlink(missing_ok=True)


def marker_present(marker: str) -> bool:
    needle = marker if not marker.startswith("eq:") else f"\\label{{{marker}}}"
    for path in (main_tex(VERSION), rt_tex(VERSION)):
        if path.is_file() and needle in path.read_text(encoding="utf-8"):
            return True
    return False


def _write_tex_crlf(path: Path, text: str) -> None:
    """Write tex with CRLF line endings (canon convention)."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))


def insert_edition_note() -> None:
    cfg = EDITION_CONFIG[VERSION]
    main = main_tex(VERSION)
    text = main.read_bytes().decode("utf-8")
    if f"\\subsubsection{{v{VERSION}}}" in text:
        print(f"SKIP edition note v{VERSION}: already present")
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


def clear_borrowed_doi() -> None:
    tex = main_tex(VERSION)
    content = tex.read_bytes().decode("utf-8")
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


def archive_sources() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PACKAGE / "README_PATCH_PACK.md", ARCHIVE / "README_PATCH_PACK.md")
    shutil.copy2(PACKAGE / "verify_v0_8_25_patched.py", ARCHIVE / "verify_v0_8_25_patched.py")
    for name, _ in PATCHES:
        shutil.copy2(PATCH_DIR / name, ARCHIVE / name)
    final_src = PACKAGE / "final"
    if final_src.is_dir():
        final_dst = ARCHIVE / "final"
        if final_dst.exists():
            shutil.rmtree(final_dst)
        shutil.copytree(final_src, final_dst)
    (ARCHIVE / "INGEST_README.md").write_text(
        "\n".join(
            [
                "# v0.8.26 audit patch pack (archived)",
                "",
                "Applied in order `01`–`06` onto a copy of `been_processed/v0.8.25/`.",
                "Finished edition: `been_processed/v0.8.26/`.",
                "Do not mint/push Zenodo from the agent — user owns mint/push.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"archived under {ARCHIVE.relative_to(ROOT)}")


def copy_nonrelease() -> None:
    src = edition_dir(PREV) / NONRELEASE
    if not src.is_file():
        print(f"no nonrelease to copy ({NONRELEASE})")
        return
    shutil.copy2(src, edition_dir(VERSION) / NONRELEASE)
    print(f"copied {NONRELEASE}")


def apply_metadata_crlf(version: str) -> None:
    """Run apply_metadata then restore CRLF if the round-trip dropped them."""
    apply_metadata(version)
    for path in (main_tex(version), rt_tex(version)):
        raw = path.read_bytes()
        if b"\r\n" in raw:
            continue
        # convert LF-only back to CRLF for canon sources
        text = raw.decode("utf-8")
        path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        print(f"restored CRLF: {path.name}")


def main() -> None:
    if VERSION not in EDITION_CONFIG:
        raise SystemExit(f"register {VERSION} in canon_edition.EDITION_CONFIG first")
    if not edition_dir(PREV).is_dir():
        raise SystemExit(f"v{PREV} folder missing")
    if not PATCH_DIR.is_dir():
        raise SystemExit(f"missing patch dir: {PATCH_DIR}")

    copy_edition(PREV, VERSION)
    copy_nonrelease()

    target = edition_dir(VERSION)
    for name, marker in PATCHES:
        src = PATCH_DIR / name
        if not src.is_file():
            raise SystemExit(f"missing patch: {src}")
        print(f"Applying {name}")
        git_apply_bytes(rewrite_patch_bytes(src), target)
        if not marker_present(marker):
            raise SystemExit(f"after apply, marker still missing: {marker}")
        print(f"Applied {name}")

    for path in (main_tex(VERSION), rt_tex(VERSION)):
        if not _is_crlf(path):
            raise SystemExit(f"CRLF lost after patches: {path}")

    # Metadata bump AFTER patches (patch 06 matches Editorial note v0.8.25).
    apply_metadata_crlf(VERSION)
    insert_edition_note()
    clear_borrowed_doi()
    seed_zenodo_json()
    archive_sources()

    text = main_tex(VERSION).read_text(encoding="utf-8")
    if f"\\subsubsection{{v{VERSION}}}" not in text:
        raise SystemExit(f"missing edition note v{VERSION}")
    if f"\\input{{SST_CANON-v{VERSION}-research-track}}" not in text:
        raise SystemExit("main must \\input dotted research-track name")
    if "SST_NONRELEASE_SPECULATIVE_RESEARCH" in text:
        raise SystemExit("main Canon must not input the non-release speculative appendix")
    if not _is_crlf(main_tex(VERSION)) or not _is_crlf(rt_tex(VERSION)):
        raise SystemExit("CRLF lost after metadata")

    print(f"v{VERSION} build complete.")


if __name__ == "__main__":
    main()
