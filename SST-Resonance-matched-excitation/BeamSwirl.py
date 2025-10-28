# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib
# --- Headless-safe backend guard ---
if not (os.environ.get("DISPLAY") or os.environ.get("MPLBACKEND")):
    matplotlib.use("Agg")  # no GUI needed on servers/CI
import matplotlib.pyplot as plt

# ===== Constants (SST canonical) =====
Ce = 1.09384563e6        # m/s
rc = 1.40897017e-15      # m
omega_0 = Ce / rc        # central angular frequency
delta_omega = 0.1 * omega_0  # beam spectral width (10% spread)

# ===== Beam & target (absolute frequency) =====
def rho_beam(omega):
    A = 1.0
    return A * np.exp(-(omega - omega_0)**2 / (2 * delta_omega**2))

def sigma_knot_abs(omega, omega_n_list, Gamma_n_list, B_n_list):
    out = np.zeros_like(omega, dtype=float)
    for w0, G, B in zip(omega_n_list, Gamma_n_list, B_n_list):
        out += B * (G**2) / ((omega - w0)**2 + G**2)
    return out

# ===== Target lines (absolute frequency) =====
omega_n_list = np.array([0.95, 1.00, 1.05]) * omega_0
Gamma_n_list = np.array([0.02, 0.01, 0.02]) * omega_0
B_n_list     = np.array([1.0, 2.0, 1.0])

# ===== Baseband (detuning) representations =====
Delta_n_list = omega_n_list - omega_0
Sigma_beam   = delta_omega
Gamma_n_det  = Gamma_n_list

def rho_beam_det(Delta):
    A = 1.0
    return A * np.exp(-(Delta)**2 / (2 * Sigma_beam**2))

def sigma_knot_det(Delta):
    out = np.zeros_like(Delta, dtype=float)
    for Dn, Gn, B in zip(Delta_n_list, Gamma_n_det, B_n_list):
        out += B * (Gn**2) / ((Delta - Dn)**2 + Gn**2)
    return out

# ---- NumPy 1.x/2.x trapezoid compatibility
try:
    trapz = np.trapezoid
except AttributeError:
    trapz = np.trapz

# ===== Frequency-domain plot (integrand + integral) =====
def make_frequency_domain_overlap_plot(savepath="sst_spectral_overlap.png"):
    omega_axis = np.linspace(0.9 * omega_0, 1.1 * omega_0, 2000)
    beam = rho_beam(omega_axis)
    knot = sigma_knot_abs(omega_axis, omega_n_list, Gamma_n_list, B_n_list)
    integrand = beam * knot
    Y_scalar = trapz(integrand, omega_axis)

    plt.figure(figsize=(10, 6))
    plt.plot(omega_axis, beam, label=r'Beam $\rho_{\mathrm{beam}}(\omega)$', linestyle='--')
    plt.plot(omega_axis, knot, label=r'Target $\sigma(\omega)$', linestyle=':')
    plt.plot(omega_axis, integrand, label=r'Overlap integrand $\rho\,\sigma$', linewidth=2)
    plt.xlabel(r'Angular frequency $\omega$ (rad/s)')
    plt.ylabel(r'Amplitude (a.u.)')
    plt.title(r'Spectral Overlap in SST (Gaussian $\times$ sum of Lorentzians)')
    ax = plt.gca()
    ax.text(0.02, 0.95, rf'$Y={Y_scalar:.2e}$', transform=ax.transAxes, ha='left', va='top')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(savepath, dpi=160)
    if matplotlib.get_backend().lower() != "agg":
        plt.show()
    print(f"Saved: {savepath}")
    print(f"Integrated overlap Y = {Y_scalar:.3e} (a.u.)")

# ===== Time-domain via baseband kernel =====
def pulse_envelope(t, tau):
    return np.exp(-(t**2) / (tau**2))

def compute_time_domain_response_baseband(
        N=4096, dt=1e-20, taus=(1e-18, 5e-18, 1e-17), energy_normalize=False
):
    """
    Baseband simulation:
      1) Δω grid from FFT (centered).
      2) σ_det(Δω) -> IFFT with (Δω/2π) scaling -> K_env(t).
      3) Convolve F_env with K_env (dt factor).
      If energy_normalize=True, each envelope is L2-normalized (unit energy).
    """
    # Time grid (centered, length N)
    t = np.linspace(-N//2 * dt, (N//2 - 1) * dt, N)

    # Detuning grid (angular frequency), consistent with numpy FFT
    domega = 2.0 * np.pi / (N * dt)
    Delta_omega = np.fft.fftfreq(N, d=dt) * 2.0 * np.pi
    Delta_omega = np.fft.fftshift(Delta_omega)

    # Build K_env(t) from σ_det(Δω)
    sigma_vals = sigma_knot_det(Delta_omega)
    K_env = np.fft.ifft(np.fft.ifftshift(sigma_vals)) * (domega / (2.0 * np.pi))
    K_env = np.fft.fftshift(np.real(K_env))

    responses = []
    for tau in taus:
        F_env = pulse_envelope(t, tau)
        if energy_normalize:
            norm = np.sqrt(trapz(F_env**2, t))
            if norm > 0:
                F_env = F_env / norm
        S_env = np.convolve(F_env, K_env, mode='same') * dt
        responses.append((tau, F_env, S_env))
    return t, responses

def make_time_domain_plots(savepath_main="sst_time_response_env.png",
                           savepath_zoom="sst_time_response_env_zoom.png",
                           energy_normalize=False):
    t, responses = compute_time_domain_response_baseband(energy_normalize=energy_normalize)

    # Full response
    plt.figure(figsize=(12, 8))
    for tau, F_env, S_env in responses:
        plt.plot(t * 1e15, S_env, label=fr'Envelope $\tau={tau*1e18:.0f}\,\mathrm{{as}}$')
    plt.title(r'Time-Domain Envelope Response $S_{\mathrm{env}}(t)$ for Varying Pulse Widths')
    plt.xlabel(r'Time (fs)')
    plt.ylabel(r'Response (a.u.)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(savepath_main, dpi=160)
    if matplotlib.get_backend().lower() != "agg":
        plt.show()
    print(f"Saved: {savepath_main}")

    # Zoomed to the actual half-span of the window
    half_span = 0.5 * (t.max() - t.min())
    zoom = np.abs(t) < half_span
    half_span_fs = half_span * 1e15

    plt.figure(figsize=(10, 4))
    for tau, F_env, S_env in responses:
        plt.plot(t[zoom] * 1e15, S_env[zoom], label=fr'$\tau={tau*1e18:.0f}\,\mathrm{{as}}$')
    plt.title(rf'Zoomed Envelope Response $S_{{\rm env}}(t)$ (|t| < ${half_span_fs:.3f}\,\mathrm{{fs}}$)')
    plt.xlabel(r'Time (fs)')
    plt.ylabel(r'Response (a.u.)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(savepath_zoom, dpi=160)
    if matplotlib.get_backend().lower() != "agg":
        plt.show()
    print(f"Saved: {savepath_zoom}")

if __name__ == '__main__':
    make_frequency_domain_overlap_plot()
    # energy_normalize=True makes the curves comparable by equal pulse energy
    make_time_domain_plots(energy_normalize=False)