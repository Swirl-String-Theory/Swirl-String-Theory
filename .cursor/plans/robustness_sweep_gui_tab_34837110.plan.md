---
name: Robustness sweep GUI tab
overview: Add a new SST Dashboard tab with full CLI coverage via argv passed to a subprocess, ProcessWorker line parsing (v5 tab style), and UI with main_gui KaTeX + v5 structured event cards. Execution is **Option A only** (subprocess); sweep refactor is still useful to export a shared parser for validation/DRY but is not required to avoid the stdin menu when argv is non-empty.
todos:
  - id: refactor-sweep-entry
    content: Extract build_robustness_arg_parser() + run_robustness_sweep_with_args(args) in v10_3 master sweep; slim main() to stdin menu + parse + run (enables GUI import of parser only; subprocess child does not require this for stdin skip)
    status: completed
  - id: gui-tab-module
    content: "Create gui_tabs/tab_knot_robustness_v10_3.py: scrollable controls, argv→subprocess command; ProcessWorker (v5 style); QSplitter: optional status cards, QPlainTextEdit raw log, QWebEngineView KaTeX + appendEvent"
    status: completed
  - id: register-tab
    content: Import and addTab in sst_dashboard_app.py
    status: completed
isProject: false
---

# Knot robustness v10.3 master sweep — dashboard tab

## Context

- Tabs are registered in `[SST_Dashboard/sst_dashboard_app.py](c:/workspace/projects/SSTcore/SST_Dashboard/sst_dashboard_app.py)` via `self.tabs.addTab(...)`, following the same pattern as `[SST_Dashboard/gui_tabs/tab_mass_sweep.py](c:/workspace/projects/SSTcore/SST_Dashboard/gui_tabs/tab_mass_sweep.py)` (scrollable form + `QThread` worker + log/progress).
- The sweep script’s **entire** user-facing surface is the argparse block in `[trefoil_closure/sst_knot_candidate_robustness_sweep_v10_3_master_sweep.py](c:/workspace/projects/SSTcore/trefoil_closure/sst_knot_candidate_robustness_sweep_v10_3_master_sweep.py)` (lines ~3674–3730): mode, preset, output/backend/knot fields, grid lists, contact/root/branch options, torch/local-core/auto-compile toggles, CMake build options, extrapolation and layout, parallelism, console log paths, and archive toggles.

## Design choices

1. **Synthetic argv (recommended)**
  Build a `list[str]` from the widgets and call `parser.parse_args(that_list)`. This keeps **one source of truth** for defaults, `choices=`, and types—no hand-maintained `argparse.Namespace` and no drift when the script adds flags.
2. **Small refactor in the sweep script (required for clean GUI launch)**
  Today `main()` does:
  - interactive `prompt_cli_menu_v10()` when `len(sys.argv) == 1` and stdin is a TTY;
  - then `parse_args` and the long global-mutation + execution block.  
   For the GUI we must **never** depend on that stdin branch and should expose a callable entry point.
   **Refactor (minimal):**
  - Extract `def build_robustness_arg_parser() -> argparse.ArgumentParser` containing only the `add_argument` calls (today ~3674–3730).
  - Extract `def run_robustness_sweep_with_args(args: argparse.Namespace) -> None` containing everything from the current `main()` after parsing (global updates + `try`/`finally` log tee + batch execution), starting at the block that today begins with assignments like `EXTRAP_MIN_NINT = int(args.extrap_min_nint)` (~3737).
  - Replace `main()` with:
    - `argv_in = None` + stdin menu **only** when `len(sys.argv) == 1 and sys.stdin.isatty()`;
    - `args = parser.parse_args(argv_in)`;
    - `run_robustness_sweep_with_args(args)`.
     For the **dashboard (Option A)**, the tab builds `argv` and spawns `sys.executable -u <path/to/sst_knot_candidate_robustness_sweep_v10_3_master_sweep.py> ...`; optionally import `build_robustness_arg_parser()` in the GUI to `parse_args` for early validation before spawn. `run_robustness_sweep_with_args` is not called from the dashboard process.
