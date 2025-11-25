import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('TkAgg') # Interactive backend

def visualize_sst_topology_shift():
    fig = plt.figure(figsize=(14, 6))

    # --- Subplot 1: The OLD Model (Vortex Ring) ---
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')

    # Torus Math
    n = 100
    theta = np.linspace(0, 2.*np.pi, n)
    phi = np.linspace(0, 2.*np.pi, n)
    theta, phi = np.meshgrid(theta, phi)
    c, a = 2, 1
    x = (c + a*np.cos(theta)) * np.cos(phi)
    y = (c + a*np.cos(theta)) * np.sin(phi)
    z = a * np.sin(theta)

    # Plot Surface
    ax1.plot_surface(x, y, z, rstride=5, cstride=5, color='red', alpha=0.3, edgecolor='k')

    # Annotations for "Wrong" features
    ax1.set_title("OLD MODEL: Vortex Ring\n(Localized, Massive, T-Phase)", fontsize=12, color='darkred')
    ax1.text(0, 0, 3.5, "Recirculating Flow\n(Implies Rest Mass)", ha='center', color='red')

    # --- Subplot 2: The NEW Model (Torsion Wave) ---
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')

    # Helix Math
    z_line = np.linspace(-4, 4, 200)
    x_line = np.cos(3 * z_line)
    y_line = np.sin(3 * z_line)

    # Plot Wave
    ax2.plot(x_line, y_line, z_line, color='blue', linewidth=3)

    # Swirl Vectors along the wave
    step = 10
    ax2.quiver(np.zeros_like(z_line[::step]), np.zeros_like(z_line[::step]), z_line[::step],
               x_line[::step], y_line[::step], np.zeros_like(z_line[::step]),
               length=1.0, color='cyan', arrow_length_ratio=0.3)

    # Annotations for "Correct" features
    ax2.set_title("NEW MODEL: Torsional Wave\n(Delocalized, Massless, R-Phase)", fontsize=12, color='darkblue')
    ax2.text(0, 0, 4.5, "Propagating Twist\n(Matches Maxwell)", ha='center', color='blue')

    # Formatting
    for ax in [ax1, ax2]:
        ax.set_axis_off()

    plt.tight_layout()
    plt.savefig('sst_topology_shift.png')
    plt.show()

visualize_sst_topology_shift()