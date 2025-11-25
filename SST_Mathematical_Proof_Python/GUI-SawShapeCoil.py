import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, TextBox, RadioButtons
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('TkAgg')

# --- 1. SST CORE INTEGRATION ---
try:
    import sstbindings
    # Use the wire_grid kernel for polyline performance
    from sstbindings import biot_savart_wire_grid, SSTGravity
    HAS_SST = True
    print("SUCCESS: SST C++ Bindings loaded (Saw-Coil Mode).")
except ImportError:
    HAS_SST = False
    print("WARNING: 'sstbindings' not found. Using slow Python fallback.")

# --- SST Constants ---
V_SWIRL = 1.09384563e6  # m/s
OMEGA_DEFAULT = 10.9e6  # Hz
B_SAT_DEFAULT = 5.0     # Tesla

# --- PRESETS ---
coil_configs = [
    (40, 11, -9), (34, 11, 7), (30, 11, 3), (32, 13, 9),
    (28, 11, 7), (28, 11, -9), (34, 15, -13), (80, 33, -27),
]
preset_labels = [f"N={c[0]}, +{c[1]}, {c[2]}" for c in coil_configs]

params = {
    "coil_corners": coil_configs[0][0],
    "skip_forward": coil_configs[0][1],
    "skip_backward": coil_configs[0][2],
    "num_layers": 1,
    "layer_spacing": 0.15,
    "grid_dims": (13, 13, 13), # Increased default for better gradients
    "x_min": -2.0, "x_max": 2.0,
    "y_min": -2.0, "y_max": 2.0,
    "z_min": -1.0, "z_max": 1.0,
}

def generate_alternating_skip_sequence(corners, step_even, step_odd, radius=1.0, z_layer=0.0, angle_offset=0.0):
    sequence = []
    current = 1
    toggle = True
    for _ in range(corners + 1):
        sequence.append(current)
        step = step_even if toggle else step_odd
        current = (current + step - 1) % corners + 1
        toggle = not toggle
    angles = np.linspace(0, 2*np.pi, corners, endpoint=False) - np.pi/2
    positions = [
        (radius*np.cos(angles[i%corners] + angle_offset),
         radius*np.sin(angles[i%corners] + angle_offset),
         z_layer)
        for i in sequence
    ]
    return {"sequence": sequence, "positions": positions}

def get_wire_arrows(all_positions):
    arrows = []
    for i in range(len(all_positions)-1):
        p0 = np.array(all_positions[i])
        p1 = np.array(all_positions[i+1])
        v = p1-p0
        if v[2] < 0:
            v = -v
        arrows.append((tuple(p0), tuple(v)))
    return arrows

