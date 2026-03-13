import math
import os
import csv
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# SST-60 numerical validation of branch selection
#
# Outputs:
#   1) branch table CSV
#   2) raw and residual .dat files for TikZ/pgfplots
#   3) three-panel figure  (Option A)
#   4) log-residual figure (Option B)
#   5) pgfplots snippet files
#
# DDE:
#   phi'(t) = Omega0 + K sin(phi(t-tau) - phi(t))
#
# Locked branches satisfy:
#   Omega = Omega0 - K sin(Omega tau)
#
# Linear classification:
#   A = K cos(Omega tau)
#   stable branch: A > 0
#   sufficiently unstable branch: A*tau < -1
# ============================================================

OUTPUT_DIR = "sst60_numerics_output"


# ============================================================
# Utilities
# ============================================================

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def self_consistency(Omega: float, Omega0: float, K: float, tau: float) -> float:
    return Omega - Omega0 + K * math.sin(Omega * tau)


def branch_parameter_A(Omega: float, K: float, tau: float) -> float:
    return K * math.cos(Omega * tau)


def find_branches(
        Omega0: float,
        K: float,
        tau: float,
        omega_min: float,
        omega_max: float,
        num_scan: int = 40000,
        tol: float = 1e-12,
        max_iter: int = 100
):
    """
    Find roots of:
        Omega = Omega0 - K sin(Omega tau)
    via sign-change scan + bisection.
    """
    xs = np.linspace(omega_min, omega_max, num_scan)
    fs = np.array([self_consistency(x, Omega0, K, tau) for x in xs])

    roots = []

    def bisect(a, b):
        fa = self_consistency(a, Omega0, K, tau)
        fb = self_consistency(b, Omega0, K, tau)

        if fa == 0:
            return a
        if fb == 0:
            return b
        if fa * fb > 0:
            return None

        for _ in range(max_iter):
            c = 0.5 * (a + b)
            fc = self_consistency(c, Omega0, K, tau)
            if abs(fc) < tol or abs(b - a) < tol:
                return c
            if fa * fc <= 0:
                b = c
                fb = fc
            else:
                a = c
                fa = fc
        return 0.5 * (a + b)

    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]
        fa, fb = fs[i], fs[i + 1]
        if fa == 0.0:
            roots.append(a)
        elif fa * fb < 0:
            r = bisect(a, b)
            if r is not None:
                roots.append(r)

    roots_sorted = sorted(roots)
    unique_roots = []
    for r in roots_sorted:
        if not unique_roots or abs(r - unique_roots[-1]) > 1e-6:
            unique_roots.append(r)

    return unique_roots


def classify_branches(branches, K, tau):
    out = []
    for Omega in branches:
        A = branch_parameter_A(Omega, K, tau)
        out.append({
            "Omega": Omega,
            "theta": Omega * tau,
            "A": A,
            "A_tau": A * tau,
            "stable_linear": (A > 0),
            "unstable_sufficient": (A * tau < -1.0),
        })
    return out


