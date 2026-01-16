import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import os
import matplotlib
matplotlib.use('TkAgg')  # Ensure it uses Tkinter backend
script_name = os.path.splitext(os.path.basename(__file__))[0]

# ========== Parameters ==========
num_magnets = 12
radius = 1.2
dipole_ring_radius = 1.5
arrow_length = 0.3
offset = 0.1
winding_colors = np.linspace(0, 1, num_magnets, endpoint=False)
x_range = (-2, 2)
y_range = (-2, 2)
z_range = (-2, 2)
X, Y, Z = np.meshgrid(np.linspace(*x_range, 11), np.linspace(*y_range, 11), np.linspace(*z_range, 11))


def saving(plot):
    filename = f"{script_name}.png"
    plot.savefig(filename, dpi=150)  # Save image with high resolution

# ========== Magnetic Field Utilities ==========
def magnetic_field_dipole(r, m):
    mu0 = 1.0  # normalized
    norm_r = np.linalg.norm(r)
    if norm_r < 1e-8:
        return np.zeros(3)
    r_hat = r / norm_r
    return (mu0 / (4 * np.pi * norm_r**3)) * (3 * np.dot(m, r_hat) * r_hat - m)

def generate_dipole_ring(radius, num_magnets, z_offset=0.0, invert=False):
    positions = []
    orientations = []
    for i in range(num_magnets):
        phi = 2 * np.pi * i / num_magnets
        x, y, z = radius * np.cos(phi), radius * np.sin(phi), z_offset
        mx = np.cos(2 * phi)
        my = np.sin(2 * phi)
        mz = np.cos(phi)
        m = np.array([mx, my, (-1 if invert else 1) * mz])
        m /= np.linalg.norm(m)
        orientations.append(m)
        positions.append(np.array([x, y, z]))
    return positions, orientations


middle_pos, middle_ori = generate_dipole_ring(dipole_ring_radius, num_magnets, z_offset=0.0)


# ========== Plotting ==========
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for pos, ori, c in zip(middle_pos, middle_ori, winding_colors):
    start = pos - ori * 0.3
    ax.quiver(*start, *ori, length=0.6, color=plt.cm.hsv(c), linewidth=2, arrow_length_ratio=0.25)


ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim(*x_range)
ax.set_ylim(*y_range)
ax.set_zlim(*z_range)
ax.set_box_aspect([1, 1, 1])
plt.tight_layout()
saving(plt)
plt.show()