3. **Execution model (Option A — fixed choice)**
  Run the sweep as a **subprocess** (`sys.executable -u <script> ...`) with `cwd` set to `trefoil_closure/` (script parent) so relative paths like `ideal.txt` resolve like CLI. Use a `QThread` worker patterned after `[trefoil_closure/sst_trefoil_v5_gui_extra_tab.py](c:/workspace/projects/SSTcore/trefoil_closure/sst_trefoil_v5_gui_extra_tab.py)` `ProcessWorker`: stdout line-by-line → raw `QPlainTextEdit` + regex-driven **structured events** in the web pane. Env: `PYTHONUNBUFFERED=1`; Windows: `CREATE_NO_WINDOW` as in that file. **Stop** terminates the child process (`terminate()`); nested `ProcessPoolExecutor` workers may linger briefly on Windows (same limitation as v5 tab).
  - Non-empty argv avoids the interactive stdin menu in the child without any GUI-specific change; the refactor remains valuable for sharing the parser and keeping `main()` thin.
  - The sweep’s file console mirror under `output_dir` is unchanged.
4. **Multiprocessing**
  The child Python process owns `ProcessPoolExecutor`; the dashboard has **no shared module globals** with the sweep. Disable **Start** while a run is active to avoid overlapping subprocesses competing for CPU/GPU.

## GUI layout (new module)

Add `[SST_Dashboard/gui_tabs/tab_knot_robustness_v10_3.py](c:/workspace/projects/SSTcore/SST_Dashboard/gui_tabs/tab_knot_robustness_v10_3.py)` with:

- `**QScrollArea`** (or inner `**QTabWidget`** for subsections) so the form stays usable. Suggested groups:
  - **Run / preset**: `mode` (ideal/torus), `preset` (fast/full), `sweep_layout`, `parallel_scope`, `max_workers`.
  - **Knots**: `knot_id`, `knot_list`, `knot_preset`, `external_knotlib` (tooltips = argparse `help` text).
  - **Discretization grids**: editable lines for `n_geom_list`, `n_int_list`, `lambda_list`, `plateau_fracs`, `extra_target_pairs`; optional `max_fourier_mode` (e.g. checkbox “override” + `QSpinBox`, or empty = omit flag).
  - **Physics / solver**: `contact_model`, `root_selection_mode`, `branch_mode`, `emit_v5_logs`, `run_v6_shiftfree_postcheck`, `backend` (`BS_BACKEND_ALLOWED`: auto, local_cpp_scan, torch, numpy).
  - **Build / integration**: checkboxes for `no_torch`, `no_local_sst_core`, `no_auto_compile`, `sstcore_cmake_build`; line edits for `sst_project_root`, `sst_cmake_build_dir`, `sst_cmake_config`.
  - **Extrapolation / archives**: `extrap_min_nint`, `no_v8_extrapolation`, `no_raw_scan_archive`, `no_root_candidate_archive`, `no_master_batch_archive`.
  - **Output / logging**: `output_dir` (browse), `no_console_log`, `console_log` path.
- **Widget mapping** (use radios where there are exactly 2–3 modes if you want literal radio buttons; otherwise `QComboBox` is fine and matches existing dashboard style):
  - Small **choice sets** → `QComboBox` or `QButtonGroup` + `QRadioButton`.
  - **Booleans / `store_true`** → `QCheckBox` (label matches the positive behavior, argv builder adds `--no-*` or omits as needed).
  - **0/1 int flags** (`emit_v5_logs`, `run_v6_shiftfree_postcheck`) → `QCheckBox` or small combo.
- **Actions**: Start / Stop — `terminate()` on the child (v5 pattern). Optional “Copy argv preview” for debugging.
- **Paths:** Resolve `trefoil_closure/sst_knot_candidate_robustness_sweep_v10_3_master_sweep.py` from the SSTcore repo root (dashboard parent). **Optional:** `sys.path` + import only `build_robustness_arg_parser` for pre-flight `parse_args` validation; do not import or run the full sweep in-process.

## UI: KaTeX (main_gui.py style)