def choose_demo_branches(branch_data):
    stable = [d for d in branch_data if d["stable_linear"]]
    unstable = [d for d in branch_data if d["unstable_sufficient"]]

    if not stable:
        raise RuntimeError("No stable branch with A > 0 found.")
    if not unstable:
        raise RuntimeError("No sufficiently unstable branch with A*tau < -1 found.")

    stable_pick = stable[len(stable) // 2]
    unstable_pick = unstable[len(unstable) // 2]
    return stable_pick, unstable_pick


def print_branch_table(branch_data):
    print("\n=== BRANCH TABLE ===")
    print(
        f"{'idx':>3}  {'Omega':>12}  {'theta=Omega*tau':>16}  "
        f"{'A':>12}  {'A*tau':>12}  {'A>0?':>6}  {'A*tau<-1?':>10}"
    )
    for i, d in enumerate(branch_data):
        print(
            f"{i:3d}  {d['Omega']:12.8f}  {d['theta']:16.8f}  "
            f"{d['A']:12.8f}  {d['A_tau']:12.8f}  "
            f"{str(d['stable_linear']):>6}  {str(d['unstable_sufficient']):>10}"
        )


def save_branch_table_csv(branch_data, filename="branch_table.csv"):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["idx", "Omega", "theta", "A", "A_tau", "stable_linear", "unstable_sufficient"])
        for i, d in enumerate(branch_data):
            writer.writerow([
                i,
                d["Omega"],
                d["theta"],
                d["A"],
                d["A_tau"],
                d["stable_linear"],
                d["unstable_sufficient"],
            ])
    return path


# ============================================================
# DDE solver
# ============================================================

def interp_history(t_query, t_hist, phi_hist):
    if t_query <= t_hist[0]:
        return phi_hist[0]
    if t_query >= t_hist[-1]:
        return phi_hist[-1]

    idx = np.searchsorted(t_hist, t_query) - 1
    idx = max(0, min(idx, len(t_hist) - 2))
    t0, t1 = t_hist[idx], t_hist[idx + 1]
    y0, y1 = phi_hist[idx], phi_hist[idx + 1]

    if t1 == t0:
        return y0
    w = (t_query - t0) / (t1 - t0)
    return (1.0 - w) * y0 + w * y1


def make_history_function(Omega_star, phi0, eps=1e-3, mode="cos"):
    def history(t):
        base = Omega_star * t + phi0
        if mode == "cos":
            return base + eps * math.cos(2.0 * math.pi * t)
        if mode == "sin":
            return base + eps * math.sin(2.0 * math.pi * t)
        return base
    return history


def solve_dde_euler(
        Omega0: float,
        K: float,
        tau: float,
        t_final: float,
        dt: float,
        history_func,
):
    """
    Simple method-of-steps + explicit Euler.
    Adequate for qualitative validation.
    """
    n_hist = int(round(tau / dt))
    tau_eff = n_hist * dt

    t_values = np.arange(-tau_eff, t_final + dt, dt)
    phi_values = np.zeros_like(t_values)
    omega_inst = np.zeros_like(t_values)

    hist_mask = t_values <= 0.0
    for i, t in enumerate(t_values[hist_mask]):
        phi_values[i] = history_func(float(t))

    start_idx = np.where(t_values > 0.0)[0][0]

    for i in range(1, start_idx):
        omega_inst[i] = (phi_values[i] - phi_values[i - 1]) / dt
    omega_inst[0] = omega_inst[1] if start_idx > 1 else 0.0

    for i in range(start_idx, len(t_values)):
        t = t_values[i - 1]
        phi_now = phi_values[i - 1]
        delayed_t = t - tau_eff

        phi_delay = interp_history(delayed_t, t_values[:i], phi_values[:i])
        dphi = Omega0 + K * math.sin(phi_delay - phi_now)

        phi_values[i] = phi_now + dt * dphi
        omega_inst[i] = dphi

    return t_values, phi_values, omega_inst, tau_eff


def summarize_run(label, Omega_star, A, A_tau, t_values, omega_inst, fit_tail_fraction=0.2):
    n = len(t_values)
    start = int((1.0 - fit_tail_fraction) * n)
    omega_tail = omega_inst[start:]
    omega_mean = float(np.mean(omega_tail))
    omega_std = float(np.std(omega_tail))
    drift = omega_mean - Omega_star

    print(f"\n=== SUMMARY: {label} ===")
    print(f"Target/reference branch Omega_* = {Omega_star:.10f}")
    print(f"A = {A:.10f}")
    print(f"A*tau = {A_tau:.10f}")
    print(f"Tail mean omega_inst = {omega_mean:.10f}")
    print(f"Tail std  omega_inst = {omega_std:.10e}")
    print(f"Tail mean - Omega_*  = {drift:.10e}")


# ============================================================
# Export helpers
# ============================================================

def downsample_series(t_values, y_values, stride=100):
    return t_values[::stride], y_values[::stride]


def save_dat_file(filename, columns, headers):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(" ".join(headers) + "\n")
        for row in zip(*columns):
            f.write(" ".join(f"{x:.10f}" for x in row) + "\n")
    return path


def print_compact_preview(label, t_values, y_values, max_rows=16):
    print(f"\n=== PREVIEW: {label} ===")
    print("% t value")
    n = len(t_values)

    if n <= max_rows:
        for t, y in zip(t_values, y_values):
            print(f"{t:.8f} {y:.10f}")
        return

    head = max_rows // 2
    tail = max_rows - head

    for t, y in zip(t_values[:head], y_values[:head]):
        print(f"{t:.8f} {y:.10f}")

    print("...")

    for t, y in zip(t_values[-tail:], y_values[-tail:]):
        print(f"{t:.8f} {y:.10f}")


def write_pgfplots_snippet_optionA(
        filename,
        raw_dat,
        stable_resid_dat,
        unstable_resid_dat
):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r"""\begin{tikzpicture}
\begin{groupplot}[
    group style={group size=1 by 3, vertical sep=1.2cm},
    width=0.9\linewidth,
    height=0.26\linewidth,
    grid=major,
    grid style={opacity=0.25},
    tick label style={font=\small},
    label style={font=\small},
    legend style={font=\scriptsize}
]

\nextgroupplot[
    ylabel={$\omega_{\mathrm{inst}}(t)$},
    title={SST-60 numerical validation of branch selection}
]
\addplot table [x=t, y=omega_stable, col sep=space] {""" + raw_dat + r"""};
\addlegendentry{stable-init trajectory}
\addplot table [x=t, y=omega_unstable, col sep=space] {""" + raw_dat + r"""};
\addlegendentry{unstable-init trajectory}
\addplot[dashed] table [x=t, y=Omega_stable_ref, col sep=space] {""" + raw_dat + r"""};
\addlegendentry{stable locked branch}
\addplot[dashed] table [x=t, y=Omega_unstable_ref, col sep=space] {""" + raw_dat + r"""};
\addlegendentry{unstable reference branch}

\nextgroupplot[
    ylabel={$\Delta\omega_{\mathrm{stable}}(t)$}
]
\addplot table [x=t, y=dw_stable, col sep=space] {""" + stable_resid_dat + r"""};
\addlegendentry{stable residual}
\addplot[dashed] coordinates {(0,0) (200,0)};

\nextgroupplot[
    xlabel={$t$},
    ylabel={$\Delta\omega_{\mathrm{unstable}}(t)$}
]
\addplot table [x=t, y=dw_unstable, col sep=space] {""" + unstable_resid_dat + r"""};
\addlegendentry{unstable residual}
\addplot[dashed] coordinates {(0,0) (200,0)};

\end{groupplot}
\end{tikzpicture}
""")
    return path


