#!/usr/bin/env python3
"""Minimal unified-diff applicator (context match) for Canon ingest scripts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: list[str]  # including leading ' ', '+', '-'


def parse_unified_diff(text: str) -> list[tuple[str, list[Hunk]]]:
    """Return list of (target_path, hunks)."""
    text = text.replace("\r\n", "\n")
    files: list[tuple[str, list[Hunk]]] = []
    current_path: str | None = None
    hunks: list[Hunk] = []
    i = 0
    lines = text.split("\n")
    hunk_re = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

    while i < len(lines):
        line = lines[i]
        if line.startswith("--- "):
            if current_path is not None:
                files.append((current_path, hunks))
            # next +++ line
            i += 1
            if i >= len(lines) or not lines[i].startswith("+++ "):
                raise ValueError(f"expected +++ after --- at line {i}")
            plus = lines[i][4:].strip()
            current_path = plus.split("\t")[0].strip()
            hunks = []
            i += 1
            continue
        m = hunk_re.match(line)
        if m:
            old_start = int(m.group(1))
            old_count = int(m.group(2) or "1")
            new_start = int(m.group(3))
            new_count = int(m.group(4) or "1")
            body: list[str] = []
            old_seen = 0
            new_seen = 0
            i += 1
            while i < len(lines) and (
                old_seen < old_count or new_seen < new_count
            ):
                bl = lines[i]
                if bl.startswith("\\"):  # No newline at end of file
                    i += 1
                    continue
                if bl == "":
                    # bare empty line → treat as context blank
                    body.append(" ")
                    old_seen += 1
                    new_seen += 1
                    i += 1
                    continue
                tag = bl[:1]
                if tag not in (" ", "+", "-"):
                    break
                body.append(bl)
                if tag in (" ", "-"):
                    old_seen += 1
                if tag in (" ", "+"):
                    new_seen += 1
                i += 1
            hunks.append(
                Hunk(old_start, old_count, new_start, new_count, body)
            )
            continue
        i += 1

    if current_path is not None:
        files.append((current_path, hunks))
    return files


def _hunk_old_block(hunk: Hunk) -> list[str]:
    out: list[str] = []
    for line in hunk.lines:
        tag = line[:1]
        payload = line[1:]
        if tag in (" ", "-"):
            out.append(payload)
        elif tag == "+":
            continue
        else:
            out.append(line)
    return out


def _hunk_new_block(hunk: Hunk) -> list[str]:
    out: list[str] = []
    for line in hunk.lines:
        tag = line[:1]
        payload = line[1:]
        if tag in (" ", "+"):
            out.append(payload)
        elif tag == "-":
            continue
        else:
            out.append(line)
    return out


def _find_block(hay: list[str], needle: list[str], hint: int) -> int:
    """Find needle in hay; prefer near 1-based hint line."""
    if not needle:
        return max(0, hint - 1)
    # Exact search
    candidates: list[int] = []
    n = len(needle)
    for i in range(0, len(hay) - n + 1):
        if hay[i : i + n] == needle:
            candidates.append(i)
    if not candidates:
        # Strip trailing whitespace fuzzy
        needle_stripped = [x.rstrip() for x in needle]
        for i in range(0, len(hay) - n + 1):
            if [x.rstrip() for x in hay[i : i + n]] == needle_stripped:
                candidates.append(i)
    if not candidates:
        raise ValueError(
            "context not found for hunk near line "
            f"{hint}: {needle[0][:80]!r} ..."
        )
    hint0 = max(0, hint - 1)
    return min(candidates, key=lambda c: abs(c - hint0))


def apply_hunks_to_text(text: str, hunks: list[Hunk]) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    # Apply from bottom to top so earlier line numbers stay valid
    for hunk in sorted(hunks, key=lambda h: h.old_start, reverse=True):
        old_block = _hunk_old_block(hunk)
        new_block = _hunk_new_block(hunk)
        pos = _find_block(lines, old_block, hunk.old_start)
        lines[pos : pos + len(old_block)] = new_block
    return "\n".join(lines)


def apply_unified_diff(patch_text: str, workdir: Path) -> None:
    for target_name, hunks in parse_unified_diff(patch_text):
        path = workdir / Path(target_name).name
        if not path.is_file():
            raise SystemExit(f"patch target missing: {path}")
        original = path.read_text(encoding="utf-8")
        nl = "\r\n" if "\r\n" in original else "\n"
        updated = apply_hunks_to_text(original, hunks)
        if nl != "\n":
            updated = updated.replace("\n", nl)
        path.write_bytes(updated.encode("utf-8"))
        print(f"applied {len(hunks)} hunk(s) -> {path.name}")
