import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, CheckButtons
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('TkAgg')

# --- 1. SST CORE INTEGRATION ---
try:
    import sstbindings
    from sstbindings import biot_savart_wire_grid, SSTGravity
    HAS_SST = True
    print("SUCCESS: SST C++ Bindings loaded (Saw-Bowl Mode).")
except ImportError:
    HAS_SST = False
    print("WARNING: 'sstbindings' not found. Using slow Python fallback.")

# --- SST Constants ---
V_SWIRL = 1.09384563e6  # m/s
OMEGA_DEFAULT = 10.9e6  # Hz
B_SAT_DEFAULT = 5.0     # Tesla

# --- GEOMETRY HELPERS (From Plotly Script) ---
S_DEFAULT = 40
STEP_FWD = 11
STEP_BWD = -9
POWER = 2.2

def alternating_skip_indices(S, step_fwd, step_bwd, n_pairs, start=1):
    idx = start
    seq = [idx]
    for k in range(2 * n_pairs):
        if k % 2 == 0:
            idx = (idx + step_fwd - 1) % S + 1
        else:
            idx = (idx + step_bwd - 1) % S + 1
        seq.append(idx)
    return np.array(seq, dtype=int)

def r_profile(s, Rb, Rt, profile, power):
    if profile == 'Exponential':
        return Rb + (Rt - Rb) * (s**power)
    elif profile == 'Inverse Exp':
        return Rt - (Rt - Rb) * (s**power)
    else:  # Linear
        return Rb + (Rt - Rb) * s

def generate_bowl_geometry(S, step_fwd, step_bwd, n_pairs, Rb, Rt, Hc,
                           profile='Exponential', mode='Curved', angle_offset=0.0):
    """
    Generates a single phase polyline (N, 3) for the Saw-Bowl geometry.
    """
    seq = alternating_skip_indices(S, step_fwd, step_bwd, n_pairs, start=1)
    slot_angles_base = np.linspace(0, 2*np.pi, S, endpoint=False) - np.pi/2.0

    N_segs = len(seq) - 1

    if mode == 'Curved':
        samples_per_seg = 12 # Reduced from 24 to keep physics calc fast
        total_points = N_segs * samples_per_seg

        # Parameter s goes from 0 to 1 along the whole coil
        s_nodes = np.linspace(0, 1, N_segs + 1)
        r_nodes = r_profile(s_nodes, Rb, Rt, profile, POWER)
        z_nodes = s_nodes # Normalized Z

        xs, ys, zs = [], [], []

        for k in range(N_segs):
            i0, i1 = seq[k]-1, seq[k+1]-1
            a0 = slot_angles_base[i0] + angle_offset
            a1 = slot_angles_base[i1] + angle_offset

            # Shortest path interpolation
            da = (a1 - a0 + np.pi) % (2*np.pi) - np.pi

            # Segment arrays
            t = np.linspace(0, 1, samples_per_seg, endpoint=False)
            a_line = a0 + t * da

            # Interpolate R and Z linearly between nodes (the nodes themselves follow the profile)
            # Note: For smoother profile adherence, we could interpolate s first, but this is standard
            r_line = np.linspace(r_nodes[k], r_nodes[k+1], samples_per_seg, endpoint=False)
            z_line = np.linspace(z_nodes[k], z_nodes[k+1], samples_per_seg, endpoint=False)

            xs.append(r_line * np.cos(a_line))
            ys.append(r_line * np.sin(a_line))
            zs.append(z_line)

        # Add last point
        k = N_segs
        # We just need the final node coordinate
        a_end = slot_angles_base[seq[-1]-1] + angle_offset
        xs.append([r_nodes[-1] * np.cos(a_end)])
        ys.append([r_nodes[-1] * np.sin(a_end)])
        zs.append([z_nodes[-1]])

        X = np.concatenate(xs)
        Y = np.concatenate(ys)
        Z = np.concatenate(zs) * Hc

    else: # Straight
        s_nodes = np.linspace(0, 1, N_segs + 1)
        r_nodes = r_profile(s_nodes, Rb, Rt, profile, POWER)
        z_nodes = s_nodes * Hc

        angles = slot_angles_base[seq-1] + angle_offset
        X = r_nodes * np.cos(angles)
        Y = r_nodes * np.sin(angles)
        Z = z_nodes

    return np.stack([X, Y, Z], axis=-1), seq

