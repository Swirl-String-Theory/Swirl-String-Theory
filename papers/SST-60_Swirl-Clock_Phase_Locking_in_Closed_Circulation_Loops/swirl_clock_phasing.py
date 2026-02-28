import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')  # Ensure it uses Tkinter backend

# -----------------------------
# Parameters (edit these)
# -----------------------------
tau = 20.0          # delay / circulation time
Omega0 = 1.0        # natural frequency
K = 0.4             # feedback strength

# Derived dimensionless parameters
omega0 = Omega0 * tau          # = Ω0 τ
beta = K * tau                 # = K τ
# Phase-locking equation in u = Ωτ:
# u = ω0 - β sin(u)
# Equivalent root form:
# g(u) := ω0 - β sin(u) - u = 0

def g(u):
    return omega0 - beta*np.sin(u) - u

def A(u):
    # stability indicator used in your text: A = K cos(u)
    return K*np.cos(u)

def is_stable(u):
    # "stable if A>0" (as in your caption)
    return A(u) > 0.0

# -----------------------------
# Root finding by scanning + bisection
# -----------------------------
def find_roots_bisection(func, u_min, u_max, N_scan=40000, bisect_iter=80, dedup_eps=1e-4):
    u_grid = np.linspace(u_min, u_max, N_scan)
    f_grid = func(u_grid)

    # detect sign changes
    idx = np.where(np.sign(f_grid[:-1]) * np.sign(f_grid[1:]) < 0)[0]

    roots = []
    for i in idx:
        a, b = u_grid[i], u_grid[i+1]
        fa, fb = func(a), func(b)
        # bisection
        for _ in range(bisect_iter):
            c = 0.5*(a+b)
            fc = func(c)
            if fa*fc <= 0:
                b, fb = c, fc
            else:
                a, fa = c, fc
        roots.append(0.5*(a+b))

    roots = np.array(sorted(roots))
    if roots.size == 0:
        return roots

    # de-duplicate close roots
    keep = [roots[0]]
    for r in roots[1:]:
        if abs(r - keep[-1]) > dedup_eps:
            keep.append(r)
    return np.array(keep)

# -----------------------------
# Choose plotting window:
# Option A (recommended): zoom to the "physically relevant" region around ω0 ± β
# because intersections must satisfy u = ω0 - β sin u ∈ [ω0-β, ω0+β]
# -----------------------------
u_phys_min = omega0 - beta
u_phys_max = omega0 + beta

# Add a margin so curves are readable
margin = 0.25 * (u_phys_max - u_phys_min) + 0.5
u_min = max(0.0, u_phys_min - margin)
u_max = u_phys_max + margin

# If you want a "wide view", uncomment:
# u_min, u_max = 0.0, max(4*np.pi, omega0 + 6*beta + 10*np.pi)

roots = find_roots_bisection(g, u_min, u_max)

Omega_roots = roots / tau
stable_mask = np.array([is_stable(u) for u in roots], dtype=bool)
A_vals = A(roots)

# -----------------------------
# Explanatory console output
# -----------------------------
print("\n=== Phase-locking summary ===")
print(f"tau   = {tau}")
print(f"Omega0= {Omega0}")
print(f"K     = {K}")
print(f"omega0= Omega0*tau = {omega0}")
print(f"beta  = K*tau      = {beta}")
print("Equation: u = omega0 - beta sin(u), where u = Omega*tau")
print("Roots u are discrete phase-locked branches; Omega = u/tau.")
print("Stability tag used: stable iff A = K cos(u) > 0.\n")

print("Roots (u), Omega, stability, A=K cos(u):")
for u, Om, st, Aval in zip(roots, Omega_roots, stable_mask, A_vals):
    print(f"u={u:10.5f}   Omega={Om:10.6f}   {'stable' if st else 'unstable':8s}   A={Aval:+.6f}")

# -----------------------------
# Make figure with matched x-axes and better readability
# Add: extra curve g(u) as dashed line around 0 (optional)
# Add: vertical guides at each root so panels align (recommended)
# -----------------------------
fig = plt.figure(figsize=(10, 6.6), constrained_layout=True)
gs = fig.add_gridspec(2, 1, height_ratios=[1,1], hspace=0.18)

# Panel (a): intersections
ax1 = fig.add_subplot(gs[0, 0])

u_plot = np.linspace(u_min, u_max, 4000)

# Main curves: y=u and y=omega0 - beta sin u
ax1.plot(u_plot, u_plot, lw=1.2, alpha=0.35, label=r"$y=u$")
ax1.plot(u_plot, omega0 - beta*np.sin(u_plot), lw=1.2, label=r"$y=\omega_0-\beta\sin u$")

# Extra curve option (same roots): g(u)=omega0-beta sin u - u, plotted on a twin axis
# This gives intuition: roots are exactly where g(u)=0.
ax1b = ax1.twinx()
ax1b.plot(u_plot, g(u_plot), lw=0.9, ls="--", alpha=0.35, label=r"$g(u)=\omega_0-\beta\sin u-u$")
ax1b.axhline(0.0, lw=0.8, ls=":", alpha=0.7)
ax1b.tick_params(axis='y', labelsize=9)
ax1b.set_ylabel(r"$g(u)$", rotation=270, labelpad=10, fontsize=9)

# Mark roots
if roots.size:
    ax1.scatter(roots, roots, s=26, zorder=5)

# Make panel (a) “TikZ-like”: same x and y window so the y=u line is visually honest
ax1.set_xlim(u_min, u_max)
ax1.set_ylim(u_min, u_max)
ax1.set_xlabel(r"")
ax1.set_ylabel(r"$y$")
ax1.set_title(r"Graphical solution of $u=\omega_0-\beta\sin u$", pad=6)
ax1.grid(True, alpha=0.25)

# Combine legends from ax1 and ax1b
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax1b.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", frameon=True)

# Panel (b): Omega vs u with stability
ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)

if roots.size:
    # stable
    ax2.scatter(
        roots[stable_mask],
        Omega_roots[stable_mask],
        s=60,
        marker="o",
        color="tab:blue",
        edgecolors="black",
        linewidths=0.8,
        zorder=5,
        label=r"stable ($A>0$)"
    )

    # unstable
    ax2.scatter(
        roots[~stable_mask],
        Omega_roots[~stable_mask],
        s=80,
        marker="o",
        facecolors="white",
        edgecolors="tab:red",
        linewidths=1.6,
        zorder=6,
        label=r"unstable ($A<0$)"
    )

ax2.set_xlim(u_min, u_max)
ax2.set_xlabel(r"$u=\Omega\tau$")
ax2.plot(u_plot, u_plot/tau, lw=1.0, alpha=0.7, label=r"$\Omega=u/\tau$")
ax2.set_ylabel(r"$\Omega$")
ax2.set_title("Discrete phase-locked modes and stability filtering", pad=6)
ax2.grid(True, alpha=0.25)
ax2.legend(loc="upper left", frameon=True)



fig.savefig("swirl_clock_phase_locking.png", dpi=300)
fig.savefig("swirl_clock_phase_locking.pdf")
plt.show()