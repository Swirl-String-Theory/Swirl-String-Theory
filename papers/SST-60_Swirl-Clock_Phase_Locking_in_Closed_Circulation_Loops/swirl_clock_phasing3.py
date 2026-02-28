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
omega0 = Omega0 * tau
beta = K * tau

# -----------------------------
# Self-consistency in u = Omega*tau:
# f(u) = u - omega0 + beta*sin(u) = 0
# -----------------------------
def f(u):
    return u - omega0 + beta * np.sin(u)

def stability_tag(u):
    # A = K cos(u) ; stable if A>0 (edit sign here if needed)
    A = K * np.cos(u)
    return A > 0, A

# -----------------------------
# Find roots by scanning intervals
# -----------------------------
u_min, u_max = 0.0, max(4*np.pi, omega0 + 6*beta + 10*np.pi)
N_scan = 20000
u_grid = np.linspace(u_min, u_max, N_scan)
f_grid = f(u_grid)

# bracketing sign changes
idx = np.where(np.sign(f_grid[:-1]) * np.sign(f_grid[1:]) < 0)[0]

roots = []
for i in idx:
    a, b = u_grid[i], u_grid[i+1]
    fa, fb = f(a), f(b)
    # bisection
    for _ in range(80):
        c = 0.5*(a+b)
        fc = f(c)
        if fa*fc <= 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    roots.append(0.5*(a+b))

# de-duplicate close roots
roots = np.array(sorted(roots))
if roots.size:
    keep = [roots[0]]
    for r in roots[1:]:
        if abs(r - keep[-1]) > 1e-3:
            keep.append(r)
    roots = np.array(keep)

# Convert to Omega roots
Omega_roots = roots / tau

stable_mask = []
A_vals = []
for u in roots:
    st, A = stability_tag(u)
    stable_mask.append(st)
    A_vals.append(A)
stable_mask = np.array(stable_mask, dtype=bool)
A_vals = np.array(A_vals)

# -----------------------------
# Make the figure
# -----------------------------
fig = plt.figure(figsize=(8.0, 6.0))

# Panel (a): intersection plot
ax1 = fig.add_subplot(2, 1, 1)
u_plot = np.linspace(u_min, u_max, 4000)
ax1.plot(u_plot, u_plot, label=r"$y=u$")
ax1.plot(u_plot, omega0 - beta*np.sin(u_plot), label=r"$y=\omega_0-\beta\sin u$")
if roots.size:
    ax1.scatter(roots, roots, s=18, marker="o", label="solutions")
ax1.set_xlabel(r"$u=\Omega\tau$")
ax1.set_ylabel(r"$y$")
ax1.set_title("Phase-locking intersections")
ax1.grid(True, alpha=0.3)
ax1.legend()

# Panel (b): discrete spectrum with stability
ax2 = fig.add_subplot(2, 1, 2)
if roots.size:
    # stable solutions
    ax2.scatter(roots[stable_mask], Omega_roots[stable_mask], s=28, marker="o", label="stable (A>0)")
    # unstable solutions
    ax2.scatter(roots[~stable_mask], Omega_roots[~stable_mask], s=28, marker="o", facecolors="none",
                label="unstable (A<0)")
ax2.set_xlabel(r"$u=\Omega\tau$")
ax2.set_ylabel(r"$\Omega$")
ax2.set_title("Discrete phase-locked modes and stability filtering")
ax2.grid(True, alpha=0.3)
ax2.legend()

fig.tight_layout()

# Save
fig.savefig("swirl_clock_phase_locking-wide.png", dpi=300)
fig.savefig("swirl_clock_phase_locking-wide.pdf")
plt.show()

# Print a small table for copy-paste into TikZ if you want
print("\nRoots (u), Omega, stability, A = K cos(u):")
for u, Om, st, A in zip(roots, Omega_roots, stable_mask, A_vals):
    print(f"u={u:9.5f}   Omega={Om:9.6f}   {'stable' if st else 'unstable'}   A={A:+.6f}")