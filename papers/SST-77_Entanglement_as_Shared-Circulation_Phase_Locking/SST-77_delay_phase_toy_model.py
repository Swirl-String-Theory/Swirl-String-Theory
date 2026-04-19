#!/usr/bin/env python3
"""
sst77_delay_phase_toy_model.py

Numerical illustration for the reduced SST toy model:
    dphi_A/dt = omega0 + kappa_AB * sin(phi_B(t-tau) - phi_A(t))
    dphi_B/dt = omega0 + kappa_AB * sin(phi_A(t-tau) - phi_B(t))

Outputs:
  1) time series of Delta(t) = phi_A(t) - phi_B(t)
  2) reduced correlation C(theta_A, theta_B) versus angle difference
  3) locking/stability sweep versus kappa_AB * tau
  4) correlation degradation versus effective leakage rate Gamma_topo_eff

This is a reduced classical toy-model integrator, not a Bell/CHSH solver.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, List

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class ModelParams:
    omega0: float         # carrier frequency [s^-1]
    kappa_ab: float       # coupling rate [s^-1]
    tau: float            # delay [s]
    t_final: float        # final integration time [s]
    dt: float             # timestep [s]
    phiA_hist: float      # constant history for phi_A on [-tau, 0]
    phiB_hist: float      # constant history for phi_B on [-tau, 0]
    transient_fraction: float = 0.5  # discard first fraction when computing correlations


def validate_params(p: ModelParams) -> None:
    if p.dt <= 0:
        raise ValueError("dt must be positive.")
    if p.tau < 0:
        raise ValueError("tau must be nonnegative.")
    if p.t_final <= 0:
        raise ValueError("t_final must be positive.")
    if not (0.0 <= p.transient_fraction < 1.0):
        raise ValueError("transient_fraction must lie in [0, 1).")
    if p.tau > 0 and p.dt > p.tau / 2:
        print(
            "Warning: dt is relatively large compared with tau. "
            "A smaller dt may improve stability/accuracy."
        )


def integrate_delay_system(
        p: ModelParams,
        gamma_topo_eff: float = 0.0,
        rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Integrate the delayed phase model using a simple explicit Euler scheme.
    The delay is handled by indexing into the past trajectory.

    Optional effective leakage/decoherence:
        gamma_topo_eff >= 0
    is implemented as independent phase diffusion for phi_A and phi_B:
        dphi -> dphi + sqrt(2 * gamma_topo_eff * dt) * N(0,1)
    This is a reduced surrogate for finite phase memory, not a first-principles SST derivation.
    """
    validate_params(p)

    if gamma_topo_eff < 0:
        raise ValueError("gamma_topo_eff must be nonnegative.")

    if rng is None:
        rng = np.random.default_rng(12345)

    n_steps = int(round(p.t_final / p.dt))
    if n_steps < 2:
        raise ValueError("Need at least two time steps.")

    times = np.linspace(0.0, n_steps * p.dt, n_steps + 1)

    phiA = np.empty(n_steps + 1, dtype=float)
    phiB = np.empty(n_steps + 1, dtype=float)

    phiA[0] = p.phiA_hist
    phiB[0] = p.phiB_hist

    delay_steps = int(round(p.tau / p.dt)) if p.tau > 0 else 0
    noise_scale = math.sqrt(2.0 * gamma_topo_eff * p.dt) if gamma_topo_eff > 0 else 0.0

    for i in range(n_steps):
        if delay_steps == 0:
            phiA_delayed = phiA[i]
            phiB_delayed = phiB[i]
        else:
            j = i - delay_steps
            if j >= 0:
                phiA_delayed = phiA[j]
                phiB_delayed = phiB[j]
            else:
                # Constant history on [-tau, 0]
                phiA_delayed = p.phiA_hist
                phiB_delayed = p.phiB_hist

        dphiA = p.omega0 + p.kappa_ab * math.sin(phiB_delayed - phiA[i])
        dphiB = p.omega0 + p.kappa_ab * math.sin(phiA_delayed - phiB[i])

        if gamma_topo_eff > 0:
            dphiA += noise_scale * rng.normal() / p.dt
            dphiB += noise_scale * rng.normal() / p.dt

        phiA[i + 1] = phiA[i] + p.dt * dphiA
        phiB[i + 1] = phiB[i] + p.dt * dphiB

    return times, phiA, phiB


