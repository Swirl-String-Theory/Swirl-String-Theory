#!/usr/bin/env python3
"""Create an idempotent SHA-256 manifest for a manuscript package."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

DEFAULT_EXCLUDE_SUFFIXES = {
    ".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk", ".synctex.gz"
}
DEFAULT_EXCLUDE_NAMES = {
    "SHA256SUMS.txt",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def excluded(path: Path) -> bool:
    if path.name in DEFAULT_EXCLUDE_NAMES:
        return True
    lowered = path.name.lower()
    return any(lowered.endswith(suffix) for suffix in DEFAULT_EXCLUDE_SUFFIXES)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="SHA256SUMS.txt")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = root / args.output
    paths = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p != output and not excluded(p)
    )

    lines = [
        f"{digest(path)} *{path.relative_to(root).as_posix()}"
        for path in paths
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote {output} with {len(lines)} entries")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