# --- PHYSICS ENGINE ---
def compute_sst_physics(phases_geometry, grid_dims, bounds):
    nx, ny, nz = grid_dims
    limit = bounds
    x = np.linspace(-limit, limit, nx)
    y = np.linspace(-limit, limit, ny)
    z = np.linspace(0, limit, nz) # Z usually 0 to Hc
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    Bx_tot = np.zeros_like(X)
    By_tot = np.zeros_like(Y)
    Bz_tot = np.zeros_like(Z)

    Xf, Yf, Zf = X.flatten(), Y.flatten(), Z.flatten()

    if HAS_SST:
        for polyline in phases_geometry:
            bx, by, bz = biot_savart_wire_grid(Xf, Yf, Zf, polyline, 1.0)
            Bx_tot += bx.reshape(X.shape)
            By_tot += by.reshape(Y.shape)
            Bz_tot += bz.reshape(Z.shape)
    else:
        # Fallback dummy data
        Bx_tot = X * 0.1
        By_tot = Y * 0.1
        Bz_tot = Z * 0.1

    B_mag = np.sqrt(Bx_tot**2 + By_tot**2 + Bz_tot**2) + 1e-9

    # Gradients for Shear
    dVz_dy = np.gradient(Bz_tot, y, axis=1)
    dVy_dz = np.gradient(By_tot, z, axis=2)
    dVx_dz = np.gradient(Bx_tot, z, axis=2)
    dVz_dx = np.gradient(Bz_tot, x, axis=0)
    dVy_dx = np.gradient(By_tot, x, axis=0)
    dVx_dy = np.gradient(Bx_tot, y, axis=1)

    Wx = dVz_dy - dVy_dz
    Wy = dVx_dz - dVz_dx
    Wz = dVy_dx - dVx_dy

    B_flat = np.stack([Bx_tot.flatten(), By_tot.flatten(), Bz_tot.flatten()], axis=-1)
    Curl_flat = np.stack([Wx.flatten(), Wy.flatten(), Wz.flatten()], axis=-1)

    if HAS_SST:
        shear = np.array(SSTGravity.compute_beltrami_shear(B_flat, Curl_flat)).reshape(X.shape)
        gravity = np.array(SSTGravity.compute_gravity_dilation(
            B_flat, OMEGA_DEFAULT, V_SWIRL, B_SAT_DEFAULT
        )).reshape(X.shape)
    else:
        shear = np.zeros_like(B_mag)
        gravity = np.ones_like(B_mag)

    return {
        "X":X, "Y":Y, "Z":Z,
        "Bx":Bx_tot/B_mag, "By":By_tot/B_mag, "Bz":Bz_tot/B_mag,
        "mag":B_mag, "shear":shear, "gravity":gravity
    }

