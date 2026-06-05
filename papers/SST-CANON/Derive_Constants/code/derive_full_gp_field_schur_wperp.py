#!/usr/bin/env python3
"""
derive_full_gp_field_schur_wperp.py

Full-field GP/NLS relaxed-Hessian audit for the remaining gate w_perp=1.

This is the next step beyond the collective-coordinate script.  It computes
finite-difference Hessians for two strain channels, optionally relaxing the
full complex GP field on a 2D disk for each epsilon.

Gate:
    sigma = 3 + (2/3) w_perp
    c2 = sigma/(4 chi_R^2)
    c2 = 11/48 at chi_R=2 only if w_perp=1.

Channels:
    scalar:      A = exp(eps) I
    transverse:  A = diag(exp(eps), exp(-eps))

The field is initialized as a deformed n=1 vortex.  If --relax-field is set,
the real and imaginary parts of psi inside the disk are optimized by L-BFGS-B
with the boundary held fixed.  The Hessian is then a relaxed-field numerical
proxy for the Schur-complement Hessian.

Epistemic status:
    - If w_perp -> 1 under grid/refinement, the gate is supported.
    - If w_perp is not near 1, the unweighted shell normalization is not
      derived by this GP field model.
    - This remains a numerical finite-difference approximation, not an analytic
      theorem.

Usage:
    python derive_full_gp_field_schur_wperp.py --outdir outputs_full_gp_schur

Heavier:
    python derive_full_gp_field_schur_wperp.py --relax-field --grid-n 36 --maxiter 80 --outdir outputs_full_gp_schur_relaxed
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except Exception:
    minimize = None
    SCIPY_AVAILABLE = False


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def vortex_profile_pade(r: np.ndarray, n: int = 1) -> np.ndarray:
    return r**n / np.sqrt(r**(2*n) + 2.0)


def make_grid(N: int, L: float, Rmask: float, boundary_width: float):
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x, indexing="xy")
    R = np.sqrt(X*X + Y*Y)
    mask = R <= Rmask
    boundary = (R <= Rmask) & (R >= Rmask - boundary_width)
    interior = mask & (~boundary) & (R > 1.5*dx)
    core_fixed = mask & (R <= 1.5*dx)
    fixed = boundary | core_fixed
    return x, X, Y, R, mask, interior, fixed, dx


def affine_vortex(X, Y, eps: float, channel: str, n: int = 1) -> np.ndarray:
    if channel == "scalar":
        invx = math.exp(-eps)
        invy = math.exp(-eps)
    elif channel == "perp":
        invx = math.exp(-eps)
        invy = math.exp(eps)
    else:
        raise ValueError(channel)
    XA = invx * X
    YA = invy * Y
    RA = np.sqrt(XA*XA + YA*YA)
    TH = np.arctan2(YA, XA)
    amp = vortex_profile_pade(RA, n)
    psi = amp * np.exp(1j*n*TH)
    psi = np.where(RA < 1e-12, 0.0, psi)
    return psi


def gp_energy(psi: np.ndarray, mask: np.ndarray, dx: float) -> float:
    dpx = np.gradient(psi, dx, axis=1, edge_order=2)
    dpy = np.gradient(psi, dx, axis=0, edge_order=2)
    density = 0.5*(np.abs(dpx)**2 + np.abs(dpy)**2) + 0.25*(1.0 - np.abs(psi)**2)**2
    return float(np.sum(density[mask]) * dx*dx)


def pack(psi: np.ndarray, interior: np.ndarray) -> np.ndarray:
    vals = psi[interior]
    return np.concatenate([vals.real, vals.imag])


def unpack(vec: np.ndarray, psi_fixed: np.ndarray, interior: np.ndarray) -> np.ndarray:
    psi = psi_fixed.copy()
    n = int(vec.size // 2)
    vals = vec[:n] + 1j*vec[n:]
    psi[interior] = vals
    return psi


def relaxed_energy_for_eps(eps: float, channel: str, args, grid):
    x, X, Y, R, mask, interior, fixed, dx = grid
    psi0 = affine_vortex(X, Y, eps, channel, args.winding)
    psi0 = np.where(mask, psi0, 0.0)
    psi0[fixed & mask] = psi0[fixed & mask]
    E_init = gp_energy(psi0, mask, dx)

    if not args.relax_field or not SCIPY_AVAILABLE:
        return E_init, E_init, 0.0, 0, False, "frozen"

    x0 = pack(psi0, interior)
    psi_fixed = psi0.copy()

    def obj(v):
        psi = unpack(v, psi_fixed, interior)
        return gp_energy(psi, mask, dx)

    res = minimize(
        obj, x0, method="L-BFGS-B",
        options={"maxiter": args.maxiter, "ftol": args.ftol, "gtol": args.gtol, "maxls": 20},
    )
    psi_relaxed = unpack(res.x, psi_fixed, interior)
    E_final = gp_energy(psi_relaxed, mask, dx)
    step_norm = float(np.linalg.norm(res.x - x0) / max(np.linalg.norm(x0), 1e-30))
    return E_init, E_final, step_norm, int(res.nit), bool(res.success), str(res.message)


def channel_hessian(channel: str, args, grid):
    h = args.eps
    rows = []
    E = {}
    for label, eps in [("minus", -h), ("zero", 0.0), ("plus", +h)]:
        Ei, Ef, step, nit, success, message = relaxed_energy_for_eps(eps, channel, args, grid)
        E[label] = Ef
        rows.append({
            "channel": channel,
            "point": label,
            "epsilon": eps,
            "energy_initial": Ei,
            "energy_final": Ef,
            "relative_relax_step_norm": step,
            "iterations": nit,
            "success": success,
            "message": message,
        })
    H = (E["plus"] - 2*E["zero"] + E["minus"])/(h*h)
    slope = (E["plus"] - E["minus"])/(2*h)
    return H, slope, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid-n", type=int, default=34)
    parser.add_argument("--L-box", type=float, default=6.0)
    parser.add_argument("--R-mask", type=float, default=5.0)
    parser.add_argument("--boundary-width", type=float, default=0.7)
    parser.add_argument("--eps", type=float, default=0.0152703116982)
    parser.add_argument("--winding", type=int, default=1)
    parser.add_argument("--chi-R", type=float, default=2.0)
    parser.add_argument("--relax-field", action="store_true")
    parser.add_argument("--maxiter", type=int, default=40)
    parser.add_argument("--ftol", type=float, default=1e-10)
    parser.add_argument("--gtol", type=float, default=1e-6)
    parser.add_argument("--target-tol", type=float, default=0.05)
    parser.add_argument("--outdir", default="outputs_full_gp_schur_wperp")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    grid = make_grid(args.grid_n, args.L_box, args.R_mask, args.boundary_width)
    x, X, Y, R, mask, interior, fixed, dx = grid

    H_scalar, slope_scalar, rows_scalar = channel_hessian("scalar", args, grid)
    H_perp, slope_perp, rows_perp = channel_hessian("perp", args, grid)

    w = H_perp/H_scalar if abs(H_scalar) > 1e-30 else float("nan")
    sigma = 3.0 + (2.0/3.0)*w
    c2 = sigma/(4.0*args.chi_R*args.chi_R)
    target_c2 = 11.0/48.0
    pass_gate = abs(w - 1.0) <= args.target_tol

    write_csv(outdir/"full_gp_schur_energy_points.csv", rows_scalar + rows_perp)
    summary = [{
        "grid_n": args.grid_n,
        "L_box": args.L_box,
        "R_mask": args.R_mask,
        "boundary_width": args.boundary_width,
        "eps": args.eps,
        "relax_field": args.relax_field,
        "scipy_available": SCIPY_AVAILABLE,
        "interior_dof_complex": int(np.sum(interior)),
        "fixed_dof_complex": int(np.sum(fixed & mask)),
        "H_scalar": H_scalar,
        "H_perp": H_perp,
        "slope_scalar": slope_scalar,
        "slope_perp": slope_perp,
        "w_perp_full_field_proxy": w,
        "sigma": sigma,
        "c2_at_chiR": c2,
        "target_11_over_48": target_c2,
        "pass_wperp_near_1": pass_gate,
        "status": "PASS_FULL_FIELD_PROXY_WPERP_NEAR_1" if pass_gate else "OPEN_GATE_FULL_FIELD_PROXY_NOT_EQUAL_1",
    }]
    write_csv(outdir/"full_gp_schur_wperp_summary.csv", summary)

    report = f"""# Full-field GP Schur proxy for w_perp