def wrap_to_pi(x: np.ndarray) -> np.ndarray:
    """Wrap angles to (-pi, pi]."""
    return (x + np.pi) % (2.0 * np.pi) - np.pi


def binary_observable(phi: np.ndarray, theta: float) -> np.ndarray:
    """
    A(theta,t) = sign(cos(phi(t)-theta)).
    Use +1 at exact zeros for determinism.
    """
    vals = np.cos(phi - theta)
    return np.where(vals >= 0.0, 1.0, -1.0)


def compute_correlation_curve(
        phiA: np.ndarray,
        phiB: np.ndarray,
        transient_fraction: float = 0.5,
        n_angles: int = 181,
        thetaA_fixed: float = 0.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute C(theta_A, theta_B) as a function of delta_theta = theta_B - theta_A.
    """
    n = len(phiA)
    start = int(transient_fraction * n)
    phiA_ss = phiA[start:]
    phiB_ss = phiB[start:]

    delta_thetas = np.linspace(-np.pi, np.pi, n_angles)
    correlations = np.empty_like(delta_thetas)

    A = binary_observable(phiA_ss, thetaA_fixed)

    for k, dtheta in enumerate(delta_thetas):
        thetaB = thetaA_fixed + dtheta
        B = binary_observable(phiB_ss, thetaB)
        correlations[k] = np.mean(A * B)

    return delta_thetas, correlations


def branch_metrics(delta_ss: np.ndarray) -> Dict[str, float]:
    """
    Return branch diagnostics for steady-state wrapped phase difference.
    """
    dist0 = np.mean(np.abs(wrap_to_pi(delta_ss - 0.0)))
    distpi = np.mean(np.abs(wrap_to_pi(delta_ss - np.pi)))
    distm_pi = np.mean(np.abs(wrap_to_pi(delta_ss + np.pi)))

    branches = {"0": dist0, "pi": distpi, "-pi": distm_pi}
    nearest = min(branches, key=branches.get)

    return {
        "mean": float(np.mean(delta_ss)),
        "std": float(np.std(delta_ss)),
        "dist0": float(dist0),
        "distpi": float(distpi),
        "distm_pi": float(distm_pi),
        "nearest_branch": nearest,
        "nearest_distance": float(branches[nearest]),
    }


def correlation_amplitude(corr: np.ndarray) -> float:
    """
    Simple amplitude/contrast measure for C(theta_A, theta_B).
    """
    return 0.5 * (float(np.max(corr)) - float(np.min(corr)))


def print_summary(p: ModelParams, times: np.ndarray, phiA: np.ndarray, phiB: np.ndarray) -> None:
    delta = wrap_to_pi(phiA - phiB)
    start = int(p.transient_fraction * len(times))
    delta_ss = delta[start:]
    metrics = branch_metrics(delta_ss)

    print("\n=== Reduced SST toy-model summary ===")
    print(f"omega0       = {p.omega0:.6e} s^-1")
    print(f"kappa_AB     = {p.kappa_ab:.6e} s^-1")
    print(f"tau          = {p.tau:.6e} s")
    print(f"dt           = {p.dt:.6e} s")
    print(f"t_final      = {p.t_final:.6e} s")
    print(f"kappa_AB*tau = {p.kappa_ab * p.tau:.6e}")
    print(f"delay steps  = {int(round(p.tau / p.dt)) if p.tau > 0 else 0}")

    print("\nSteady-state diagnostics (wrapped to (-pi, pi]):")
    print(f"mean Delta_ss     = {metrics['mean']: .6f} rad")
    print(f"std  Delta_ss     = {metrics['std']: .6f} rad")
    print(f"closest branch    = {metrics['nearest_branch']}")
    print(f"branch distance   = {metrics['nearest_distance']:.6f} rad")


def export_csv_xy(filename: str, x_name: str, y_name: str, x: np.ndarray, y: np.ndarray) -> None:
    """
    Export two-column CSV.
    """
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([x_name, y_name])
        for xi, yi in zip(x, y):
            writer.writerow([float(xi), float(yi)])


def export_fig1_timeseries_csv(filename: str, times: np.ndarray, delta: np.ndarray) -> None:
    export_csv_xy(filename, "t", "delta", times, delta)


def export_fig2_correlation_csv(filename: str, delta_thetas: np.ndarray, correlations: np.ndarray) -> None:
    export_csv_xy(filename, "dtheta", "C", delta_thetas, correlations)


def export_fig3_series_csv(sample_series: List[Tuple[float, np.ndarray, np.ndarray]]) -> None:
    """
    Export one CSV per representative time series:
        fig3_locking_series_1.csv, ...
    with columns: t, delta, kappa_tau
    """
    for idx, (kappa_tau, times_s, delta_s) in enumerate(sample_series, start=1):
        filename = f"fig3_locking_series_{idx}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["t", "delta", "kappa_tau"])
            for t_i, d_i in zip(times_s, delta_s):
                writer.writerow([float(t_i), float(d_i), float(kappa_tau)])


def export_fig3_metrics_csv(
        filename: str,
        kappa_tau: np.ndarray,
        means: np.ndarray,
        stds: np.ndarray,
        dist0: np.ndarray,
) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ktau", "mean_delta", "std_delta", "dist0"])
        for kt, m, s, d0 in zip(kappa_tau, means, stds, dist0):
            writer.writerow([float(kt), float(m), float(s), float(d0)])


def export_fig4_leakage_csv(
        filename: str,
        gamma_values: np.ndarray,
        amplitudes: np.ndarray,
        c0_vals: np.ndarray,
) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["gamma", "amp", "c00"])
        for g, a, c0 in zip(gamma_values, amplitudes, c0_vals):
            writer.writerow([float(g), float(a), float(c0)])


def run_locking_sweep(
        base_params: ModelParams,
        kappa_values: np.ndarray,
) -> Dict[str, np.ndarray]:
    """
    Sweep over kappa_AB while holding tau fixed.
    Return steady-state metrics and selected time-series samples.
    """
    means = np.empty_like(kappa_values, dtype=float)
    stds = np.empty_like(kappa_values, dtype=float)
    dists0 = np.empty_like(kappa_values, dtype=float)

    # Store a few representative time series for plotting
    chosen_indices = np.linspace(0, len(kappa_values) - 1, num=min(5, len(kappa_values)), dtype=int)
    sample_series: List[Tuple[float, np.ndarray, np.ndarray]] = []

    for idx, kappa in enumerate(kappa_values):
        p = ModelParams(
            omega0=base_params.omega0,
            kappa_ab=float(kappa),
            tau=base_params.tau,
            t_final=base_params.t_final,
            dt=base_params.dt,
            phiA_hist=base_params.phiA_hist,
            phiB_hist=base_params.phiB_hist,
            transient_fraction=base_params.transient_fraction,
        )
        times, phiA, phiB = integrate_delay_system(p)
        delta = wrap_to_pi(phiA - phiB)
        start = int(p.transient_fraction * len(times))
        delta_ss = delta[start:]
        metrics = branch_metrics(delta_ss)

        means[idx] = metrics["mean"]
        stds[idx] = metrics["std"]
        dists0[idx] = metrics["dist0"]

        if idx in chosen_indices:
            sample_series.append((float(kappa * p.tau), times.copy(), delta.copy()))

    return {
        "kappa_values": kappa_values,
        "kappa_tau": kappa_values * base_params.tau,
        "means": means,
        "stds": stds,
        "dist0": dists0,
        "sample_series": sample_series,
    }


def run_leakage_sweep(
        base_params: ModelParams,
        gamma_values: np.ndarray,
        rng_seed: int = 12345,
) -> Dict[str, np.ndarray]:
    """
    Sweep over effective leakage/decoherence rate gamma_topo_eff.
    Measure the correlation amplitude.
    """
    amps = np.empty_like(gamma_values, dtype=float)
    c0_vals = np.empty_like(gamma_values, dtype=float)

    for idx, gamma in enumerate(gamma_values):
        rng = np.random.default_rng(rng_seed + idx)
        times, phiA, phiB = integrate_delay_system(
            base_params,
            gamma_topo_eff=float(gamma),
            rng=rng,
        )
        _, corr = compute_correlation_curve(
            phiA=phiA,
            phiB=phiB,
            transient_fraction=base_params.transient_fraction,
            n_angles=181,
            thetaA_fixed=0.0,
        )
        amps[idx] = correlation_amplitude(corr)
        c0_vals[idx] = corr[len(corr) // 2]  # approximately theta_B - theta_A = 0

    return {
        "gamma_values": gamma_values,
        "amplitudes": amps,
        "c0": c0_vals,
    }


def plot_results(
        times: np.ndarray,
        phiA: np.ndarray,
        phiB: np.ndarray,
        delta_thetas: np.ndarray,
        correlations: np.ndarray,
        transient_fraction: float,
        locking_sweep: Dict[str, np.ndarray],
        leakage_sweep: Dict[str, np.ndarray],
) -> None:
    delta = wrap_to_pi(phiA - phiB)
    t_trans = times[int(transient_fraction * len(times))]

    # Export CSV data for pgfplots/TikZ
    export_fig1_timeseries_csv(
        "fig1_delta_timeseries.csv",
        times,
        delta,
    )
    export_fig2_correlation_csv(
        "fig2_correlation_curve.csv",
        delta_thetas,
        correlations,
    )
    export_fig3_series_csv(locking_sweep["sample_series"])
    export_fig3_metrics_csv(
        "fig3_locking_metrics.csv",
        locking_sweep["kappa_tau"], locking_sweep["means"], locking_sweep["stds"], locking_sweep["dist0"]
    )
    export_fig4_leakage_csv("fig4_leakage_curve.csv", leakage_sweep["gamma_values"], leakage_sweep["amplitudes"], leakage_sweep["c0"])

    # Figure 1: Delta(t)
    fig1 = plt.figure(figsize=(8, 4.5))
    ax1 = fig1.add_subplot(111)
    ax1.plot(times, delta, linewidth=1.2)
    ax1.axvline(t_trans, linestyle="--", linewidth=1.0)
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel(r"$\Delta(t)=\phi_A(t)-\phi_B(t)$ [rad, wrapped]")
    ax1.set_title("Delayed phase toy model: phase-difference time series")
    ax1.grid(True)

    # Figure 2: C(theta_A, theta_B)
    fig2 = plt.figure(figsize=(8, 4.5))
    ax2 = fig2.add_subplot(111)
    ax2.plot(delta_thetas, correlations, linewidth=1.5)
    ax2.set_xlabel(r"$\theta_B-\theta_A$ [rad]")
    ax2.set_ylabel(r"$C(\theta_A,\theta_B)$")
    ax2.set_title("Reduced binary correlation versus analyzer-angle difference")
    ax2.grid(True)

    # Figure 3: locking/stability sweep
    fig3 = plt.figure(figsize=(10, 4.8))
    ax3a = fig3.add_subplot(121)
    for kappa_tau, times_s, delta_s in locking_sweep["sample_series"]:
        ax3a.plot(times_s, delta_s, linewidth=1.1, label=fr"$\kappa_{{AB}}\tau={kappa_tau:.2f}$")
    ax3a.set_xlabel("t [s]")
    ax3a.set_ylabel(r"$\Delta(t)$ [rad, wrapped]")
    ax3a.set_title("Representative time series across a locking sweep")
    ax3a.grid(True)
    ax3a.legend(fontsize=8)

    ax3b = fig3.add_subplot(122)
    ax3b.plot(locking_sweep["kappa_tau"], locking_sweep["stds"], linewidth=1.5, label=r"$\mathrm{std}(\Delta)_{\rm ss}$")
    ax3b.plot(locking_sweep["kappa_tau"], locking_sweep["dist0"], linewidth=1.5, label=r"$\langle|\Delta| \rangle_{\rm ss}$ to branch $0$")
    ax3b.set_xlabel(r"$\kappa_{AB}\tau$")
    ax3b.set_ylabel("steady-state metric")
    ax3b.set_title("Locking diagnostics versus control parameter")
    ax3b.grid(True)
    ax3b.legend(fontsize=8)

    # Figure 4: coherence/leakage sweep
    fig4 = plt.figure(figsize=(8, 4.5))
    ax4 = fig4.add_subplot(111)
    ax4.plot(leakage_sweep["gamma_values"], leakage_sweep["amplitudes"], linewidth=1.5, label="correlation amplitude")
    ax4.plot(leakage_sweep["gamma_values"], leakage_sweep["c0"], linewidth=1.5, label=r"$C(0,0)$")
    ax4.set_xlabel(r"effective leakage rate $\Gamma_{\mathrm{topo}}^{\mathrm{eff}}$ [s$^{-1}$]")
    ax4.set_ylabel("correlation metric")
    ax4.set_title("Correlation degradation versus effective leakage")
    ax4.grid(True)
    ax4.legend(fontsize=8)

    plt.tight_layout()

    # Save figures
    fig1.savefig("SST-77_delay_phase_toy_model_1.png", dpi=300, bbox_inches="tight")
    fig2.savefig("SST-77_delay_phase_toy_model_2.png", dpi=300, bbox_inches="tight")
    fig3.savefig("SST-77_delay_phase_toy_model_3.png", dpi=300, bbox_inches="tight")
    fig4.savefig("SST-77_delay_phase_toy_model_4.png", dpi=300, bbox_inches="tight")

    plt.show()


def main() -> None:
    # Baseline representative reduced-model parameters.
    # These are demonstration values, not SST predictions.
    params = ModelParams(
        omega0=20.0,          # s^-1
        kappa_ab=8.0,         # s^-1
        tau=0.35,             # s
        t_final=40.0,         # s
        dt=0.001,             # s
        phiA_hist=0.15,       # rad
        phiB_hist=2.10,       # rad
        transient_fraction=0.5,
    )

    # Baseline run
    times, phiA, phiB = integrate_delay_system(params)
    print_summary(params, times, phiA, phiB)

    delta_thetas, correlations = compute_correlation_curve(
        phiA=phiA,
        phiB=phiB,
        transient_fraction=params.transient_fraction,
        n_angles=181,
        thetaA_fixed=0.0,
    )

    # Figure 3: locking sweep
    kappa_values = np.array([1.0, 2.0, 4.0, 8.0, 12.0, 16.0, 24.0], dtype=float)
    locking_sweep = run_locking_sweep(params, kappa_values)

    # Figure 4: effective leakage/coherence sweep
    gamma_values = np.array([0.0, 0.02, 0.05, 0.10, 0.20, 0.40, 0.80], dtype=float)
    leakage_sweep = run_leakage_sweep(params, gamma_values, rng_seed=12345)

    plot_results(
        times=times,
        phiA=phiA,
        phiB=phiB,
        delta_thetas=delta_thetas,
        correlations=correlations,
        transient_fraction=params.transient_fraction,
        locking_sweep=locking_sweep,
        leakage_sweep=leakage_sweep,
    )

    print("\nExported CSV files:")
    print("  fig1_delta_timeseries.csv")
    print("  fig2_correlation_curve.csv")
    print("  fig3_locking_series_1.csv ... fig3_locking_series_5.csv")
    print("  fig3_locking_metrics.csv")
    print("  fig4_leakage_curve.csv")


if __name__ == "__main__":
    main()