# --- GUI APP ---
class SawBowlApp:
    def __init__(self):
        self.fig = plt.figure(figsize=(15, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(left=0.05, right=0.75, bottom=0.1)

        # Initial State
        self.params = {
            "Rb": 0.5, "Rt": 1.5, "layers": 20, "Hc": 1.0,
            "grid_res": 11, "bounds": 2.0
        }
        self.mode = "Curved"
        self.profile = "Exponential"
        self.phases_active = [True, True, True]

        self.init_gui()
        self.update()

    def init_gui(self):
        # Sliders Area (Bottom)
        ax_Rb = plt.axes([0.15, 0.08, 0.55, 0.03])
        ax_Rt = plt.axes([0.15, 0.04, 0.55, 0.03])
        ax_L  = plt.axes([0.15, 0.005, 0.25, 0.03])
        ax_H  = plt.axes([0.45, 0.005, 0.25, 0.03])

        self.sl_Rb = Slider(ax_Rb, 'R Base', 0.01, 3.0, valinit=self.params["Rb"])
        self.sl_Rt = Slider(ax_Rt, 'R Top', 0.01, 3.0, valinit=self.params["Rt"])
        self.sl_L  = Slider(ax_L,  'Layers', 5, 80, valinit=self.params["layers"], valstep=1)
        self.sl_H  = Slider(ax_H,  'Height', 0.1, 3.0, valinit=self.params["Hc"])

        for s in [self.sl_Rb, self.sl_Rt, self.sl_L, self.sl_H]:
            s.on_changed(self.update_wrapper)

        # Control Panel (Right Side)
        # Mode
        ax_mode = plt.axes([0.8, 0.75, 0.15, 0.12])
        self.rad_mode = RadioButtons(ax_mode, ('Curved', 'Straight'), active=0)
        self.rad_mode.on_clicked(self.set_mode)
        ax_mode.set_title("Geometry Mode")

        # Profile
        ax_prof = plt.axes([0.8, 0.55, 0.15, 0.15])
        self.rad_prof = RadioButtons(ax_prof, ('Exponential', 'Linear', 'Inverse Exp'), active=0)
        self.rad_prof.on_clicked(self.set_profile)
        ax_prof.set_title("Bowl Profile")

        # SST View
        ax_view = plt.axes([0.8, 0.35, 0.15, 0.15])
        self.rad_view = RadioButtons(ax_view,
                                     ('SST Gravity Dilation', 'Beltrami Shear', 'Magnetic Field', 'Geometry Only'), active=2)
        self.rad_view.on_clicked(self.update_wrapper)
        ax_view.set_title("Analysis View")

    def set_mode(self, label):
        self.mode = label
        self.update()

    def set_profile(self, label):
        self.profile = label
        self.update()

    def update_wrapper(self, val=None):
        self.update()

    def update(self):
        self.ax.clear()

        # 1. Read Params
        Rb = self.sl_Rb.val
        Rt = self.sl_Rt.val
        n_pairs = int(self.sl_L.val)
        Hc = self.sl_H.val

        # 2. Generate Geometry
        phases = []
        poly_list = []
        colors = ['purple', 'blue', 'green']
        offsets = [0.0, 2*np.pi/3, 4*np.pi/3]

        for i in range(3):
            if not self.phases_active[i]: continue
            pts, seq = generate_bowl_geometry(
                S_DEFAULT, STEP_FWD, STEP_BWD, n_pairs,
                Rb, Rt, Hc, self.profile, self.mode, offsets[i]
            )
            phases.append((pts, colors[i]))
            poly_list.append(pts)

        # 3. Compute Physics (Only if needed)
        view = self.rad_view.value_selected
        if view != 'Geometry Only':
            # Compute on grid
            grid_dims = (self.params["grid_res"], self.params["grid_res"], self.params["grid_res"])
            data = compute_sst_physics(poly_list, grid_dims, self.params["bounds"])

            # Visualize Field
            X, Y, Z = data["X"], data["Y"], data["Z"]

            if view == 'SST Gravity Dilation':
                vals = 1.0 - data["gravity"] # Red = Low G
                mask = vals > 0.02
                cmap = 'inferno'
                scale = 0.15
            elif view == 'Beltrami Shear':
                vals = data["shear"]
                # Normalize shear for coloring
                norm_shear = (vals - vals.min()) / (np.ptp(vals) + 1e-9)
                vals = norm_shear
                mask = vals > 0.2
                cmap = 'magma'
                scale = 0.15
            else: # Magnetic Field
                vals = data["Bz"] # Color by Z-component
                mask = data["mag"] > 0.05
                cmap = 'coolwarm'
                scale = 0.1

            # Subsample for clarity
            sl = (slice(None), slice(None), slice(None))

            self.ax.quiver(
                X[mask], Y[mask], Z[mask],
                data["Bx"][mask], data["By"][mask], data["Bz"][mask],
                length=scale, normalize=True, cmap=cmap, array=vals[mask], alpha=0.6
            )

        # 4. Visualize Geometry
        for pts, col in phases:
            self.ax.plot(pts[:,0], pts[:,1], pts[:,2], c=col, lw=1.5, alpha=0.8)

        self.ax.set_title(f"SawBowl SST: {self.mode} / {self.profile}")
        lim = max(Rb, Rt) * 1.2
        self.ax.set_xlim(-lim, lim)
        self.ax.set_ylim(-lim, lim)
        self.ax.set_zlim(0, Hc * 1.2)
        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    app = SawBowlApp()
    plt.show()