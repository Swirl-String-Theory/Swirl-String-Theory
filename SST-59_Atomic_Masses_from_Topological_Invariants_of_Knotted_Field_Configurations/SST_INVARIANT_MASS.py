"""
Sst mass kernel computation.

Incorporates concordance-motivated constraints and the double-twist sliceness benchmark:
J. Lee (2025) "Rational Concordance of Double Twist Knots", arXiv:2504.07636v1.

This file implements:
  M(T) = amplification * k^{-3/2} * phi^{-g} * n^{-1/phi} * (u*V/c^2)
with amplification = (4/alpha)^S (default S=1). All factors are dimensionless except u, V, c.

where g4 is the slice genus (concordance-invariant). For genus-one sectors, g4 is a sharp
benchmark: in the double-twist family K_{m,n}, g4 ∈ {0,1} with a closed sliceness criterion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import math


# ==========================================================
# Physical constants container (for dependency injection)
# ==========================================================
@dataclass
class PhysicalConstant:
    value: float
    unit: str = ""
    uncertainty: float = 0.0


def default_constants() -> Dict[str, PhysicalConstant]:
    """Canon-aligned constants for use with master_mass_invariant and solve_for_L_tot."""
    phi_val = (1 + math.sqrt(5)) / 2
    return {
        "alpha_fs": PhysicalConstant(7.2973525643e-3),
        "phi": PhysicalConstant(phi_val),
        "c": PhysicalConstant(299_792_458.0),
        "v_swirl": PhysicalConstant(1.093_845_63e6),
        "r_c": PhysicalConstant(1.408_970_17e-15),
        "rho_core": PhysicalConstant(3.8934358266918687e18),
    }


# ==========================================================
# Double-twist genus-one benchmark (Lee 2025, arXiv:2504.07636)
# ==========================================================
def is_slice_double_twist(m: int, n: int) -> bool:
    """
    Double-twist knot K_{m,n} sliceness criterion:
      K_{m,n} is slice  <=>  (m*n == 0) or (abs(m+n) == 1).
    Source: J. Lee (2025), arXiv:2504.07636v1, Proposition/Discussion around Fig.2.
    """
    return (m * n == 0) or (abs(m + n) == 1)


def g4_double_twist(m: int, n: int) -> int:
    """
    Slice genus benchmark for double-twist genus-one family.
    Returns:
      0 if slice, else 1 (genus-one non-slice member).
    """
    return 0 if is_slice_double_twist(m, n) else 1


@dataclass(frozen=True)
class KnotTopology:
    """
    Topological indices used by the SST mass kernel.

    k: kernel suppression index (real > 0)
    g4: slice genus (integer >= 0). Chosen for concordance robustness.
        If you want to track Seifert genus separately, store it in g_seifert (optional).
    n: number of components (integer >= 1)
    L_tot: dimensionless total ropelength-like factor (>=0)
    S: optional shielding exponent for (4/alpha)^S. Default S=1 preserves legacy behavior.
    """
    k: float
    g4: int
    n: int
    L_tot: float
    S: float = 1.0
    g_seifert: Optional[int] = None
    meta: Optional[dict] = None


def master_mass_invariant(topo: KnotTopology, constants: Dict[str, PhysicalConstant]) -> float:
    """
    M(T) = (4/alpha)^S * k^{-3/2} * phi^{-g4} * n^{-1/phi} * (u*V/c^2).
    """
    c = constants["c"].value
    r_c = constants["r_c"].value
    rho_core = constants["rho_core"].value
    v_swirl = constants["v_swirl"].value
    alpha_fs = constants["alpha_fs"].value
    phi_val = constants["phi"].value

    u = 0.5 * rho_core * (v_swirl ** 2)  # J/m^3
    V = math.pi * (r_c ** 3) * topo.L_tot  # m^3

    # Legacy kernel uses (4/alpha) with exponent 1. Keep as default.
    amplification = (4.0 / alpha_fs) ** float(topo.S)
    mass_kg = (
        amplification
        * (topo.k ** (-1.5))
        * (phi_val ** (-int(topo.g4)))
        * (topo.n ** (-1.0 / phi_val))
        * (u * V / (c ** 2))
    )
    return mass_kg


def solve_for_L_tot(target_mass_kg: float, topo_without_L: KnotTopology, constants: Dict[str, PhysicalConstant]) -> float:
    """Solve for L_tot so that master_mass_invariant(topo_with_L_tot, constants) == target_mass_kg."""
    c = constants["c"].value
    r_c = constants["r_c"].value
    rho_core = constants["rho_core"].value
    v_swirl = constants["v_swirl"].value
    alpha_fs = constants["alpha_fs"].value
    phi_val = constants["phi"].value

    u = 0.5 * rho_core * (v_swirl ** 2)
    amplification = (4.0 / alpha_fs) ** float(topo_without_L.S)

    # target_mass = amplification * k^{-3/2} * phi^{-g4} * n^{-1/phi} * (u*pi*r_c^3*L / c^2)
    denom = (
        amplification
        * (topo_without_L.k ** (-1.5))
        * (phi_val ** (-int(topo_without_L.g4)))
        * (topo_without_L.n ** (-1.0 / phi_val))
        * (u * math.pi * (r_c ** 3) / (c ** 2))
    )
    if denom <= 0:
        raise ValueError("Denominator non-positive; check parameters.")
    return target_mass_kg / denom


def get_particle_topologies() -> Dict[str, KnotTopology]:
    """
    Provides default topologies. L_tot values are expected to be calibrated by solve_for_L_tot
    or set from ropelength tables.
    """
    # Placeholder L_tot=1; typically calibrated on electron or set from knot ropelength data.
    # k choices follow your current convention (spectral / complexity proxy).
    # NOTE: g4 is slice genus. For trefoil-like genus-one candidates, g4=1.
    # Shielding exponent S defaults to 1 (legacy). Set S=0 only if you explicitly enable shielding.
    electron = KnotTopology(k=3.0, g4=1, n=1, L_tot=1.0, S=1.0, g_seifert=1)
    muon     = KnotTopology(k=5.0, g4=1, n=1, L_tot=1.0, S=1.0, g_seifert=1)
    proton   = KnotTopology(k=3.0, g4=2, n=3, L_tot=1.0, S=1.0, g_seifert=2)

    return {"e": electron, "mu": muon, "p": proton}


def make_double_twist_topology(m: int, n: int, *, k: float, components: int = 1, L_tot: float = 1.0, S: float = 1.0) -> KnotTopology:
    """
    Convenience constructor for genus-one double-twist K_{m,n}.
    Sets g4 using the closed sliceness benchmark (Lee 2025).
    k is left explicit (you may choose crossing-proxy, spectral index, etc.).
    """
    return KnotTopology(k=float(k), g4=g4_double_twist(m, n), n=int(components), L_tot=float(L_tot), S=float(S), g_seifert=1, meta={"family": "K_mn", "m": m, "n_twist": n})