def write_pgfplots_snippet_optionB(filename, log_dat):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r"""\begin{tikzpicture}
\begin{axis}[
    width=0.9\linewidth,
    height=0.42\linewidth,
    xlabel={$t$},
    ylabel={$|\Delta\omega(t)|$},
    ymode=log,
    grid=major,
    grid style={opacity=0.25},
    tick label style={font=\small},
    label style={font=\small},
    legend style={font=\scriptsize, at={(0.98,0.98)}, anchor=north east},
    title={Log-scale residual frequency magnitude}
]
\addplot table [x=t, y=abs_dw_stable, col sep=space] {""" + log_dat + r"""};
\addlegendentry{stable: $|\omega_{\mathrm{inst}}-\Omega_{\ast,\mathrm{stable}}|$}

\addplot table [x=t, y=abs_dw_unstable, col sep=space] {""" + log_dat + r"""};
\addlegendentry{unstable: $|\omega_{\mathrm{inst}}-\Omega_{\ast,\mathrm{unstable}}|$}
\end{axis}
\end{tikzpicture}
""")
    return path


# ============================================================
# Plot builders
# ============================================================

def make_optionA_threepanel_figure(
        t_stable, w_stable, Omega_stable,
        t_unstable, w_unstable, Omega_unstable,
        fig_filename="sst60_optionA_threepanel.png"
):
    dw_stable = w_stable - Omega_stable
    dw_unstable = w_unstable - Omega_unstable

    fig, (ax1, ax2, ax3) = plt.subplots(
        3, 1, figsize=(10, 9), sharex=True,
        gridspec_kw={"height_ratios": [2.0, 1.2, 1.2]}
    )

    # Panel 1: raw trajectories
    ax1.plot(t_stable, w_stable, label="stable-init trajectory")
    ax1.plot(t_unstable, w_unstable, label="unstable-init trajectory")

    ax1.axhline(
        Omega_stable, linestyle="--", linewidth=1.0,
        label=fr"stable locked branch $\Omega_\ast={Omega_stable:.4f}$"
    )
    ax1.axhline(
        Omega_unstable, linestyle="--", linewidth=1.0,
        label=fr"unstable reference branch $\Omega_\ast={Omega_unstable:.4f}$"
    )

    ax1.set_ylabel(r"$\omega_{\mathrm{inst}}(t)$")
    ax1.set_title("SST-60 numerical validation of branch selection")
    ax1.legend()

    # Panel 2: stable residual
    ax2.plot(t_stable, dw_stable, label=r"stable: $\omega_{\mathrm{inst}}-\Omega_{\ast,\mathrm{stable}}$")
    ax2.axhline(0.0, linestyle="--", linewidth=1.0)
    ax2.set_ylabel(r"$\Delta\omega_{\mathrm{stable}}(t)$")
    ax2.legend()

    stable_margin = max(1e-6, 1.1 * np.max(np.abs(dw_stable)))
    ax2.set_ylim(-stable_margin, stable_margin)

    # Panel 3: unstable residual
    ax3.plot(t_unstable, dw_unstable, label=r"unstable: $\omega_{\mathrm{inst}}-\Omega_{\ast,\mathrm{unstable}}$")
    ax3.axhline(0.0, linestyle="--", linewidth=1.0)
    ax3.set_xlabel("t")
    ax3.set_ylabel(r"$\Delta\omega_{\mathrm{unstable}}(t)$")
    ax3.legend()

    unstable_margin = max(1e-6, 1.1 * np.max(np.abs(dw_unstable)))
    ax3.set_ylim(-0.02 * unstable_margin, unstable_margin)

    plt.tight_layout()

    fig_path = os.path.join(OUTPUT_DIR, fig_filename)
    plt.savefig(fig_path, dpi=220)
    print(f"\nSaved Option A figure to: {fig_path}")
    plt.show()

    return dw_stable, dw_unstable, fig_path


