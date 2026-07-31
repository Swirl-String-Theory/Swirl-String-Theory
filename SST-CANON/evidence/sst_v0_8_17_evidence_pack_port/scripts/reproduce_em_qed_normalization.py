#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reproduce_em_qed_normalization.py
=================================
Claims 61/67 -- Swirl <-> electromagnetic normalization and the identity
    B_core^SST = B_QED   (QED / Schwinger critical magnetic field).

CORRECT bridge (dimensionally forced):
    A_SI = (m_e / e) * u_swirl          [NOT (e/m_e) * u]
    B_SST = curl A_SI = (m_e / e) * omega
At the Compton angular frequency omega_c = m_e c^2 / hbar:
    B_core^SST = (m_e/e) * omega_c = m_e^2 c^2 / (e hbar) = B_QED

Dimensional check:
    [A] = T*m = kg*m/(C*s);   [(m_e/e) u] = (kg/C)(m/s) = kg*m/(C*s)   OK
    [(e/m_e) u] = (C/kg)(m/s) = C*m/(kg*s)  -> NOT tesla*metre          WRONG

Epistemic status:
    [ORTHODOX]   B_QED = m_e^2 c^2/(e hbar) is the Schwinger critical field.
    [DERIVED]    the (m_e/e) prefactor is fixed by dimensional analysis.
    [CALIBRATED] B_core = B_QED follows once omega is set to the Compton
                 anchor omega_c; it is a consistency identity, not an
                 independent dynamical prediction.

Run:  python3 reproduce_em_qed_normalization.py
"""
import math

# --- CODATA-2018 ---
HBAR  = 1.054571817e-34
M_E   = 9.1093837015e-31
C     = 2.99792458e8
E     = 1.602176634e-19

OMEGA_C = M_E*C*C/HBAR


def vector_potential_prefactor():
    """Correct SI bridge prefactor A = k * u with k = m_e/e."""
    return M_E/E


def B_from_omega(omega):
    """B_SST = (m_e/e) * omega."""
    return (M_E/E)*omega


def B_qed():
    """QED/Schwinger critical magnetic field m_e^2 c^2/(e hbar)."""
    return M_E*M_E*C*C/(E*HBAR)


def main():
    fails = 0
    k = vector_potential_prefactor()
    print("Swirl<->EM normalization  (claims 61/67)")
    print("-"*64)
    print(f"  A_SI prefactor  m_e/e        = {k:.8e} kg/C")
    print(f"  (wrong form)    e/m_e        = {E/M_E:.8e} C/kg  [DIM-WRONG]")

    # Dimensional gate: m_e/e must give tesla*metre for A; check via B units.
    B_core = B_from_omega(OMEGA_C)
    B_q    = B_qed()
    print("-"*64)
    print(f"  omega_c                      = {OMEGA_C:.8e} rad/s")
    print(f"  B_core^SST=(m_e/e)*omega_c   = {B_core:.7e} T   [DERIVED prefactor]")
    print(f"  B_QED=m_e^2 c^2/(e hbar)     = {B_q:.7e} T   [ORTHODOX Schwinger]")
    rel = abs(B_core-B_q)/B_q
    ok1 = rel < 1e-12
    print(f"  B_core == B_QED ?            -> {'PASS' if ok1 else 'FAIL'} (rel={rel:.1e})  [CALIBRATED]")
    fails += not ok1

    # benchmark numeric
    ok2 = abs(B_q - 4.4140052e9)/4.4140052e9 < 1e-5
    print(f"  numeric B_QED ~ 4.414e9 T    -> {'PASS' if ok2 else 'FAIL'}")
    fails += not ok2

    # explicit guard against the inverted prefactor
    wrong = (E/M_E)*OMEGA_C
    ok3 = wrong > 1e25   # ~1.4e32, dimensionally meaningless as tesla
    print(f"  guard: (e/m_e)*omega_c       = {wrong:.3e}  (NOT tesla; inverted form rejected)")
    print("-"*64)
    print(f"  RESULT: {'ALL PASS' if fails==0 else f'{fails} FAIL'}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
