#!/usr/bin/env python3
"""Post-patch numerical checks for SST CANON v0.8.25 patch pack.

Run after applying patches 01-06. Confirms:
  1. corrected Rydberg form of F_swirl^max (16 pi^2 coefficient),
  2. rho_calc == rho_horn identity behind patch 02,
  3. M0 = (m_e/4) L_tot reduction behind patch 03,
  4. all canonical anchors unchanged.
"""
import numpy as np
from scipy import constants as C

c, hbar, h, me, e, eps0 = C.c, C.hbar, C.h, C.m_e, C.e, C.epsilon_0
alpha, G, Rinf = C.alpha, C.G, C.Rydberg

v = alpha * c / 2
omega_c = me * c**2 / hbar
rc = v / omega_c
F = me * c**2 / (2 * rc)

def check(name, a, b, tol=1e-6):
    rel = abs(a - b) / abs(b)
    status = "OK" if rel < tol else "FAIL"
    print(f"{name:58s} {a:.9e} vs {b:.9e}  rel={rel:.2e}  {status}")
    return rel < tol

ok = True
print("== Patch 01: corrected Rydberg form ==")
ok &= check("16 pi^2 hbar Rinf^2 c / alpha^5 == F", 16*np.pi**2*hbar*Rinf**2*c/alpha**5, F)
print(f"(rejected old form 32 pi^2 gives {32*np.pi**2*hbar*Rinf**2*c/alpha**5:.4f} N = 2F -> factor-2 error confirmed)")

print("\n== Patch 02: rho_calc retirement ==")
rhohorn = me*c**2/(2*np.pi*v**2*rc**3)
rho_calc_legacy = 4*F/(np.pi*alpha**2*c**2*rc**2)
ok &= check("rho_calc(legacy) == rho_horn^eff", rho_calc_legacy, rhohorn)
ok &= check("pi rc^2 rho_horn v^2 == F", np.pi*rc**2*rhohorn*v**2, F)

print("\n== Patch 03: M0 reduction ==")
lam_c = h/(me*c)
M0_per_L = 2*np.pi**3*rhohorn*rc**5/lam_c**2
ok &= check("M0/L_tot == m_e/4", M0_per_L, me/4, 1e-12)
L31 = 16.371637
print(f"M0(3_1) = {M0_per_L*L31/me:.6f} m_e  (expected 4.092909; NOT the electron mass)")

print("\n== Anchor invariance ==")
ok &= check("F_swirl^max", F, 29.053507, 1e-6)
ok &= check("v* canonical", v, 1.09384563e6, 1e-8)
ok &= check("r_c canonical", rc, 1.40897017e-15, 1e-7)
ok &= check("rho_horn canonical", rhohorn, 3.8934358266918687e18, 1e-6)
ok &= check("Rinf identity v^3/(pi rc c^3)", v**3/(np.pi*rc*c**3), Rinf, 1e-9)

print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
raise SystemExit(0 if ok else 1)