Hessians:
\[
H_{{00}}={H_scalar:.12g},\qquad H_{{\perp\perp}}={H_perp:.12g}.
\]

Measured:
\[
w_\perp={w:.12g}.
\]

Then:
\[
\sigma=3+\frac23w_\perp={sigma:.12g},
\qquad
c_2={c2:.12g}.
\]

Target:
\[
w_\perp=1,\qquad c_2=11/48={target_c2:.12g}.
\]

Status: `{summary[0]['status']}`.

This is a finite-grid full-field relaxation proxy.  It closes the gate only if
\(w_\perp\to1\) under grid, radius, boundary, and relaxation convergence.
"""
    (outdir/"full_gp_schur_wperp_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Full-field GP Schur-complement target for \(w_\perp\)}
The primitive shell-normalization gate is \(w_\perp=1\).  A finite-grid
full-field GP audit estimates the relaxed Hessians
\[
  H_{00}^{\rm rel},\qquad H_{\perp\perp}^{\rm rel},
\]
by relaxing the complex GP field on a disk for scalar and transverse strain
channels.  The measured quantity is
\[
  w_\perp=\frac{H_{\perp\perp}^{\rm rel}}{H_{00}^{\rm rel}}.
\]
This closes the gate only if \(w_\perp\to1\) under convergence.  If the limit is
not \(1\), then \(11/48\) remains a shell-normalization closure rather than a
primitive GP result.
"""
    (outdir/"full_gp_schur_wperp_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    print("Full-field GP Schur proxy for w_perp")
    print("="*72)
    print(f"relax field     : {args.relax_field}")
    print(f"scipy available : {SCIPY_AVAILABLE}")
    print(f"complex dof     : {int(np.sum(interior))}")
    print(f"H_scalar        : {H_scalar:.12g}")
    print(f"H_perp          : {H_perp:.12g}")
    print(f"w_perp          : {w:.12g}")
    print(f"c2              : {c2:.12g}")
    print(f"status          : {summary[0]['status']}")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
