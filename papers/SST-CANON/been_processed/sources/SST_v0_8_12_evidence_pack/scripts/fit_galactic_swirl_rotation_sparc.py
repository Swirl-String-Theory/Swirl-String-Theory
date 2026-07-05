#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fit_galactic_swirl_rotation_sparc.py
====================================
Claim 42 -- Dark-sector / galactic rotation as an SST swirl-pressure flat-tail.

STATUS: [RESEARCH-TRACK / PHENOMENOLOGICAL FIT].  The canonical Euler pressure
balance (1/rho_f) dp/dr = v_theta^2/r yields flat rotation curves (Canon Sec 6.4
/ research-track Stage-3 Branch-A). This script provides the missing fit
machinery. It does NOT derive the galactic coherence length r_s from first
principles -- the AU-scale coherence-length lemma (H_eff) remains OPEN; r_s is a
fit parameter here.

Model:
    V_model(r)^2 = V_bar(r)^2 + V_swirl(r)^2
    V_bar^2      = Vgas|Vgas| + Y_disk*Vdisk|Vdisk| + Y_bul*Vbul|Vbul|   (signed sq.)
    V_swirl(r)   = C_tail * (1 - exp(-r/r_s))     (saturating flat-tail, Branch-A)

Fit (numpy-only, no scipy): for each trial r_s, V_model^2 is LINEAR in
(Y_disk, Y_bul, C_tail^2); weighted least squares solves them, then chi^2 is
recomputed in V-space. The global best over the r_s grid is reported.

Inputs:
    --sparc PATH   a SPARC '*_rotmod.dat' file with columns
                   Rad[kpc] Vobs Vobs_err Vgas Vdisk Vbul [SBdisk SBbul]
    (no --sparc)   a built-in synthetic demo galaxy is fitted instead.

Outputs (under --out, default ./outputs_galactic_swirl):
    <name>_rotmod_fit.csv     per-radius Vbar,Vswirl,Vmodel,residuals
    <name>_fit_summary.csv    fitted params, chi2, dof, chi2_red, rms
    <name>_rotation_curve.png (if matplotlib present)

Run:  python3 fit_galactic_swirl_rotation_sparc.py
      python3 fit_galactic_swirl_rotation_sparc.py --sparc NGC2403_rotmod.dat
