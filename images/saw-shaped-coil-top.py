import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg') # Interactive backend

def generate_winding_sequence(start_node, n_points, step_forward, step_backward, n_steps=20):
    sequence = [start_node]
    current = start_node
    for _ in range(n_steps):
        # Forward step
        next_node = (current + step_forward - 1) % n_points + 1
        sequence.append(next_node)
        # Backward step
        current = (next_node - step_backward - 1) % n_points + 1
        sequence.append(current)
    return sequence

def plot_gamma_coil():
    n_points = 40
    radius = 1.0

    # Angles for the 40 points (0 at top, clockwise)
    angles = np.linspace(np.pi/2, np.pi/2 - 2*np.pi, n_points, endpoint=False)

    # Points coordinates
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)

    plt.figure(figsize=(10, 10))

    # Plot slots
    plt.scatter(x, y, c='black', s=50, zorder=5)
    for i in range(n_points):
        plt.text(x[i]*1.1, y[i]*1.1, str(i+1), ha='center', va='center', fontsize=8)

    # Generate sequences for 3 phases
    # Logic: Start -> +11 -> -9 -> +11 ...
    # We trace enough steps to complete a revolution or fill the pattern
    # A full cycle of +2 net advance on 40 points takes 20 'pairs' of steps to return to start?
    # 20 * 2 = 40. Yes.
    steps = 20
    seq_a = generate_winding_sequence(1, n_points, 11, 9, steps)
    seq_b = generate_winding_sequence(14, n_points, 11, 9, steps)
    seq_c = generate_winding_sequence(28, n_points, 11, 9, steps)

    # Plot windings
    # We use alpha to make it readable

    def plot_seq(seq, color, label):
        for i in range(len(seq)-1):
            start = seq[i]-1
            end = seq[i+1]-1
            # Draw line
            plt.plot([x[start], x[end]], [y[start], y[end]], color=color, alpha=0.6, linewidth=1)
            # Add arrow for direction on the first few segments
            if i < 3:
                mid_x = (x[start] + x[end])/2
                mid_y = (y[start] + y[end])/2
                plt.arrow(x[start], y[start], (x[end]-x[start])*0.6, (y[end]-y[start])*0.6,
                          head_width=0.05, color=color, zorder=4)

    plot_seq(seq_a, 'red', 'Phase A (Start 1)')
    plot_seq(seq_b, 'blue', 'Phase B (Start 14)')
    plot_seq(seq_c, 'green', 'Phase C (Start 28)')

    # Add legend proxy
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='red', lw=2),
                    Line2D([0], [0], color='blue', lw=2),
                    Line2D([0], [0], color='green', lw=2)]
    plt.legend(custom_lines, ['Phase A (Start 1)', 'Phase B (Start 14)', 'Phase C (Start 28)'], loc='upper right')

    plt.title(f"SST Gamma Coil Winding Diagram\nS=40, Step +11/-9")
    plt.axis('off')
    plt.savefig("saw-shaped-coil-top.png")

def calculate_sst_physics():
    # Constants
    rho_f = 7.0e-7 # kg/m^3 (SST Ether density)
    mu_0 = 4 * np.pi * 1e-7
    g = 9.81

    # Coil Specs
    D_min = 0.15 # m
    D_max = 0.20 # m
    D_avg = (D_min + D_max) / 2
    R_avg = D_avg / 2
    Area = np.pi * (R_avg**2)

    wire_diam = 0.8e-3 # m
    wire_rad = wire_diam / 2
    wire_area = np.pi * (wire_rad**2)
    rho_copper = 1.68e-8 # Ohm m

    # Length estimation
    # One "turn" in this pattern is a chord +11 and a chord -9
    # Chord length formula: C = 2R sin(theta/2)
    # Angle for 11 slots: 11 * (2pi/40)
    # Angle for 9 slots: 9 * (2pi/40)

    theta_11 = 11 * (2 * np.pi / 40)
    theta_9 = 9 * (2 * np.pi / 40)

    len_chord_11 = 2 * R_avg * np.sin(theta_11 / 2)
    len_chord_9 = 2 * R_avg * np.sin(theta_9 / 2)

    len_per_cycle = len_chord_11 + len_chord_9
    # 20 cycles per phase to complete the circle (net +2 progression * 20 = 40)
    total_len_per_phase = 20 * len_per_cycle

    # Resistance
    resistance = rho_copper * total_len_per_phase / wire_area

    # Inductance (Very rough approximation for a complex toroid/solenoid hybrid)
    # L approx mu0 * N^2 * A / l ? No, this is a star winding.
    # Let's skip L for now and focus on B field requirements.

    # SST Lift Calculation
    # To lift 1 kg (Test Mass)
    mass_test = 1.0
    F_req = mass_test * g

    # Required Swirl Velocity v_theta
    # F = 1/2 * rho_f * v^2 * A
    v_req = np.sqrt( (2 * F_req) / (rho_f * Area) )

    # Required B Field (assuming eta=1)
    # v = sqrt(eta / (mu0 * rho_f)) * B
    # B = v / sqrt(eta / (mu0 * rho_f))
    eta = 1.0
    conversion_factor = np.sqrt(eta / (mu_0 * rho_f))
    B_req = v_req / conversion_factor

    return {
        "Diameter": D_avg,
        "Wire Length (per phase)": total_len_per_phase,
        "Resistance (per phase)": resistance,
        "Required v_theta (1kg lift)": v_req,
        "Required B_field (1kg lift)": B_req,
        "Force per Tesla^2": (rho_f * Area / 2) * conversion_factor**2
    }

plot_gamma_coil()
physics_results = calculate_sst_physics()
print(physics_results)
plt.axis('on')
plt.text(0, 0, s=physics_results["Diameter"], ha='center', va='center', fontsize=8 )
plt.show()