# Numerical checks for SST Addendum O (attosecond chiral photoionization)
# Omar's preferred validation using explicit constants and tabulated outputs.

import math
import pandas as pd
from ace_tools_open import display_dataframe_to_user

# ---- Constants (SI) ----
c = 299_792_458.0  # m/s (speed of light)
vswirl = 1_093_845.63  # m/s (user's canonical swirl speed C_e)
me = 9.109_383_7015e-31  # kg (electron mass, CODATA 2018/2022 same to our precision)
eV = 1.602_176_634e-19  # J

# ---- Reference timing from the paper ----
T_rabbit = 1.33e-15  # s (period of the 2ω modulation mentioned in the paper; used for phase comparisons)

# Observed delay magnitudes (seconds)
delays_as = [60.0, 240.0]  # attoseconds
delays_s = [d * 1e-18 for d in delays_as]

# Representative electron kinetic energies at sidebands (from ~2 to 12 eV window in figures)
energies_eV = [2, 4, 6, 8, 10, 12]

# ---- Helper functions ----
def electron_speed(E_eV: float) -> float:
    """Nonrelativistic electron speed sqrt(2E/m)."""
    E = E_eV * eV
    v = math.sqrt(2 * E / me)
    return v

def path_difference(v: float, dt: float) -> float:
    """Δℓ = v * Δt"""
    return v * dt

def dilation_shift_per_period(v: float, T: float) -> float:
    """Δt_dil = T * (1 - sqrt(1 - (v/c)^2))"""
    beta2 = (v / c) ** 2
    return T * (1.0 - math.sqrt(1.0 - beta2))

def beta_required_for_delay(delta_t: float, T: float) -> float:
    """Solve 1 - sqrt(1 - β^2) = Δt/T  => β = sqrt(1 - (1 - Δ)^2)"""
    Δ = delta_t / T
    val = 1.0 - (1.0 - Δ) ** 2
    return 0.0 if val < 0 else math.sqrt(val)

# ---- Table 1: Path differences for observed delays at representative energies ----
rows = []
for E in energies_eV:
    v = electron_speed(E)
    for d_as, d_s in zip(delays_as, delays_s):
        dL = path_difference(v, d_s)  # meters
        rows.append({
            "E (eV)": E,
            "v_e (m/s)": v,
            "Delay (as)": d_as,
            "Δℓ (nm)": dL * 1e9,
            "Δℓ (Å)": dL * 1e10,
            "Phase frac Δτ/T (unitless)": d_s / T_rabbit,
            "Phase shift (deg)": 360.0 * d_s / T_rabbit,
        })

df_paths = pd.DataFrame(rows)

# ---- Table 2: Swirl-time dilation magnitude per 1.33 fs at user's vswirl ----
Δt_swirl = dilation_shift_per_period(vswirl, T_rabbit)  # seconds
beta_req_60as = beta_required_for_delay(60e-18, T_rabbit)
beta_req_240as = beta_required_for_delay(240e-18, T_rabbit)

df_dilation = pd.DataFrame([{
    "vswirl (m/s)": vswirl,
    "β_s (vswirl/c)": vswirl / c,
    "Δt_dil per 1.33 fs (as)": Δt_swirl * 1e18,
    "β required for 60 as": beta_req_60as,
    "v required for 60 as (m/s)": beta_req_60as * c,
    "β required for 240 as": beta_req_240as,
    "v required for 240 as (m/s)": beta_req_240as * c,
}] )

display_dataframe_to_user("SST_attosecond_paths", df_paths)
display_dataframe_to_user("SST_swirl_dilation_check", df_dilation)

df_paths.head(), df_dilation