"""
import os
import sys
import argparse
import numpy as np


# ---------------------------------------------------------------------------
# SPARC loader  (Lelli, McGaugh & Schombert 2016 rotmod format)
# ---------------------------------------------------------------------------
def load_sparc_rotmod(path):
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            try:
                vals = [float(x) for x in parts[:6]]
            except ValueError:
                continue
            if len(vals) >= 6:
                rows.append(vals[:6])
    if not rows:
        raise ValueError(f"no numeric rows parsed from {path}")
    a = np.array(rows)
    name = os.path.splitext(os.path.basename(path))[0].replace("_rotmod", "")
    return dict(name=name, r=a[:,0], Vobs=a[:,1], errV=np.maximum(a[:,2], 1.0),
                Vgas=a[:,3], Vdisk=a[:,4], Vbul=a[:,5])


def synthetic_demo_galaxy(seed=0):
    """A realistic disc galaxy: baryons + swirl flat-tail + noise (truth known)."""
    rng = np.random.default_rng(seed)
    r = np.linspace(0.5, 18.0, 24)                       # kpc
    Vdisk = 120.0*np.sqrt(r)/np.sqrt(r+2.0)              # rising disc
    Vgas  = 30.0*r/(r+6.0)
    Vbul  = 80.0*np.exp(-r/1.5)
    Yd_true, Yb_true = 0.5, 0.7
    Vbar2 = Vgas*np.abs(Vgas) + Yd_true*Vdisk*np.abs(Vdisk) + Yb_true*Vbul*np.abs(Vbul)
    Ctail_true, rs_true = 110.0, 3.0
    Vsw = Ctail_true*(1-np.exp(-r/rs_true))
    Vtrue = np.sqrt(np.maximum(Vbar2, 0) + Vsw**2)
    errV = np.full_like(r, 5.0)
    Vobs = Vtrue + rng.normal(0, errV)
    return dict(name="DEMO_synthetic", r=r, Vobs=Vobs, errV=errV,
                Vgas=Vgas, Vdisk=Vdisk, Vbul=Vbul,
                truth=dict(Y_disk=Yd_true, Y_bul=Yb_true, C_tail=Ctail_true, r_s=rs_true))


# ---------------------------------------------------------------------------
# Fit
# ---------------------------------------------------------------------------
def fit(gal, rs_grid=None):
    r, Vobs, errV = gal["r"], gal["Vobs"], gal["errV"]
    Vgas, Vdisk, Vbul = gal["Vgas"], gal["Vdisk"], gal["Vbul"]
    signed = lambda V: V*np.abs(V)
    y  = signed(Vobs) - signed(Vgas)                     # target in V^2 space
    # weights: var(V^2) ~ (2 V errV)^2
    w  = 1.0/np.maximum((2.0*np.abs(Vobs)*errV)**2, 1e-12)
    if rs_grid is None:
        rs_grid = np.linspace(0.3, max(r)*1.5, 200)

    best = None
    for rs in rs_grid:
        g = (1.0-np.exp(-r/rs))**2
        X = np.column_stack([signed(Vdisk), signed(Vbul), g])  # cols: Yd, Yb, C_tail^2
        Wsqrt = np.sqrt(w)
        coef, *_ = np.linalg.lstsq(X*Wsqrt[:,None], y*Wsqrt, rcond=None)
        coef = np.clip(coef, 0.0, None)                  # non-negative physical params
        Vmodel2 = signed(Vgas) + X@coef
        Vmodel  = np.sqrt(np.maximum(Vmodel2, 0.0))
        chi2 = float(np.sum(((Vobs-Vmodel)/errV)**2))
        if best is None or chi2 < best["chi2"]:
            best = dict(chi2=chi2, rs=float(rs), Yd=float(coef[0]),
                        Yb=float(coef[1]), Ctail=float(np.sqrt(coef[2])),
                        Vmodel=Vmodel)
    dof = max(len(r)-4, 1)
    best["dof"] = dof
    best["chi2_red"] = best["chi2"]/dof
    Vbar = np.sqrt(np.maximum(signed(Vgas)+best["Yd"]*signed(Vdisk)+best["Yb"]*signed(Vbul), 0))
    Vsw  = best["Ctail"]*(1-np.exp(-r/best["rs"]))
    resid = Vobs-best["Vmodel"]
    best["Vbar"], best["Vswirl"], best["resid"] = Vbar, Vsw, resid
    best["rms"] = float(np.sqrt(np.mean(resid**2)))
    return best


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sparc", help="path to SPARC *_rotmod.dat (else synthetic demo)")
    ap.add_argument("--out", default="outputs_galactic_swirl")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()

    gal = load_sparc_rotmod(args.sparc) if args.sparc else synthetic_demo_galaxy()
    os.makedirs(args.out, exist_ok=True)
    res = fit(gal)
    r = gal["r"]

    print(f"Galactic swirl-rotation fit  [RESEARCH-TRACK]   galaxy={gal['name']}")
    print("-"*64)
    print(f"  Y_disk = {res['Yd']:.3f}   Y_bul = {res['Yb']:.3f}")
    print(f"  C_tail = {res['Ctail']:.2f} km/s   r_s = {res['rs']:.2f} kpc  [r_s OPEN: not derived]")
    print(f"  chi^2 = {res['chi2']:.2f}   dof = {res['dof']}   chi2/dof = {res['chi2_red']:.3f}")
    print(f"  RMS residual = {res['rms']:.2f} km/s")
    if "truth" in gal:
        t = gal["truth"]
        print(f"  (demo truth: Y_disk={t['Y_disk']}, Y_bul={t['Y_bul']}, "
              f"C_tail={t['C_tail']}, r_s={t['r_s']})")

    # per-radius CSV
    f1 = os.path.join(args.out, f"{gal['name']}_rotmod_fit.csv")
    with open(f1, "w") as f:
        f.write("Rad_kpc,Vobs,errV,Vbar,Vswirl,Vmodel,resid,resid_over_err\n")
        for i in range(len(r)):
            f.write(f"{r[i]:.4f},{gal['Vobs'][i]:.4f},{gal['errV'][i]:.4f},"
                    f"{res['Vbar'][i]:.4f},{res['Vswirl'][i]:.4f},{res['Vmodel'][i]:.4f},"
                    f"{res['resid'][i]:.4f},{res['resid'][i]/gal['errV'][i]:.4f}\n")
    # summary CSV
    f2 = os.path.join(args.out, f"{gal['name']}_fit_summary.csv")
    with open(f2, "w") as f:
        f.write("galaxy,Y_disk,Y_bul,C_tail_kms,r_s_kpc,chi2,dof,chi2_red,rms_kms\n")
        f.write(f"{gal['name']},{res['Yd']:.4f},{res['Yb']:.4f},{res['Ctail']:.4f},"
                f"{res['rs']:.4f},{res['chi2']:.4f},{res['dof']},{res['chi2_red']:.4f},{res['rms']:.4f}\n")
    print(f"  wrote {f1}\n  wrote {f2}")

    if not args.no_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            plt.figure(figsize=(7,5))
            plt.errorbar(r, gal["Vobs"], yerr=gal["errV"], fmt="o", ms=4,
                         color="k", label="Vobs", zorder=5)
            plt.plot(r, res["Vbar"], "--", color="tab:brown", label="V_bar (baryons)")
            plt.plot(r, res["Vswirl"], ":", color="tab:blue", label="V_swirl (SST flat-tail)")
            plt.plot(r, res["Vmodel"], "-", color="tab:red", lw=2, label="V_model")
            plt.xlabel("radius [kpc]"); plt.ylabel("v [km/s]")
            plt.title(f"{gal['name']}  (chi2/dof={res['chi2_red']:.2f})  [research-track]")
            plt.legend(); plt.tight_layout()
            f3 = os.path.join(args.out, f"{gal['name']}_rotation_curve.png")
            plt.savefig(f3, dpi=130); print(f"  wrote {f3}")
        except Exception as ex:
            print(f"  [plot skipped: {ex}]")

    print("-"*64)
    print("  [RESEARCH-TRACK] phenomenological 2-component fit. r_s is fitted,")
    print("  NOT derived; the swirl coherence-length lemma is OPEN. Keep this")
    print("  sector research-track until r_s has a first-principles derivation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