def make_optionB_log_figure(
        t_stable, w_stable, Omega_stable,
        t_unstable, w_unstable, Omega_unstable,
        fig_filename="sst60_optionB_log_residuals.png"
):
    dw_stable = np.abs(w_stable - Omega_stable)
    dw_unstable = np.abs(w_unstable - Omega_unstable)

    eps = 1e-12

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        t_stable, dw_stable + eps,
        label=r"stable: $|\omega_{\mathrm{inst}}-\Omega_{\ast,\mathrm{stable}}|$"
    )
    ax.plot(
        t_unstable, dw_unstable + eps,
        label=r"unstable: $|\omega_{\mathrm{inst}}-\Omega_{\ast,\mathrm{unstable}}|$"
    )

    ax.set_yscale("log")
    ax.set_xlabel("t")
    ax.set_ylabel(r"$|\Delta\omega(t)|$")
    ax.set_title("Log-scale residual frequency magnitude")
    ax.legend()
    plt.tight_layout()

    fig_path = os.path.join(OUTPUT_DIR, fig_filename)
    plt.savefig(fig_path, dpi=220)
    print(f"Saved Option B figure to: {fig_path}")
    plt.show()

    return dw_stable, dw_unstable, fig_path


# ============================================================
# Main
# ============================================================

def main():
    ensure_output_dir()

    # --------------------------------------------------------
    # Parameters
    # --------------------------------------------------------
    tau = 20.0
    K = 0.4
    Omega0 = 1.0
    beta = K * tau

    print("=== PARAMETERS ===")
    print(f"Omega0 = {Omega0}")
    print(f"K      = {K}")
    print(f"tau    = {tau}")
    print(f"beta   = K*tau = {beta}")

    # --------------------------------------------------------
    # Find and classify branches
    # --------------------------------------------------------
    branches = find_branches(
        Omega0=Omega0,
        K=K,
        tau=tau,
        omega_min=0.1,
        omega_max=2.0,
        num_scan=40000
    )

    branch_data = classify_branches(branches, K, tau)
    print_branch_table(branch_data)

    branch_csv = save_branch_table_csv(branch_data)
    print(f"\nSaved branch table to: {branch_csv}")

    stable_branch, unstable_branch = choose_demo_branches(branch_data)

    print("\n=== CHOSEN BRANCHES ===")
    print(
        f"Stable branch:   Omega = {stable_branch['Omega']:.10f}, "
        f"A = {stable_branch['A']:.10f}, A*tau = {stable_branch['A_tau']:.10f}"
    )
    print(
        f"Unstable branch: Omega = {unstable_branch['Omega']:.10f}, "
        f"A = {unstable_branch['A']:.10f}, A*tau = {unstable_branch['A_tau']:.10f}"
    )

    # --------------------------------------------------------
    # Simulate DDE
    # --------------------------------------------------------
    dt = 0.002
    t_final = 200.0
    eps_hist = 1e-2

    hist_stable = make_history_function(
        Omega_star=stable_branch["Omega"], phi0=0.0, eps=eps_hist, mode="cos"
    )
    hist_unstable = make_history_function(
        Omega_star=unstable_branch["Omega"], phi0=0.0, eps=eps_hist, mode="cos"
    )

    t_s, phi_s, omega_s, tau_eff = solve_dde_euler(
        Omega0=Omega0, K=K, tau=tau, t_final=t_final, dt=dt, history_func=hist_stable
    )
    t_u, phi_u, omega_u, _ = solve_dde_euler(
        Omega0=Omega0, K=K, tau=tau, t_final=t_final, dt=dt, history_func=hist_unstable
    )

    print("\n=== EFFECTIVE GRID-ALIGNED DELAY USED IN SIMULATION ===")
    print(f"tau_eff = {tau_eff:.10f}")

    mask_s = t_s >= 0.0
    mask_u = t_u >= 0.0

    t_stable = t_s[mask_s]
    w_stable = omega_s[mask_s]
    Omega_stable = stable_branch["Omega"]

    t_unstable = t_u[mask_u]
    w_unstable = omega_u[mask_u]
    Omega_unstable = unstable_branch["Omega"]

    summarize_run(
        "stable-init",
        Omega_stable,
        stable_branch["A"],
        stable_branch["A_tau"],
        t_stable,
        w_stable
    )
    summarize_run(
        "unstable-init",
        Omega_unstable,
        unstable_branch["A"],
        unstable_branch["A_tau"],
        t_unstable,
        w_unstable
    )

    # --------------------------------------------------------
    # Make figures
    # --------------------------------------------------------
    dw_stable, dw_unstable, optionA_fig = make_optionA_threepanel_figure(
        t_stable, w_stable, Omega_stable,
        t_unstable, w_unstable, Omega_unstable
    )

    abs_dw_stable, abs_dw_unstable, optionB_fig = make_optionB_log_figure(
        t_stable, w_stable, Omega_stable,
        t_unstable, w_unstable, Omega_unstable
    )

    # --------------------------------------------------------
    # Downsample and export .dat files
    # --------------------------------------------------------
    export_stride = 100

    t_stable_ds, w_stable_ds = downsample_series(t_stable, w_stable, stride=export_stride)
    _, dw_stable_ds = downsample_series(t_stable, dw_stable, stride=export_stride)
    _, abs_dw_stable_ds = downsample_series(t_stable, abs_dw_stable, stride=export_stride)

    t_unstable_ds, w_unstable_ds = downsample_series(t_unstable, w_unstable, stride=export_stride)
    _, dw_unstable_ds = downsample_series(t_unstable, dw_unstable, stride=export_stride)
    _, abs_dw_unstable_ds = downsample_series(t_unstable, abs_dw_unstable, stride=export_stride)

    # Raw data for Option A top panel
    raw_dat = save_dat_file(
        "optionA_raw.dat",
        columns=[
            t_stable_ds,
            w_stable_ds,
            w_unstable_ds,
            np.full_like(t_stable_ds, Omega_stable),
            np.full_like(t_stable_ds, Omega_unstable),
        ],
        headers=[
            "t",
            "omega_stable",
            "omega_unstable",
            "Omega_stable_ref",
            "Omega_unstable_ref",
        ],
    )

    # Stable residual
    stable_resid_dat = save_dat_file(
        "optionA_stable_residual.dat",
        columns=[t_stable_ds, dw_stable_ds],
        headers=["t", "dw_stable"],
    )

    # Unstable residual
    unstable_resid_dat = save_dat_file(
        "optionA_unstable_residual.dat",
        columns=[t_unstable_ds, dw_unstable_ds],
        headers=["t", "dw_unstable"],
    )

    # Log-scale data
    log_dat = save_dat_file(
        "optionB_log_residuals.dat",
        columns=[t_stable_ds, abs_dw_stable_ds, abs_dw_unstable_ds],
        headers=["t", "abs_dw_stable", "abs_dw_unstable"],
    )

    print(f"\nSaved raw data file:              {raw_dat}")
    print(f"Saved stable residual data file:  {stable_resid_dat}")
    print(f"Saved unstable residual data file:{unstable_resid_dat}")
    print(f"Saved log residual data file:     {log_dat}")

    # Compact previews only
    print_compact_preview("Option A stable residual", t_stable_ds, dw_stable_ds)
    print_compact_preview("Option A unstable residual", t_unstable_ds, dw_unstable_ds)
    print_compact_preview("Option B |stable residual|", t_stable_ds, abs_dw_stable_ds)
    print_compact_preview("Option B |unstable residual|", t_unstable_ds, abs_dw_unstable_ds)

    # --------------------------------------------------------
    # Write pgfplots snippets
    # --------------------------------------------------------
    pgf_optionA = write_pgfplots_snippet_optionA(
        filename="sst60_optionA_threepanel_pgfplots.tex",
        raw_dat="optionA_raw.dat",
        stable_resid_dat="optionA_stable_residual.dat",
        unstable_resid_dat="optionA_unstable_residual.dat",
    )

    pgf_optionB = write_pgfplots_snippet_optionB(
        filename="sst60_optionB_log_pgfplots.tex",
        log_dat="optionB_log_residuals.dat",
    )

    print(f"\nSaved Option A pgfplots snippet to: {pgf_optionA}")
    print(f"Saved Option B pgfplots snippet to: {pgf_optionB}")

    print("\n=== DONE ===")
    print(f"Figures saved in: {OUTPUT_DIR}")
    print("Use Option A for separate-scale residual panels.")
    print("Use Option B for log-scale convergence / non-convergence comparison.")


if __name__ == "__main__":
    main()