import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('TkAgg') # Interactive backend

def plot_vortex_topologies():
    fig = plt.figure(figsize=(12, 6))

    # --- Subplot 1: The "Wrong" Model (Vortex Ring) ---
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')

    # Torus parametrization
    theta = np.linspace(0, 2 * np.pi, 100)
    phi = np.linspace(0, 2 * np.pi, 100)
    Theta, Phi = np.meshgrid(theta, phi)
    R, r = 3, 1  # Major and minor radius

    X = (R + r * np.cos(Phi)) * np.cos(Theta)
    Y = (R + r * np.cos(Phi)) * np.sin(Theta)
    Z = r * np.sin(Phi)

    # Plot Torus surface
    ax1.plot_surface(X, Y, Z, color='cyan', alpha=0.3, edgecolor='none')

    # Plot a flow line (winding)
    swirl_theta = np.linspace(0, 2 * np.pi, 200)
    # Simple loop for core
    xc = R * np.cos(swirl_theta)
    yc = R * np.sin(swirl_theta)
    zc = np.zeros_like(swirl_theta)
    ax1.plot(xc, yc, zc, 'r-', linewidth=3, label='Vortex Core (Singularity)')

    # Swirl vector indication
    ax1.quiver(R, 0, 0, 0, 0, 2, color='b', length=1.5, label='Torsion Vector (T)')

    ax1.set_title("Current Model: Vortex Ring\n(Localized, Massive-like Topology)")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_zlabel("z")
    ax1.legend()
    ax1.set_xlim(-4, 4)
    ax1.set_ylim(-4, 4)
    ax1.set_zlim(-4, 4)

    # --- Subplot 2: The "Refactored" Model (Helical Torsion Wave) ---
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')

    z_line = np.linspace(-4, 4, 200)
    # Helix parametrization (Transverse Torsion)
    freq = 3
    x_helix = np.cos(freq * z_line)
    y_helix = np.sin(freq * z_line)

    # Plot the path of the disturbance
    ax2.plot(x_helix, y_helix, z_line, 'r-', linewidth=2, label='Torsion Wavefront')

    # Plot "Field Vectors" (Swirl displacement)
    # Sample fewer points for clarity
    z_sample = np.linspace(-4, 4, 20)
    x_sample = np.cos(freq * z_sample)
    y_sample = np.sin(freq * z_sample)

    ax2.quiver(np.zeros_like(z_sample), np.zeros_like(z_sample), z_sample,
               x_sample, y_sample, np.zeros_like(z_sample),
               color='b', length=1.0, label='Swirl Displacement (Polarization)')

    # Central Axis
    ax2.plot([0, 0], [0, 0], [-4, 4], 'k--', alpha=0.5)

    ax2.set_title("Refactored Model: Propagating Torsion\n(Transverse Wave, Massless)")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_zlabel("Propagation (z)")
    ax2.legend()

    plt.tight_layout()
    plt.savefig('vortex_refactor_comparison.png')
    plt.show()

plot_vortex_topologies()