Follow `[trefoil_closure/main_gui.py](c:/workspace/projects/SSTcore/trefoil_closure/main_gui.py)`:

- Set `os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"` before creating `QWebEngineView` (stability).
- HTML shell loads **KaTeX 0.16.8** from jsDelivr: `katex.min.css`, `katex.min.js`, `contrib/auto-render.min.js`.
- Use `renderMathInElement` with delimiters `$$` / `$` (display vs inline).
- Dark, readable body styles (align with main_gui: e.g. dark background, Consolas or mixed sans for prose); append new content in a wrapper `div` and call `renderMathInElement` on the **new node** so math in streamed log lines renders (same idea as `appendLog` in main_gui).
- Escape user/process content before passing into `runJavaScript` (backslashes, quotes) or use `json.dumps` for JS string args as in the v5 tab’s `_append_web_event`.

## UI: Structured logging (sst_trefoil_v5_gui_extra_tab.py style)

Follow `[trefoil_closure/sst_trefoil_v5_gui_extra_tab.py](c:/workspace/projects/SSTcore/trefoil_closure/sst_trefoil_v5_gui_extra_tab.py)`:

- **Split view:** (1) **Raw log** — `QPlainTextEdit`, read-only, `QFont("Consolas", 10)`, stylesheet like `_build_terminal_panel` (`#111317` / `#d6d9df`, border `#2d3340`). (2) **Structured pane** — `QWebEngineView` using `build_html_shell`-style layout: optional **formula cards** at top (reuse `FORMULAS_MONITOR` / `FORMULAS_THEOREM` or a shorter v10.3-specific list), then **event cards** with classes `ok` / `warn` / `info` / `err` (colored left border), `event-title`, `event-meta`, `event-raw` (monospace pre-wrap for the original line).
- **JS:** `appendEvent(kind, title, body, raw, meta)` that prepends a card and runs `renderMathInElement` on that card (same pattern as the v5 file’s script block).
- **Python:** Reuse or copy the **regex parsers** (`FIT_RE`, `BACKEND_RE`, `META_RE`, `ROOT_RE`, `TIME_RE`, `BEST_RE`, `THEOREM_RE`, `CHECK_RE`, `CONT_RE`, `BARRIER_RE`, `[WARN]` / `[ERROR]`) — v10.3 master sweep emits the same family of tags; extend regexes only if new log lines appear. Build **HTML bodies** with inline math in `$...$` where helpful (as v5 does for fit/continuation messages). Use `html.escape` for untrusted fragments; pass through `json.dumps` into `appendEvent`.
- **Optional:** **Status cards** (`StatusCard` QFrame) for live fields (`backend`, `knot_id`, `latest_A_K`, `latest_a_star_over_rc`, etc.) updated from parser `values` dicts — same keys as v5 where applicable.

## Dependency / fallback

- `PyQt5.QtWebEngineWidgets` is required for KaTeX view. If import fails, degrade to **QPlainTextEdit-only** and show a short notice (no formula cards).

## Wire-up

- In `[SST_Dashboard/sst_dashboard_app.py](c:/workspace/projects/SSTcore/SST_Dashboard/sst_dashboard_app.py)`: `from gui_tabs.tab_knot_robustness_v10_3 import TabKnotRobustnessV103` (name can be adjusted) and `self.tabs.addTab(TabKnotRobustnessV103(), "Knot robustness v10.3")` (or similar label).

## Testing (manual)

- Launch dashboard; open new tab; run **fast preset** + single `knot_id` with **parallel none** or small worker count; confirm **raw terminal** shows `[META]` / `[FIT]` lines, **structured web pane** gets colored event cards with rendered KaTeX where applicable, and outputs land under chosen `output_dir`.
- Toggle a few `no`_* flags and confirm generated argv (preview or child log header `argv=`).

## Out of scope / follow-ups

- Full **cancel** that terminates `ProcessPoolExecutor` workers cleanly on Windows.
- Auto-refresh of knot preset lists from `expand_knot_tokens` (could add a read-only hint or link to `ideal.txt`).

