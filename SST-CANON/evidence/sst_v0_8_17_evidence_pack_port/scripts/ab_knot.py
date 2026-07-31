#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ab_knot.py
==========
Self-contained parser + evaluator for the David Fremlin <AB>...</AB> ideal-knot
Fourier format (https://david.fremlin.de/knots/), e.g.:

    <AB Id="3:1:1" Conway="3" L="16.371637" D=" 1.000000">
      <Coeff I="  1" A=" ax, ay, az" B=" bx, by, bz" />
      ...
    </AB>

The curve is   r(s) = sum_j  A_j cos(j s) + B_j sin(j s),   s in [0, 2 pi).
Indices I=j may be sparse (missing harmonics are treated as zero).

This module is dependency-light (numpy only) and produces output compatible with
the helicity pipeline in sst_helicity.py:
  * eval_AB(coeffs, s) -> (x, y, z)   matches eval_fourier_block(...)
  * parse_AB_multi(path) -> [(header, coeffs), ...]   matches parse_fseries_multi(...)
    with coeffs a dict {'a_x','b_x','a_y','b_y','a_z','b_z'} of numpy arrays
    indexed by harmonic j (index 0 = DC, unused by the <AB> format).
"""
from __future__ import annotations
import re
from typing import Dict, List, Tuple, Any
import numpy as np

_AB_HEADER = re.compile(r'<AB\b([^>]*)>', re.IGNORECASE)
_ATTR = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
_COEFF = re.compile(
    r'<Coeff\b[^>]*?\bI\s*=\s*"\s*(\d+)\s*"'
    r'[^>]*?\bA\s*=\s*"([^"]*)"'
    r'[^>]*?\bB\s*=\s*"([^"]*)"',
    re.IGNORECASE | re.DOTALL,
)


def _triplet(text: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 3:
        raise ValueError(f"expected 3 comma-separated values, got: {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def parse_AB_blocks(text: str) -> List[Tuple[Dict[str, Any], Dict[str, np.ndarray]]]:
    """Parse all <AB>...</AB> blocks in `text`. Returns list of (header, coeffs)."""
    blocks: List[Tuple[Dict[str, Any], Dict[str, np.ndarray]]] = []
    # split on </AB> so multiple knots in one file are handled
    for chunk in re.split(r'</AB\s*>', text, flags=re.IGNORECASE):
        hm = _AB_HEADER.search(chunk)
        if not hm:
            continue
        header: Dict[str, Any] = dict(_ATTR.findall(hm.group(1)))
        # normalize a couple of numeric header fields when present
        for k in ("L", "D"):
            if k in header:
                try:
                    header[k] = float(header[k])
                except ValueError:
                    pass
        rows = _COEFF.findall(chunk)
        if not rows:
            continue
        idx = [int(i) for (i, _a, _b) in rows]
        jmax = max(idx)
        size = jmax + 1  # index 0 reserved (DC, unused by <AB>)
        ax = np.zeros(size); ay = np.zeros(size); az = np.zeros(size)
        bx = np.zeros(size); by = np.zeros(size); bz = np.zeros(size)
        for (i_str, a_str, b_str) in rows:
            j = int(i_str)
            axj, ayj, azj = _triplet(a_str)
            bxj, byj, bzj = _triplet(b_str)
            ax[j], ay[j], az[j] = axj, ayj, azj
            bx[j], by[j], bz[j] = bxj, byj, bzj
        coeffs = {"a_x": ax, "b_x": bx, "a_y": ay, "b_y": by, "a_z": az, "b_z": bz}
        blocks.append((header, coeffs))
    return blocks


def parse_AB_multi(path: str) -> List[Tuple[Dict[str, Any], Dict[str, np.ndarray]]]:
    """Drop-in analogue of parse_fseries_multi for <AB> files."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return parse_AB_blocks(f.read())


def eval_AB(coeffs: Dict[str, np.ndarray], s: np.ndarray
            ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate r(s) = sum_j A_j cos(j s) + B_j sin(j s). Vectorized over s and j."""
    s = np.asarray(s, dtype=float)
    size = coeffs["a_x"].size
    j = np.arange(size)                      # 0..jmax (index 0 contributes cos0=1, sin0=0)
    phase = np.outer(s, j)                    # [S, J]
    cos = np.cos(phase); sin = np.sin(phase)
    x = cos @ coeffs["a_x"] + sin @ coeffs["b_x"]
    y = cos @ coeffs["a_y"] + sin @ coeffs["b_y"]
    z = cos @ coeffs["a_z"] + sin @ coeffs["b_z"]
    return x, y, z


# fseries-style alias so existing code can call it transparently
def eval_AB_block(coeffs: Dict[str, np.ndarray], s: np.ndarray):
    return eval_AB(coeffs, s)


def load_AB_curve(path: str, n_samples: int = 1000,
                  recenter: bool = False, normalize_scale: bool = False
                  ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Convenience: parse the largest <AB> block in `path` and return (x, y, z, header).

    recenter=True subtracts the curve centroid (makes any origin-referenced moment
    centering-invariant). normalize_scale=True rescales to unit RMS radius. Both are
    OFF by default so the raw Fremlin geometry is reproduced exactly.
    """
    blocks = parse_AB_multi(path)
    if not blocks:
        raise ValueError(f"no <AB> blocks in {path}")
    header, coeffs = max(blocks, key=lambda b: b[1]["a_x"].size)
    s = np.linspace(0.0, 2.0 * np.pi, n_samples, endpoint=False)
    x, y, z = eval_AB(coeffs, s)
    if recenter:
        x = x - x.mean(); y = y - y.mean(); z = z - z.mean()
    if normalize_scale:
        rms = float(np.sqrt(np.mean(x * x + y * y + z * z)))
        if rms > 0:
            x, y, z = x / rms, y / rms, z / rms
    return x, y, z, header


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "knot.3_1.AB"
    x, y, z, hdr = load_AB_curve(p, n_samples=2000)
    # closed-curve arclength as a sanity check (should be ~ L for unit D)
    P = np.stack([x, y, z], 1)
    seg = np.linalg.norm(np.roll(P, -1, 0) - P, axis=1)
    L = float(seg.sum())
    print(f"parsed {p}: Id={hdr.get('Id')} Conway={hdr.get('Conway')} "
          f"L_header={hdr.get('L')}")
    print(f"  samples={len(x)}  arclength={L:.4f}  "
          f"bbox=({x.max()-x.min():.3f},{y.max()-y.min():.3f},{z.max()-z.min():.3f})")
    print(f"  centroid=({x.mean():.4f},{y.mean():.4f},{z.mean():.4f})")
