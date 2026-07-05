#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_helicity_AB.py
==================
Run the sst_helicity Biot-Savart / vorticity / a_mu pipeline on David Fremlin
<AB>...</AB> ideal-knot files (via ab_knot.py), instead of .fseries files.

EPISTEMIC STATUS of a_mu = 0.5 * (Hc/Hm - 1):  [CALIBRATED / SPECULATIVE].
  * Hc = sum v.omega (a discrete helicity-like cross term) and
    Hm = sum |omega|^2 r^2 (an origin-referenced second moment) are well-defined
    field functionals, but the map (Hc/Hm - 1)/2 -> muon anomaly a_mu is a
    numerical template, NOT a derived identity. Treat outputs as a chirality /
    helicity diagnostic, not a prediction of the physical a_mu.
  * The amphichiral reference value -0.5 is a calibration target, not a theorem.

Usage:
  python3 run_helicity_AB.py knot.3_1.AB
  python3 run_helicity_AB.py "knots/*.AB" --grids 24,32 --recenter --exclude-core
"""
from __future__ import annotations
import argparse
import glob
import os
import numpy as np

import ab_knot
import sst_helicity as H


def nearest_curve_distance(grid_points: np.ndarray, curve: np.ndarray) -> np.ndarray:
    """Min distance from each grid point to the polyline vertices (coarse proxy)."""
    # chunk to bound memory: grid [G,3], curve [N,3]
    out = np.full(len(grid_points), np.inf)
    N = len(curve)
    step = max(1, 2_000_000 // max(1, len(grid_points)))
    for k in range(0, N, step):
        seg = curve[k:k + step]                       # [n,3]
        d = np.linalg.norm(grid_points[:, None, :] - seg[None, :, :], axis=2)
        out = np.minimum(out, d.min(axis=1))
    return out


def a_mu_for_curve(x, y, z, grid_size, spacing, interior,
                   recenter=False, exclude_core=False, core_factor=1.5):
    if recenter:
        x = x - x.mean(); y = y - y.mean(); z = z - z.mean()
    gp, gs, r2, inner = H.helicity_at(grid_size, spacing, interior)
    vel = H.compute_biot_savart_velocity(x, y, z, gp)
    vort = H.compute_vorticity_full_grid(vel, gs, spacing)
    v_sub = H.extract_interior_field(vel, gs, inner)
    w_sub = H.extract_interior_field(vort, gs, inner)
    r2_use = r2.copy()
    n_excluded = 0
    if exclude_core:
        # tame the self-field singularity: zero-weight interior cells within
        # core_factor*spacing of the curve (these dominate v.omega spuriously).
        curve = np.stack([x, y, z], axis=1)
        # interior grid points only:
        gp3 = gp.reshape(*gs, 3)[inner, :, :][:, inner, :][:, :, inner].reshape(-1, 3)
        dmin = nearest_curve_distance(gp3, curve)
        keep = dmin > core_factor * spacing
        n_excluded = int(np.count_nonzero(~keep))
        v_sub = v_sub[keep]; w_sub = w_sub[keep]; r2_use = r2_use[keep]
    Hc = float(np.einsum("ij,ij->", v_sub, w_sub))
    Hm = float(np.sum(np.linalg.norm(w_sub, axis=1) ** 2 * r2_use))
    a_mu = 0.5 * (Hc / Hm - 1.0) if Hm != 0.0 else float("nan")
    return a_mu, Hc, Hm, n_excluded


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", help="path or glob to <AB> file(s)")
    ap.add_argument("--grids", default="24,32",
                    help="comma list of grid sizes (default 24,32)")
    ap.add_argument("--spacing", type=float, default=0.1)
    ap.add_argument("--samples", type=int, default=1000)
    ap.add_argument("--recenter", action="store_true",
                    help="subtract curve centroid (centering-invariant r^2 moment)")
    ap.add_argument("--exclude-core", action="store_true",
                    help="zero-weight grid cells within 1.5*spacing of the curve "
                         "(tames the Biot-Savart self-field singularity)")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.pattern)) or ([args.pattern] if os.path.exists(args.pattern) else [])
    if not paths:
        print(f"no files match {args.pattern!r}"); return 1

    grids = [int(g) for g in args.grids.split(",")]
    print(f"SSTcore backend available: {H.HAVE_SST}  (False -> pure-Python fallback)")
    print("a_mu = 0.5*(Hc/Hm - 1)   [CALIBRATED/SPECULATIVE helicity diagnostic]\n")

    for path in paths:
        x, y, z, hdr = ab_knot.load_AB_curve(path, n_samples=args.samples)
        interior_frac = 0.25
        print(f"=== {os.path.basename(path)}  Id={hdr.get('Id')} "
              f"Conway={hdr.get('Conway')} L={hdr.get('L')} ===")
        for G in grids:
            I = max(2, int(round(G * interior_frac)))
            a_mu, Hc, Hm, nex = a_mu_for_curve(
                x, y, z, G, args.spacing, I,
                recenter=args.recenter, exclude_core=args.exclude_core)
            extra = f"  excluded_core_cells={nex}" if args.exclude_core else ""
            print(f"  grid={G:>3} interior={I:<3} a_mu={a_mu:+.6f}  "
                  f"[Hc={Hc:.3e}, Hm={Hm:.3e}]{extra}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
