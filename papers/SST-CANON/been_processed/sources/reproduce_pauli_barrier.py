#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reproduce_pauli_barrier.py
==========================
Claim 38 -- Hydrodynamic exchange / Pauli-barrier benchmark scale (~7.6 eV).

This mirrors the SSTcore v0.8.12 C++ kernel exactly:
    src/atomic_bridge_model.cpp : AtomicBridgeModel::pauli_barrier_scale(...)
        V_max = rho_f * Gamma0^2 / (4*pi) * (L / a_cut) * shape_factor

Epistemic status: [CALIBRATED BENCHMARK], NOT [DERIVED THEOREM].
  * The Biot-Savart overlap FORM is a derived consequence of the orthodox
    filament interaction energy.
  * The numeric SCALE (7.6 eV) is CALIBRATED: the UV cutoff is set to a_cut=r_c
    to land on the legacy atomic-window benchmark. a_cut is a regularization
    cutoff and must NOT be identified with the resolved tube radius a_core.
    shape_factor is an O(1) geometric constant (=1 here).

Run:  python3 reproduce_pauli_barrier.py
"""
import math

# --- CODATA-2018 / canonical inputs ---
HBAR  = 1.054571817e-34
M_E   = 9.1093837015e-31
C     = 2.99792458e8
ALPHA = 7.2973525693e-3
E     = 1.602176634e-19
RHO_F = 7.0e-7                     # the single free parameter

OMEGA_C = M_E*C*C/HBAR
VCHAR   = ALPHA*C/2.0
R_C     = VCHAR/OMEGA_C            # = alpha hbar/(2 m_e c) = r_e/2


def gamma0(r_c, v):
    return 2.0*math.pi*r_c*v


def bohr_radius_from_rc(r_c, alpha):
    # a_0 = lambda_bar_c/alpha and r_c = alpha*lambda_bar_c/2 => a_0 = 2 r_c/alpha^2
    return 2.0*r_c/(alpha*alpha)


def pauli_barrier_scale(rho_f, Gamma0, L, a_cut, shape_factor=1.0):
    """Exact mirror of AtomicBridgeModel::pauli_barrier_scale (SSTcore v0.8.12)."""
    if rho_f < 0.0 or Gamma0 <= 0.0 or L <= 0.0 or a_cut <= 0.0:
        raise ValueError("rho_f>=0; Gamma0,L,a_cut>0 required")
    return (rho_f*Gamma0*Gamma0/(4.0*math.pi))*(L/a_cut)*shape_factor


def main():
    G0    = gamma0(R_C, VCHAR)
    a0    = bohr_radius_from_rc(R_C, ALPHA)
    L     = 2.0*math.pi*a0            # L ~ 2 pi a_0 (hydrogenic loop length)
    a_cut = R_C                       # CALIBRATED cutoff choice (= r_c, NOT a_core)
    V     = pauli_barrier_scale(RHO_F, G0, L, a_cut, shape_factor=1.0)
    V_eV  = V/E

    print("Pauli-barrier benchmark  [CALIBRATED BENCHMARK] (not a derived theorem)")
    print("-"*64)
    print(f"  rho_f       = {RHO_F:.3e} kg/m^3   (free parameter)")
    print(f"  r_c         = {R_C:.8e} m")
    print(f"  v_swirl     = {VCHAR:.8e} m/s")
    print(f"  Gamma_0     = {G0:.8e} m^2/s")
    print(f"  a_0=2r_c/a^2= {a0:.8e} m   (Bohr radius)")
    print(f"  L=2*pi*a_0  = {L:.8e} m")
    print(f"  a_cut       = {a_cut:.8e} m   [CALIBRATED: = r_c, not a_core]")
    print(f"  shape_factor= 1.0   [O(1) geometric constant]")
    print("-"*64)
    print(f"  V_Pauli_max = {V:.8e} J = {V_eV:.5f} eV")
    print()
    ok = abs(V_eV - 7.69365) < 1e-3
    print(f"  benchmark check: 7.69 eV  -> {'PASS' if ok else 'FAIL'}")
    print()
    print("  [CRITICAL NOTE] The eV value is cutoff-calibrated to the atomic")
    print("  window; it shows the exchange scale is atomically relevant, it is")
    print("  NOT an independent prediction. A physical resolved-core result")
    print("  requires an independently specified a_core or profile model.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