# --- 2. HYBRID PHYSICS ENGINE ---
def compute_fields_hybrid(phases, grid_dims, x_range, y_range, z_range):
    """
    Computes B, Shear, and Gravity using C++ if available, else Python.
    """
    nx, ny, nz = grid_dims
    x = np.linspace(*x_range, nx)
    y = np.linspace(*y_range, ny)
    z = np.linspace(*z_range, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Flatten for processing
    flat_shape = (nx*ny*nz, 3)

    # Initialize Accumulators
    Bx_tot = np.zeros_like(X, dtype=float)
    By_tot = np.zeros_like(Y, dtype=float)
    Bz_tot = np.zeros_like(Z, dtype=float)

    if HAS_SST:
        # --- C++ ACCELERATED PATH ---
        # Flatten grids for C++ input
        Xf, Yf, Zf = X.flatten(), Y.flatten(), Z.flatten()

        for seq, points_list in phases:
            # Convert list of tuples to numpy array for C++
            polyline = np.array(points_list, dtype=float)

            # Call C++ Kernel
            # biot_savart_wire_grid(X, Y, Z, polyline, current) -> (Bx, By, Bz)
            bx, by, bz = biot_savart_wire_grid(Xf, Yf, Zf, polyline, 1.0)

            # Reshape and Accumulate
            Bx_tot += bx.reshape(X.shape)
            By_tot += by.reshape(Y.shape)
            Bz_tot += bz.reshape(Z.shape)

    else:
        # --- PYTHON FALLBACK PATH ---
        print("Computing B-Field (Python Fallback)...")
        arrows = []
        for seq, pos in phases:
            arrows.extend(get_wire_arrows(pos))

        # Use the original logic
        dl = 0.05
        for origin, vector in arrows:
            x0, y0, z0 = origin
            dx, dy, dz = vector
            dl_vec = np.array([dx, dy, dz]) * dl

            RX = X - x0; RY = Y - y0; RZ = Z - z0
            norm_R = np.sqrt(RX**2 + RY**2 + RZ**2) + 1e-8
            factor = 1.0 / (norm_R**3)

            Bx_tot += (dl_vec[1]*RZ - dl_vec[2]*RY) * factor
            By_tot += (dl_vec[2]*RX - dl_vec[0]*RZ) * factor
            Bz_tot += (dl_vec[0]*RY - dl_vec[1]*RX) * factor

    # --- COMPUTE SST METRICS ---
    # 1. Magnitude
    B_mag = np.sqrt(Bx_tot**2 + By_tot**2 + Bz_tot**2) + 1e-9

    # 2. Vorticity (Curl B) for Shear
    # Note: B is already a curl of A, but we need curl(B) for Beltrami check
    # Numerical gradients
    dVz_dy = np.gradient(Bz_tot, y, axis=1)
    dVy_dz = np.gradient(By_tot, z, axis=2)
    dVx_dz = np.gradient(Bx_tot, z, axis=2)
    dVz_dx = np.gradient(Bz_tot, x, axis=0)
    dVy_dx = np.gradient(By_tot, x, axis=0)
    dVx_dy = np.gradient(Bx_tot, y, axis=1)

    Wx = dVz_dy - dVy_dz
    Wy = dVx_dz - dVz_dx
    Wz = dVy_dx - dVx_dy

    # Flatten fields for SST Kernels
    B_flat = np.stack([Bx_tot.flatten(), By_tot.flatten(), Bz_tot.flatten()], axis=-1)
    Curl_flat = np.stack([Wx.flatten(), Wy.flatten(), Wz.flatten()], axis=-1)

    if HAS_SST:
        shear_flat = np.array(SSTGravity.compute_beltrami_shear(B_flat, Curl_flat))
        gravity_flat = np.array(SSTGravity.compute_gravity_dilation(
            B_flat, OMEGA_DEFAULT, V_SWIRL, B_SAT_DEFAULT
        ))
    else:
        # Mock physics for UI testing without library
        shear_flat = B_mag.flatten() * 0.1
        gravity_flat = np.ones_like(shear_flat)

    # Reshape back to grid
    shear_grid = shear_flat.reshape(X.shape)
    gravity_grid = gravity_flat.reshape(X.shape)

    # Return Normalized vectors for plotting + scalar maps
    return {
        "X":X, "Y":Y, "Z":Z,
        "Bx":Bx_tot/B_mag, "By":By_tot/B_mag, "Bz":Bz_tot/B_mag,
        "mag":B_mag,
        "shear":shear_grid,
        "gravity":gravity_grid
    }

def plot_wires(ax, seq, corners, zl, base_color, style='-', alpha=1.0, filter_type='even'):
    angles = np.linspace(0, 2 * np.pi, corners, endpoint=False) - np.pi / 2
    for i in range(len(seq) - 1):
        if (filter_type == "even" and i % 2) or (filter_type == "odd" and i % 2 == 0):
            continue
        a1 = angles[(seq[i] - 1) % corners]
        a2 = angles[(seq[i + 1] - 1) % corners]
        x1, y1 = np.cos(a1), np.sin(a1)
        x2, y2 = np.cos(a2), np.sin(a2)
        z1 = zl + params["layer_spacing"] * (i / (len(seq) - 1))
        z2 = zl + params["layer_spacing"] * ((i + 1) / (len(seq) - 1))
        ax.plot([x1, x2], [y1, y2], [z1, z2], color=base_color, lw=2, linestyle=style, alpha=alpha)


def compute_everything():
    angles = [0, 2*np.pi/3, 4*np.pi/3]
    colors = ['#00ccff', '#33ff66', '#ff3366']
    phases=[]

    # Generate Geometry
    for a in angles:
        sd = generate_alternating_skip_sequence(params["coil_corners"],
                                                params["skip_forward"], params["skip_backward"],
                                                angle_offset=a)
        pos=[]
        for L in range(params["num_layers"]):
            off = L*params["layer_spacing"]
            pos += [(x,y,z+off) for x,y,z in sd["positions"]]
        phases.append((sd["sequence"], pos))

    # Compute Physics
    data = compute_fields_hybrid(
        phases,
        params["grid_dims"],
        (params["x_min"],params["x_max"]),
        (params["y_min"],params["y_max"]),
        (params["z_min"],params["z_max"])
    )

    data["phases"] = phases
    data["colors"] = colors
    return data

def update_plot(*args):
    show_field = cb_status[0]
    show_even = cb_status[1]
    show_odd = cb_status[2]

    # Color Modes
    c_mode = [k for k,v in zip(color_modes, cb_status[3:]) if v]
    mode = c_mode[0] if c_mode else "Default"

    data = gui_state["data"]
    ax.clear()
    ax.set_facecolor(fig.get_facecolor())

    if show_field:
        X, Y, Z = data["X"], data["Y"], data["Z"]
        Bx, By, Bz = data["Bx"], data["By"], data["Bz"]
        mag = data["mag"]
        shear = data["shear"]
        gravity = data["gravity"]

        density = 2
        sl = (slice(None,None,density), slice(None,None,density), slice(None,None,density))

        Xf, Yf, Zf = X[sl].flatten(), Y[sl].flatten(), Z[sl].flatten()
        Bxf, Byf, Bzf = Bx[sl].flatten(), By[sl].flatten(), Bz[sl].flatten()

        # --- COLOR LOGIC ---
        if mode == "By Magnitude":
            vals = mag[sl].flatten()
            # FIX: Use np.ptp(vals) instead of vals.ptp() for NumPy 2.0 compatibility
            norm = (vals - vals.min()) / (np.ptp(vals) + 1e-9)
            colors = plt.cm.viridis(norm)

        elif mode == "By Direction":
            vals = Bzf
            norm = (vals - vals.min()) / (np.ptp(vals) + 1e-9)
            colors = plt.cm.coolwarm(norm)

        elif mode == "SST Gravity Dilation":
            # Invert: Red = Low Gravity (High Effect)
            vals = 1.0 - gravity[sl].flatten()
            # Filter noise
            mask = vals > 0.01
            colors = plt.cm.inferno(vals)

        elif mode == "Beltrami Shear":
            vals = shear[sl].flatten()
            norm = (vals - vals.min()) / (np.ptp(vals) + 1e-9)
            colors = plt.cm.magma(norm)

        else: # Default
            colors = 'teal'

        # Plot Arrows
        # If showing SST metrics, we might want to filter low-relevance arrows
        if mode == "SST Gravity Dilation":
            # Only plot significant gravity reduction zones
            mask = (1.0 - gravity[sl].flatten()) > 0.05
            ax.quiver(Xf[mask], Yf[mask], Zf[mask], Bxf[mask], Byf[mask], Bzf[mask],
                      length=0.1, normalize=True, color=colors[mask], linewidth=0.8)
        else:
            if isinstance(colors, str):
                ax.quiver(Xf, Yf, Zf, Bxf, Byf, Bzf, length=0.07, normalize=True,
                          color=colors, linewidth=0.5, arrow_length_ratio=0.3)
            else:
                # Flatten color array for quiver
                ax.quiver(Xf, Yf, Zf, Bxf, Byf, Bzf, length=0.07, normalize=True,
                          color=colors, linewidth=0.5, arrow_length_ratio=0.3)

    # Plot Geometry
    for (seq, _), color in zip(data["phases"], data["colors"]):
        for layer in range(params["num_layers"]):
            z_layer = layer * params["layer_spacing"]
            if show_even:
                plot_wires(ax, seq, params["coil_corners"], z_layer, '#aa6600', '-', alpha=1.0, filter_type='even')
            if show_odd:
                plot_wires(ax, seq, params["coil_corners"], z_layer, '#880000', '-', alpha=1.0, filter_type='odd')

    ax.set_title(f"SST Analysis: N={params['coil_corners']} Skip=({params['skip_forward']}, {params['skip_backward']})", color='white')
    ax.set_xlim(params["x_min"], params["x_max"])
    ax.set_ylim(params["y_min"], params["y_max"])
    ax.set_zlim(params["z_min"], params["z_max"])
    ax.set_axis_off()
    ax.view_init(elev=88, azim=45)
    fig.canvas.draw_idle()


def on_checkbox(label):
    idx=cb_labels.index(label); cb_status[idx] = not cb_status[idx]; update_plot()

def on_param_submit(label):
    try:
        corners = int(tb_corners.text)
        layers = int(tb_layers.text)
        skip_fwd = int(tb_skip_fwd.text)
        skip_bwd = int(tb_skip_bwd.text)
        spacing = float(tb_spacing.text)
        grid_x = int(tb_xres.text)
        grid_y = int(tb_yres.text)
        grid_z = int(tb_zres.text)
        x_min = float(tb_xmin.text)
        x_max = float(tb_xmax.text)
        y_min = float(tb_ymin.text)
        y_max = float(tb_ymax.text)
        z_min = float(tb_zmin.text)
        z_max = float(tb_zmax.text)

        assert corners > 2 and layers > 0
    except Exception as e:
        print("Invalid input:", e)
        return

    params["coil_corners"] = corners
    params["skip_forward"] = skip_fwd
    params["skip_backward"] = skip_bwd
    params["num_layers"] = layers
    params["layer_spacing"] = spacing
    params["grid_dims"] = (grid_x, grid_y, grid_z)
    params["x_min"], params["x_max"] = x_min, x_max
    params["y_min"], params["y_max"] = y_min, y_max
    params["z_min"], params["z_max"] = z_min, z_max
    gui_state["data"] = compute_everything()
    update_plot()

def on_preset(label):
    i=preset_labels.index(label)
    c,f,b = coil_configs[i]
    tb_corners.set_val(str(c)); tb_skip_fwd.set_val(str(f)); tb_skip_bwd.set_val(str(b))
    on_param_submit(label)

gui_state = {"data": compute_everything()}
cb_labels = ["Field Arrows","Even Segments","Odd Segments","Default","By Magnitude","By Direction", "SST Gravity Dilation", "Beltrami Shear"]
cb_status = [True,True,True,True,False,False,False,False]

fig = plt.figure(figsize=(14,10))
ax = fig.add_subplot(111,projection='3d')
plt.subplots_adjust(left=0.36, right=0.98, bottom=0.28, top=0.98)


# UPDATED RadioButtons for SST
rax_color = plt.axes([0.01, 0.80, 0.25, 0.15])
color_modes = ["Default", "By Magnitude", "By Direction", "SST Gravity Dilation", "Beltrami Shear"]
rb_color = RadioButtons(rax_color, color_modes, active=0)
def on_color_mode(label):
    # Reset color flags (cb_status[3] onwards correspond to modes)
    # Map label to index in cb_status
    # Indices: 0-2 are toggles. 3=Default, 4=Mag, 5=Dir, 6=Grav, 7=Shear
    target_idx = 3 + color_modes.index(label)
    for i in range(3, 8):
        cb_status[i] = (i == target_idx)
    update_plot()
rb_color.on_clicked(on_color_mode)
rax_color.set_title("Analysis Mode")


rax_preset = plt.axes([0.01, 0.60, 0.30, 0.15])
rb = RadioButtons(rax_preset, preset_labels)
rax_preset.set_title("Presets")
rb.on_clicked(on_preset)

plt.axes([0.01,0.30,0.33,0.10]).axis('off')
tb_corners = TextBox(plt.axes([0.13,0.38,0.09,0.04]), "Corners", initial=str(params["coil_corners"]))
tb_layers = TextBox(plt.axes([0.13,0.33,0.09,0.04]), "Layers", initial=str(params["num_layers"]))
tb_skip_fwd = TextBox(plt.axes([0.13,0.28,0.09,0.04]), "Skip Fwd", initial=str(params["skip_forward"]))
tb_skip_bwd = TextBox(plt.axes([0.13,0.23,0.09,0.04]), "Skip Bwd", initial=str(params["skip_backward"]))
tb_spacing = TextBox(plt.axes([0.13,0.18,0.09,0.04]), "Spacing", initial=str(params["layer_spacing"]))
tb_grid = TextBox(plt.axes([0.13,0.13,0.09,0.04]), "Grid N", initial=str(params["grid_dims"]))

tb_xmin = TextBox(plt.axes([0.25,0.38,0.07,0.04]), "Xmin", initial=str(params["x_min"]))
tb_xmax = TextBox(plt.axes([0.25,0.33,0.07,0.04]), "Xmax", initial=str(params["x_max"]))
tb_ymin = TextBox(plt.axes([0.25,0.28,0.07,0.04]), "Ymin", initial=str(params["y_min"]))
tb_ymax = TextBox(plt.axes([0.25,0.23,0.07,0.04]), "Ymax", initial=str(params["y_max"]))
tb_zmin = TextBox(plt.axes([0.25,0.18,0.07,0.04]), "Zmin", initial=str(params["z_min"]))
tb_zmax = TextBox(plt.axes([0.25,0.13,0.07,0.04]), "Zmax", initial=str(params["z_max"]))
tb_xres = TextBox(plt.axes([0.13, 0.08, 0.09, 0.04]), "X res", initial=str(params["grid_dims"][0]))
tb_yres = TextBox(plt.axes([0.13, 0.03, 0.09, 0.04]), "Y res", initial=str(params["grid_dims"][1]))
tb_zres = TextBox(plt.axes([0.25, 0.08, 0.07, 0.04]), "Z res", initial=str(params["grid_dims"][2]))

from matplotlib.widgets import Slider

# XY resolution slider
ax_sl_xy = plt.axes([0.05, 0.5, 0.25, 0.03])
slider_xy = Slider(ax_sl_xy, 'Grid XY', 2, 50, valinit=params["grid_dims"][0], valstep=1)

# Z resolution slider
ax_sl_z = plt.axes([0.05, 0.45, 0.25, 0.03])
slider_z = Slider(ax_sl_z, 'Grid Z', 1, 20, valinit=params["grid_dims"][2], valstep=1)

def on_slider_change(val):
    params["grid_dims"] = (int(slider_xy.val), int(slider_xy.val), int(slider_z.val))
    gui_state["data"] = compute_everything()
    update_plot()

slider_xy.on_changed(on_slider_change)
slider_z.on_changed(on_slider_change)


for tb in [tb_corners, tb_layers, tb_skip_fwd, tb_skip_bwd, tb_spacing,
           tb_xres, tb_yres, tb_zres,
           tb_xmin, tb_xmax, tb_ymin, tb_ymax, tb_zmin, tb_zmax]:
    tb.on_submit(on_param_submit)

update_plot()
plt.show()