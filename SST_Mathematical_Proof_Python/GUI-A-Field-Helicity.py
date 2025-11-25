import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, CheckButtons
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('TkAgg') # Essential for interactive GUI

# --- IMPORT SST BINDINGS ---
try:
    import sstbindings
    # Attempt to import the new grid-based potential binding
    # If you named it 'biot_savart_vector_potential_grid' in your py_field_kernels.cpp
    from sstbindings import biot_savart_vector_potential_grid, biot_savart_velocity_grid, SSTGravity
    HAS_SST = True
    print("SUCCESS: SST C++ Bindings loaded.")
except ImportError:
    HAS_SST = False
    print("WARNING: 'sstbindings' not found. Simulation will fail or use mock data.")
except AttributeError:
    print("WARNING: Specific functions not found in sstbindings. Re-compile your library.")
    HAS_SST = False

# --- GEOMETRY GENERATORS ---

def generate_ring(radius=1.0, points=200):
    t = np.linspace(0, 2*np.pi, points)
    x = radius * np.cos(t)
    y = radius * np.sin(t)
    z = np.zeros_like(t)

    pts = np.stack([x,y,z], axis=-1)
    tangents = np.diff(pts, axis=0, prepend=pts[[-1]])
    return pts, tangents

def generate_trefoil(scale=1.0, points=300):
    t = np.linspace(0, 2*np.pi, points)
    # Parametric Trefoil Knot
    x = scale * (np.sin(t) + 2 * np.sin(2 * t))
    y = scale * (np.cos(t) - 2 * np.cos(2 * t))
    z = scale * (-np.sin(3 * t))

    pts = np.stack([x,y,z], axis=-1)
    tangents = np.diff(pts, axis=0, prepend=pts[[-1]])
    return pts, tangents

# --- PHYSICS KERNEL ---

def compute_fields(pts, tangents, current=1.0, grid_n=15, bounds=2.5):
    # 1. Setup Grid
    vals = np.linspace(-bounds, bounds, grid_n)
    X, Y, Z = np.meshgrid(vals, vals, vals, indexing='ij')
    grid_flat = np.stack([X.flatten(), Y.flatten(), Z.flatten()], axis=-1)

    # 2. Compute Fields via C++
    if HAS_SST:
        # Magnetic Field (B)
        try:
            # FIX: Check return type.
            # py_biot_savart.cpp returns a single (N,3) array, NOT a tuple.
            if hasattr(sstbindings, 'biot_savart_velocity_grid'):
                B_result = sstbindings.biot_savart_velocity_grid(pts, grid_flat)

                # Handle potential shape mismatch if binding changed
                if isinstance(B_result, tuple) or isinstance(B_result, list):
                    # If it returns (Bx, By, Bz)
                    B_flat = np.stack(B_result, axis=-1)
                else:
                    # If it returns (N, 3) array directly
                    B_flat = B_result
            else:
                # Fallback to loop if grid wrapper missing
                from sstbindings import biot_savart_velocity
                B_flat = np.array([biot_savart_velocity(p, pts, tangents) for p in grid_flat])
        except Exception as e:
            print(f"Error computing B: {e}")
            B_flat = np.zeros_like(grid_flat)

        # Vector Potential (A) -> THE NEW METRIC
        try:
            # This calls your new 'biot_savart_vector_potential' wrapper
            # In py_field_kernels.cpp, this IS defined to return py::make_tuple(Ax, Ay, Az)
            A_result = sstbindings.biot_savart_vector_potential_grid(pts, grid_flat, current)

            if isinstance(A_result, tuple) or isinstance(A_result, list):
                A_flat = np.stack(A_result, axis=-1)
            else:
                A_flat = A_result

        except Exception as e:
            print(f"Error computing A (Check binding name): {e}")
            A_flat = np.zeros_like(grid_flat)

        # Helicity Density (h = A . B)
        try:
            h_flat = np.array(SSTGravity.compute_helicity_density(A_flat, B_flat))
        except Exception as e:
            # Fallback numpy dot product
            h_flat = np.sum(A_flat * B_flat, axis=1)

    else:
        # Mock data for interface testing
        B_flat = np.random.rand(*grid_flat.shape) * 0.1
        A_flat = np.random.rand(*grid_flat.shape) * 0.1
        h_flat = np.sum(A_flat * B_flat, axis=1)

    return grid_flat, B_flat, A_flat, h_flat

# --- GUI CLASS ---

class VectorPotentialGui:
    def __init__(self):
        self.fig = plt.figure(figsize=(14, 9))
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(left=0.25, bottom=0.1)

        self.grid_n = 13
        self.current_geom = 'Trefoil'

        self.run_sim()
        self.init_widgets()
        self.update_view()

    def run_sim(self):
        if self.current_geom == 'Ring':
            self.pts, self.tans = generate_ring()
        else:
            self.pts, self.tans = generate_trefoil()

        self.grid, self.B, self.A, self.h = compute_fields(self.pts, self.tans, grid_n=self.grid_n)

    def init_widgets(self):
        # Geometry Selector
        ax_geom = plt.axes([0.02, 0.75, 0.15, 0.12])
        self.rad_geom = RadioButtons(ax_geom, ('Trefoil', 'Ring'), active=0)
        self.rad_geom.on_clicked(self.change_geom)

        # Field Selector
        ax_field = plt.axes([0.02, 0.50, 0.15, 0.2])
        self.rad_field = RadioButtons(ax_field,
                                      ('Vector Potential (A)', 'Magnetic Field (B)', 'Helicity Density (h)'), active=0)
        self.rad_field.on_clicked(self.update_view)

        ax_field.set_title("Visualize Field:")

    def change_geom(self, label):
        self.current_geom = label
        print(f"Switching to {label}...")
        self.run_sim()
        self.update_view()

    def update_view(self, label=None):
        self.ax.clear()

        # Draw Geometry
        self.ax.plot(self.pts[:,0], self.pts[:,1], self.pts[:,2], 'k-', lw=2, alpha=0.6)

        mode = self.rad_field.value_selected

        # Data Prep
        X, Y, Z = self.grid[:,0], self.grid[:,1], self.grid[:,2]

        if mode == 'Vector Potential (A)':
            # A-Field follows the current flow (Ether Momentum)
            V = self.A
            mag = np.linalg.norm(V, axis=1)
            title = r"Vector Potential $\vec{A}$ (Ether Momentum)"
            cmap = 'viridis'

        elif mode == 'Magnetic Field (B)':
            # B-Field curls around the current
            V = self.B
            mag = np.linalg.norm(V, axis=1)
            title = r"Magnetic Field $\vec{B}$ (Vortex Flux)"
            cmap = 'plasma'

        elif mode == 'Helicity Density (h)':
            # Plot B-Vectors colored by Helicity
            V = self.B
            mag = self.h # Color by scalar h
            title = r"Helicity Density $h = \vec{A} \cdot \vec{B}$ (Topological Lock)"
            cmap = 'coolwarm'

        # Filter for clarity
        mask = np.linalg.norm(self.B, axis=1) > 0.05

        # Normalize arrows
        V_norm = V / (np.linalg.norm(V, axis=1)[:,None] + 1e-9)

        # Plot Quiver
        q = self.ax.quiver(X[mask], Y[mask], Z[mask],
                           V_norm[mask,0], V_norm[mask,1], V_norm[mask,2],
                           length=0.3, normalize=True, cmap=cmap, array=mag[mask])

        self.ax.set_title(title)
        self.ax.set_xlim(-2,2); self.ax.set_ylim(-2,2); self.ax.set_zlim(-2,2)
        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    app = VectorPotentialGui()
    plt.show()