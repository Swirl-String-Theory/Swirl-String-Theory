import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, TextBox, RadioButtons
from mpl_toolkits.mplot3d import Axes3D
import os
import matplotlib
matplotlib.use('TkAgg') # Interactive backend

# --- Import Compiled SST Library ---
try:
    import sstbindings
    # We assume the new binding is named 'biot_savart_vector_potential_grid'
    # and the helicity metric is in SSTGravity or FieldKernels
    from sstbindings import SSTGravity, biot_savart_velocity
    HAS_SST = True
    print("SUCCESS: SST C++ Bindings loaded.")
except ImportError:
    HAS_SST = False
    print("WARNING: 'sstbindings' not found. Falling back to Python placeholders.")

# --- Constants ---
V_SWIRL = 1.09384563e6
OMEGA_DEFAULT = 10.9e6

# --- Geometry Generator ---
def generate_rodin_starship(R=1.0, r=0.4, num_turns=12, num_points=2000):
    theta = np.linspace(0, num_turns * 2 * np.pi, num_points)
    phi = (2 + 2/5) * theta # Starship winding ratio

    x = (R + r * np.cos(phi)) * np.cos(theta)
    y = (R + r * np.cos(phi)) * np.sin(theta)
    z = r * np.sin(phi)

    points = np.stack([x, y, z], axis=-1)
    tangents = np.diff(points, axis=0)
    tangents = np.vstack([tangents, tangents[-1]])
    return points, tangents

# --- Physics Engine ---
def compute_sst_fields(points, tangents, grid_N=15, bounds=2.0):
    # 1. Setup Grid
    xs = np.linspace(-bounds, bounds, grid_N)
    ys = np.linspace(-bounds, bounds, grid_N)
    zs = np.linspace(-bounds, bounds, grid_N)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    grid_points = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)

    N_points = len(grid_points)

    if HAS_SST:
        # A. Compute B-Field (Velocity)
        print("Computing B-Field (Velocity)...")
        # Uses standard Biot-Savart
        V_flat = np.array([biot_savart_velocity(p.tolist(), points.tolist(), tangents.tolist()) for p in grid_points])

        # B. Compute A-Field (Vector Potential)
        print("Computing A-Field (Ether Momentum)...")
        try:
            # Calling the new binding we defined above
            # It returns tuple (Ax, Ay, Az)
            Ax, Ay, Az = sstbindings.biot_savart_vector_potential_grid(points, grid_points, 1.0)
            A_flat = np.stack([Ax, Ay, Az], axis=-1)
        except AttributeError:
            print("!! Binding 'biot_savart_vector_potential_grid' not found. Using Zero A-Field.")
            A_flat = np.zeros_like(V_flat)

        # C. Compute Helicity Density h = A . B
        print("Computing Helicity Density...")
        try:
            # Using the Kernel from sst_gravity.h
            h_map = np.array(SSTGravity.compute_helicity_density(A_flat, V_flat))
        except AttributeError:
            # Fallback: Numpy dot product
            h_map = np.sum(A_flat * V_flat, axis=1)

    else:
        # Fallback for testing GUI without C++
        V_flat = np.random.rand(N_points, 3) - 0.5
        A_flat = np.random.rand(N_points, 3) - 0.5
        h_map = np.sum(A_flat * V_flat, axis=1)

    return X, Y, Z, V_flat, A_flat, h_map

# --- Visualization App ---
class HelicityGui:
    def __init__(self):
        self.params = { "R": 1.0, "r": 0.4, "turns": 12, "grid_N": 11 }

        self.fig = plt.figure(figsize=(14, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(left=0.25, right=0.95, bottom=0.1)

        self.recompute()
        self.init_widgets()
        self.update_plot()

    def recompute(self):
        self.coil_pts, self.coil_tan = generate_rodin_starship(
            self.params["R"], self.params["r"], self.params["turns"]
        )
        (self.X, self.Y, self.Z, self.V, self.A, self.h_map) = compute_sst_fields(
            self.coil_pts, self.coil_tan, self.params["grid_N"]
        )

    def init_widgets(self):
        # Mode Selector
        rax = plt.axes([0.02, 0.65, 0.18, 0.2])
        self.radio = RadioButtons(rax,
                                  ('Helicity Density (h)', 'Vector Potential (A)', 'Magnetic Field (B)'), active=0)
        self.radio.on_clicked(self.update_plot)

        # Parameter Boxes
        self.boxes = {}
        y_off = 0.5
        for key in ["R", "r", "turns", "grid_N"]:
            ax_box = plt.axes([0.06, y_off, 0.05, 0.04])
            plt.text(0.01, y_off+0.01, key, transform=plt.gcf().transFigure)
            tb = TextBox(ax_box, '', initial=str(self.params[key]))
            tb.on_submit(self.make_callback(key))
            self.boxes[key] = tb
            y_off -= 0.06

    def make_callback(self, key):
        def callback(text):
            try:
                val = float(text)
                if key in ["turns", "grid_N"]: val = int(val)
                self.params[key] = val
                print(f"Updated {key}. Recomputing...")
                self.recompute()
                self.update_plot()
            except ValueError: pass
        return callback

    def update_plot(self, label=None):
        self.ax.clear()
        mode = self.radio.value_selected

        # Plot Coil
        self.ax.plot(self.coil_pts[:,0], self.coil_pts[:,1], self.coil_pts[:,2],
                     c='k', lw=1.5, alpha=0.4, label="Winding")

        # Flatten Arrays
        Xf, Yf, Zf = self.X.flatten(), self.Y.flatten(), self.Z.flatten()

        if mode == 'Helicity Density (h)':
            # We plot B-Field arrows, COLORED by Helicity Density
            # Red = High Knottedness (Topological Lock)
            # Blue = Zero/Low Helicity

            vecs = self.V # Use B-Field for direction
            colors = self.h_map # Use h for color
            title = "Magnetic Helicity Density ($h = \\vec{A} \\cdot \\vec{B}$)\n(Red = Stable Vacuum Vortex)"
            cmap = 'nipy_spectral'

            # Filter weak fields
            mag = np.linalg.norm(vecs, axis=1)
            mask = mag > np.percentile(mag, 20)

        elif mode == 'Vector Potential (A)':
            # Plot A-Field arrows
            vecs = self.A
            mag = np.linalg.norm(vecs, axis=1)
            colors = mag
            title = "Vector Potential Field ($\\vec{A}$)\n(Ether Momentum Stream)"
            cmap = 'viridis'
            mask = mag > 0.0

        else: # B-Field
            vecs = self.V
            mag = np.linalg.norm(vecs, axis=1)
            colors = mag
            title = "Magnetic Flux ($\\vec{B}$)"
            cmap = 'plasma'
            mask = mag > 0.0

        # Normalize vectors for clean quiver
        V_norm = vecs / (np.linalg.norm(vecs, axis=1)[:, np.newaxis] + 1e-9)

        self.ax.quiver(Xf[mask], Yf[mask], Zf[mask],
                       V_norm[mask,0], V_norm[mask,1], V_norm[mask,2],
                       length=0.25, normalize=True, cmap=cmap, array=colors[mask])

        self.ax.set_title(title)
        self.ax.set_xlim(-2, 2); self.ax.set_ylim(-2, 2); self.ax.set_zlim(-2, 2)
        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    app = HelicityGui()
    plt.show()