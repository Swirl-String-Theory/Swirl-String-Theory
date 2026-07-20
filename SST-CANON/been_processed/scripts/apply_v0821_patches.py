#!/usr/bin/env python3
"""Apply eight-source patch series onto v0.8.21 (path-rewritten git apply)."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from _paths import ROOT, SCRIPTS_DIR

from canon_edition import edition_dir, rt_tex

VERSION = "0.8.21"
PATCH_PKG = (
    ROOT.parent
    / "to_do_patches"
    / "SST_CANON-v0.8.20-eight-source-patch-series"
)
PATCH_DIR = PATCH_PKG / "patches"
ARCHIVE_DIR = ROOT / "sources" / "v0.8.21_eight_source_patch_series"

# First unique content label introduced by each patch (idempotent SKIP).
PATCH_MARKERS: list[tuple[str, str]] = [
    ("0001-sphsymm-curl-spectrum.diff", "subsec:rt_spherical_curl_spectrum_capacity"),
    ("0002-upperbounds-writhe-helicity.diff", "subsec:rt_upper_bounds_writhe_helicity"),
    ("0003-gehring-link-criticality.diff", "subsec:rt_gehring_contact_measure"),
    ("0004-biotsavart-operator.diff", "subsec:rt_biot_savart_realizability"),
    ("0005-hodge-topology-circulation.diff", "subsec:rt_hodge_complete_reconstruction"),
    ("0006-helicity-forms-mapping-class.diff", "subsubsec:rt_helicity_mapping_class"),
    ("0007-isoperimetric-domain-spectrum.diff", "subsubsec:rt_isoperimetric_domain_shape"),
    ("0008-ridgerunner-certification.diff", "subsubsec:rt_polygonal_smooth_certification"),
]


def rewrite_patch(src: Path) -> str:
    """Rewrite v0.8.20 filenames; drop git index headers that can cause silent skips."""
    lines: list[str] = []
    for line in src.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("diff --git ") or line.startswith("index "):
            continue
        lines.append(line.replace("SST_CANON-v0.8.20", f"SST_CANON-v{VERSION}"))
    return "".join(lines)


def label_present(marker: str) -> bool:
    needle = f"\\label{{{marker}}}"
    for path in (rt_tex(VERSION), edition_dir(VERSION) / f"SST_CANON-v{VERSION}.tex"):
        if path.is_file() and needle in path.read_text(encoding="utf-8"):
            return True
    return False


def git_apply(patch_body: str, target: Path) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".diff",
        delete=False,
        newline="\n",
    ) as tmp:
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


def archive_sources() -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for name, _ in PATCH_MARKERS:
        src = PATCH_DIR / name
        dst = ARCHIVE_DIR / name
        if src.is_file():
            shutil.copy2(src, dst)
    readme = ARCHIVE_DIR / "README.md"
    if not readme.is_file():
        readme.write_text(
            "\n".join(
                [
                    "# v0.8.21 eight-source patch series (archived)",
                    "",
                    "Copies of the diffs applied to build `been_processed/v0.8.21/`.",
                    "",
                    "Provenance and source PDFs live in:",
                    "",
                    "`SST-CANON/to_do_patches/SST_CANON-v0.8.20-eight-source-patch-series/`",
                    "",
                    "See `SOURCE_PROVENANCE.md` and `PATCH_SERIES.md` in that package.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    print(f"Archived patches under {ARCHIVE_DIR.relative_to(ROOT)}")


def main() -> None:
    target = edition_dir(VERSION)
    if not target.is_dir():
        raise SystemExit(f"v{VERSION} missing; run apply_v0821.py first")
    if not PATCH_DIR.is_dir():
        raise SystemExit(f"patch dir missing: {PATCH_DIR}")

    for name, marker in PATCH_MARKERS:
        src = PATCH_DIR / name
        if not src.is_file():
            raise SystemExit(f"missing patch: {src}")
        if label_present(marker):
            print(f"SKIP {name}: {marker} already present")
            continue
        print(f"Applying {name}")
        git_apply(rewrite_patch(src), target)
        if not label_present(marker):
            raise SystemExit(f"after apply, marker still missing: {marker}")
        print(f"Applied {name}")

    archive_sources()
    print(f"v{VERSION} eight-source patches done.")


if __name__ == "__main__":
    main()
