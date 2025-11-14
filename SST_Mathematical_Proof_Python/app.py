# Streamlit app to explore and run SST modules
import json, sys, pathlib, importlib.util, runpy, inspect, re, os
import streamlit as st
import subprocess, time, threading
import streamlit.components.v1 as components
from typing import Any, Optional
import pandas as _pd

try:
    import plotly.graph_objects as go  # noqa: F401
    _HAS_PLOTLY = True
except Exception:
    _HAS_PLOTLY = False

APP_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = APP_DIR / ""
INDEX_FILE = APP_DIR / "module_index.json"

# Ensure SST source directory is importable if needed
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

st.set_page_config(page_title="SST Explorer", layout="wide")

@st.cache_data(show_spinner=False)
def load_index():
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"<<Error reading file: {e}>>"

def load_module_from_path(abs_path: pathlib.Path):
    """Load a Python module from an absolute path without relying on packages."""
    spec = importlib.util.spec_from_file_location(abs_path.stem, abs_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, "Could not create module loader"
    spec.loader.exec_module(mod)
    return mod

def nice_name(rel_path: str) -> str:
    return rel_path.replace("\\\\", "/")

def _sanitize_rel_key(rel: str) -> str:
    """Sanitize a path string for use in Streamlit widget keys."""
    return rel.replace("/", "_").replace("\\", "_").replace(" ", "_")

# ---- Process & logging helpers ----
if "proc_map" not in st.session_state:
    st.session_state["proc_map"] = {}   # key -> subprocess.Popen
if "log_map" not in st.session_state:
    st.session_state["log_map"] = {}    # key -> list[str]
if "auto_scroll" not in st.session_state:
    st.session_state["auto_scroll"] = True
if "start_time_map" not in st.session_state:
    st.session_state["start_time_map"] = {}  # key -> epoch float for asset discovery
if "log_poll_until" not in st.session_state:
    st.session_state["log_poll_until"] = {}  # key -> epoch until which to keep polling for logs
if "plotly_active" not in st.session_state:
    st.session_state["plotly_active"] = None

def _script_key(rel: str) -> str:
    return rel.replace("\\\\","/")

def _is_running(key: str) -> bool:
    p = st.session_state["proc_map"].get(key)
    return bool(p) and (p.poll() is None)

# ---- Thread-safe log buffering (avoid session_state in threads) ----
_GLOBAL_LOGS: dict[str, list[str]] = {}
_GLOBAL_LOGS_LOCK = threading.Lock()

def _mark_poll_window(key: str, seconds: float = 2.0):
    st.session_state["log_poll_until"][key] = time.time() + seconds

def _needs_polling(key: str) -> bool:
    return time.time() < st.session_state["log_poll_until"].get(key, 0.0)

def _append_log(key: str, text: str):
    """Append a log line in a thread-safe module buffer (not session_state)."""
    with _GLOBAL_LOGS_LOCK:
        _GLOBAL_LOGS.setdefault(key, []).append(text)

def _drain_logs_to_session(key: str) -> bool:
    """Move any pending buffered logs for a key into session_state for UI rendering."""
    # Ensure session state container exists
    if "log_map" not in st.session_state:
        st.session_state["log_map"] = {}
    with _GLOBAL_LOGS_LOCK:
        pending = _GLOBAL_LOGS.pop(key, [])
    if pending:
        st.session_state["log_map"].setdefault(key, []).extend(pending)
        _mark_poll_window(key)
        return True
    return False

def _launch_script(abs_path: pathlib.Path, extra_args: Optional[list[str]] = None, pre_stdin: Optional[str] = None):
    key = _script_key(str(abs_path.relative_to(SRC_DIR)))
    # Ensure buffer
    st.session_state["log_map"][key] = []
    # Record start time for asset discovery
    st.session_state["start_time_map"][key] = time.time()
    _mark_poll_window(key)
    # Start subprocess with realtime stdout+stderr
    cmd = [sys.executable, "-u", str(abs_path)] + (extra_args or [])
    try:
        p = subprocess.Popen(
            cmd,
            cwd=str(abs_path.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:
        _append_log(key, f"<<launch error: {e}>>")
        return key
    st.session_state["proc_map"][key] = p
    # Optionally prime stdin
    try:
        if pre_stdin and p.stdin and p.poll() is None:
            p.stdin.write(pre_stdin + ("" if pre_stdin.endswith("\n") else "\n"))
            p.stdin.flush()
    except Exception as e:
        _append_log(key, f"<<stdin prime error: {e}>>")

    def _reader():
        try:
            for line in p.stdout:
                _append_log(key, line.rstrip("\n"))
        except Exception as e:
            _append_log(key, f"<<reader error: {e}>>")
        finally:
            rest = p.stdout.read()
            if rest:
                for ln in rest.splitlines():
                    _append_log(key, ln)
            rc = p.poll()
            _append_log(key, f"<<process exited with code {rc}>>")

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    return key

def _send_stdin(key: str, text: str):
    p = st.session_state["proc_map"].get(key)
    if p and p.poll() is None and p.stdin:
        try:
            p.stdin.write(text + "\n")
            p.stdin.flush()
        except Exception as e:
            _append_log(key, f"<<stdin error: {e}>>")

def _stop_script(key: str):
    p = st.session_state["proc_map"].get(key)
    if not p: 
        return
    try:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()
    except Exception as e:
        _append_log(key, f"<<terminate error: {e}>>")

# ---- Discovery helpers ----
def discover_py_files_recursively(root: pathlib.Path) -> list[str]:
    """Return relative paths (to SRC_DIR) of all *.py under root, excluding app and typical junk."""
    skip_dirs = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache"}
    rels = []
    for p in root.rglob("*.py"):
        if p.name == "app.py":
            continue
        parts = set(p.parts)
        if parts & skip_dirs:
            continue
        try:
            rels.append(str(p.relative_to(SRC_DIR)))
        except ValueError:
            # Not under SRC_DIR
            continue
    return sorted(set(rels))

def _list_assets_since(folder: pathlib.Path, since_epoch: float):
    """List image/HTML assets in folder modified at/after since_epoch."""
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.html", "*.csv", "*.json"]
    assets = []
    for pat in patterns:
        for f in folder.glob(pat):
            try:
                mtime = f.stat().st_mtime
            except OSError:
                continue
            if mtime >= since_epoch:
                assets.append((f, mtime))
    assets.sort(key=lambda t: t[1], reverse=True)
    return [f for f, _ in assets]

def _maybe_auto_rerun(name: str, interval_sec: float = 1.0):
    """
    Lightweight periodic rerun without external plugins.
    Triggers st.rerun()/experimental_rerun at most once per interval.
    """
    flag = f"__auto_rerun_{name}_last"
    now = time.time()
    last = st.session_state.get(flag, 0.0)
    if now - last >= interval_sec:
        st.session_state[flag] = now
        try:
            # Prefer modern API when available
            if hasattr(st, "rerun"):
                st.rerun()
            else:
                st.experimental_rerun()
        except Exception:
            # Ignore if rerun not permitted in this context
            pass

def sidebar_summary(idx):
    st.sidebar.header("SST Explorer")
    st.sidebar.write(f"Discovered **{len(idx)}** Python files")
    only_st = st.sidebar.checkbox("Only modules that import Streamlit", value=False)
    return [m for m in idx if (not only_st or m.get("imports_streamlit"))]

# ---- Plotly detection and rendering ----
_PLOTLY_FN_CANDIDATES = (
    "st_app",
    "plotly_app",
    "plotly_view",
    "build_plotly",
    "get_plotly_figure",
    "get_fig",
    "plot",
    "render_plotly",
)

def _detect_plotly_entry(mod: Any) -> Optional[str]:
    for name in _PLOTLY_FN_CANDIDATES:
        if hasattr(mod, name) and callable(getattr(mod, name)):
            return name
    return None

def _file_mentions_plotly(abs_path: pathlib.Path) -> bool:
    try:
        txt = read_text(abs_path)
        return ("plotly" in txt.lower())
    except Exception:
        return False

def render_plotly_inline(abs_path: pathlib.Path):
    if not _HAS_PLOTLY:
        st.error("plotly is not installed in this environment.")
        return
    try:
        mod = load_module_from_path(abs_path)
    except Exception as e:
        st.exception(e)
        return
    entry = _detect_plotly_entry(mod)
    try:
        if entry == "st_app":
            mod.st_app()
            return
        if entry:
            obj = getattr(mod, entry)()
        else:
            # Try common names in order
            for name in ("get_plotly_figure", "get_fig", "build_plotly", "plot"):
                if hasattr(mod, name):
                    obj = getattr(mod, name)()
                    break
            else:
                st.warning("No Plotly entry found. Expose st_app() or a function returning a plotly Figure.")
                return
        # Render results
        if isinstance(obj, list):
            for i, it in enumerate(obj):
                try:
                    st.plotly_chart(it, width='stretch')
                except Exception:
                    st.write(f"[item {i}] {type(it)}")
        else:
            st.plotly_chart(obj, width='stretch')
    except Exception as e:
        st.exception(e)

def home_tab(filtered_idx):
    st.title("SST Streamlit Explorer")
    st.write(
        "Browse and run modules from **SST_Mathematical_Proof_Python**. "
        "To make a file runnable as a page, add an entrypoint like `st_app()` or `main()`."
    )
    st.subheader("Discovered modules")
    for m in filtered_idx:
        with st.expander(nice_name(m["path"])):
            st.caption("Imports Streamlit: **{}** · Candidate: **{}**".format(
                "yes" if m.get("imports_streamlit") else "no", m.get("candidate") or "—"
            ))
            if m.get("module_doc"):
                st.write(m["module_doc"])
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Functions**")
                for f in m["functions"][:24]:
                    req = f.get("required_pos_args", 0)
                    st.write(f"- `{f['name']}` (requires {req} args)")
            with cols[1]:
                st.markdown("**Classes**")
                for c in m["classes"][:24]:
                    st.write(f"- `{c['name']}`")

def module_runner_tab(idx):
    st.header("Module Runner / Script Runner")
    items = [m["path"] for m in idx]
    choice = st.selectbox("Choose a module", items, index=0 if items else None)
    if not choice:
        return
    selected = next(m for m in idx if m["path"] == choice)
    st.write(f"**Selected:** `{choice}`")
    rel = selected["path"]
    abs_path = SRC_DIR / rel
    st.code(read_text(abs_path)[:2000] + ("\n... (truncated)" if abs_path.stat().st_size > 2000 else ""), language="python")

    candidate = selected.get("candidate")
    colA, colB, colC = st.columns(3)

    # --- Entrypoint runner (same-process import) ---
    with colA:
        st.subheader("Entrypoint (inline)")
        st.caption("Runs `st_app()`, `main()`, or `app()` inside this Streamlit process, if present.")
        if st.button("Run module entrypoint" + (f" `{candidate}`" if candidate else ""), disabled=not candidate):
            try:
                mod = load_module_from_path(abs_path)
                func = None
                if candidate and hasattr(mod, candidate):
                    func = getattr(mod, candidate)
                elif hasattr(mod, "st_app"):
                    func = getattr(mod, "st_app")
                elif hasattr(mod, "main"):
                    func = getattr(mod, "main")
                elif hasattr(mod, "app"):
                    func = getattr(mod, "app")
                if callable(func):
                    func()
                else:
                    st.warning("No callable entrypoint found.")
            except Exception as e:
                st.exception(e)
        if not candidate and not any(hasattr(load_module_from_path(abs_path), name) for name in ("st_app","main","app")):
            st.info("No inline entrypoint found in this module. Use the Script Runner on the right; any new images/HTML saved by the script will appear below.")

    # --- Script runner (subprocess) with live logs ---
    with colB:
        st.subheader("Run as Script (subprocess)")
        st.caption("Launches `python -u <file>.py` and streams stdout/stderr below. Works even without a `main()`.")
        key = _script_key(rel)
        argrow = st.columns(3)
        args_str = argrow[0].text_input("Args", key="args_"+key, placeholder="e.g. exact_closure")
        prein_str = argrow[1].text_input("Pre-send stdin", key="prein_"+key, placeholder="e.g. y")
        argrow[2].caption("Optional arguments and first input lines")
        cols = st.columns(3)
        if cols[0].button("▶️ Start script", key="start_"+key):
            extra = [s for s in (args_str or "").split() if s] or None
            _launch_script(abs_path, extra_args=extra, pre_stdin=(prein_str or None))
        if cols[1].button("⏹ Stop", key="stop_"+key, disabled=not _is_running(key)):
            _stop_script(key)
        clear_req = cols[2].button("🧹 Clear logs", key="clear_"+key)
        if clear_req:
            st.session_state["log_map"][key] = []

        with st.expander("Send stdin (optional)"):
            send_txt = st.text_input("Line to send", key="stdin_"+key)
            if st.button("Send", key="send_"+key, disabled=not _is_running(key)):
                _send_stdin(key, send_txt or "")

        if _is_running(key) or _needs_polling(key):
            _maybe_auto_rerun("module_"+key, interval_sec=1.0)

        # Drain any background logs to session_state before rendering
        _drain_logs_to_session(key)
        logs = "\n".join(st.session_state["log_map"].get(key, []))
        st.checkbox("Auto-scroll", key="auto_scroll")
        st.text_area("Logs", value=logs, height=300, key="logsbox_"+key)

        # Asset preview for scripts (images/HTML created since start)
        st.markdown("**New assets (since start):**")
        since = st.session_state["start_time_map"].get(key, 0.0)
        assets = _list_assets_since(abs_path.parent, since) if since else []
        if not assets:
            st.caption("No new assets detected yet.")
        else:
            for asset in assets[:12]:
                if asset.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                    st.image(str(asset), caption=asset.name, width='stretch')
                elif asset.suffix.lower() == ".svg":
                    try:
                        svg_text = asset.read_text(encoding="utf-8", errors="ignore")
                        components.html(svg_text, height=300, scrolling=True)
                    except Exception:
                        st.write(f"[SVG] {asset.name}")
                elif asset.suffix.lower() == ".html":
                    try:
                        html_text = asset.read_text(encoding="utf-8", errors="ignore")
                        components.html(html_text, height=360, scrolling=True)
                    except Exception:
                        st.write(f"[HTML] {asset.name}")
                elif asset.suffix.lower() == ".csv":
                    try:
                        df_prev = _pd.read_csv(asset)
                        st.dataframe(df_prev.head(50))
                        st.download_button("Download CSV", data=asset.read_bytes(), file_name=asset.name, mime="text/csv", key="dl_mod_"+asset.name)
                    except Exception:
                        st.write(f"[CSV] {asset.name}")
                elif asset.suffix.lower() == ".json":
                    try:
                        st.code((asset.read_text(encoding="utf-8", errors="ignore"))[:5000])
                        st.download_button("Download JSON", data=asset.read_bytes(), file_name=asset.name, mime="application/json", key="dlm_json_"+asset.name)
                    except Exception:
                        st.write(f"[JSON] {asset.name}")
            if len(assets) > 12:
                st.caption(f"... and {len(assets)-12} more")

    # --- Plotly inline renderer ---
    with colC:
        st.subheader("Plotly Renderer (inline)")
        if _file_mentions_plotly(abs_path):
            if st.button("Render Plotly inline", key="plotly_"+rel.replace("/","_")):
                render_plotly_inline(abs_path)
        else:
            st.caption("No obvious Plotly usage detected in file.")

def function_explorer_tab(idx):
    st.header("Function Explorer")
    flat = []
    for m in idx:
        for f in m["functions"]:
            flat.append((m, f))
    if not flat:
        st.info("No functions found.")
        return
    labels = [f"{nice_name(m['path'])} :: {f['name']} (req={f.get('required_pos_args',0)})" for (m,f) in flat]
    i = st.selectbox("Pick a function", range(len(flat)), format_func=lambda k: labels[k])
    m, f = flat[i]
    rel = m["path"]
    abs_path = SRC_DIR / rel
    st.write(f"**Module:** `{rel}`")
    st.write(f"**Function:** `{f['name']}` · requires **{f.get('required_pos_args',0)}** positional args")
    if f.get("doc"):
        st.code(f["doc"])
    if f.get("required_pos_args",0) == 0 and st.button("Run this function"):
        try:
            mod = load_module_from_path(abs_path)
            fn = getattr(mod, f["name"], None)
            if callable(fn):
                out = fn()
                if out is not None:
                    st.write("Return value:")
                    st.write(out)
            else:
                st.warning("Function not found or not callable at runtime.")
        except Exception as e:
            st.exception(e)
    else:
        st.caption("Add default arguments to make it runnable here.")

def code_viewer_tab(idx):
    st.header("Code Viewer")
    files = [m["path"] for m in idx]
    rel = st.selectbox("Choose a file", files)
    if not rel: return
    abs_path = SRC_DIR / rel
    st.code(read_text(abs_path), language="python")

def script_gallery_tab(all_paths):
    st.header("Script Gallery (recursive)")
    st.caption("Run any discovered Python script. Logs stream live; images/HTML created in the script folder are displayed automatically.")
    q = st.text_input("Filter by path substring", "")
    paths = [p for p in all_paths if (q.lower() in p.lower())] if q else all_paths
    if not paths:
        st.info("No scripts match the current filter.")
        return
    for idx, rel in enumerate(paths):
        abs_path = SRC_DIR / rel
        key = _script_key(rel)
        sanitized_rel = _sanitize_rel_key(rel)
        safe_key = f"{idx}_{sanitized_rel}"
        with st.expander(nice_name(rel), expanded=False):
            cols = st.columns(4)
            if cols[0].button("▶️ Start", key="gal_start_"+safe_key):
                _launch_script(abs_path)
            if cols[1].button("⏹ Stop", key="gal_stop_"+safe_key, disabled=not _is_running(key)):
                _stop_script(key)
            if cols[2].button("🧹 Clear logs", key="gal_clear_"+safe_key):
                st.session_state["log_map"][key] = []
            # Status display
            proc = st.session_state["proc_map"].get(key)
            status = "running" if _is_running(key) else (f"exit {proc.returncode}" if proc else "idle")
            cols[3].markdown(f"**Status:** {status}")
            if _is_running(key) or _needs_polling(key):
                _maybe_auto_rerun("gal_"+key, interval_sec=1.0)
            with st.expander("Args / Pre-input"):
                args_g = st.text_input("Args", value="", key="gal_args_"+safe_key, placeholder="e.g. exact_closure")
                prein_g = st.text_area("Pre-send stdin", value="", key="gal_prein_"+safe_key, placeholder="lines to send on start")
                if st.button("Start with args", key="gal_start_args_"+safe_key):
                    extra = [s for s in (args_g or "").split() if s] or None
                    _launch_script(abs_path, extra_args=extra, pre_stdin=(prein_g or None))
            # Drain any background logs to session_state before rendering
            _drain_logs_to_session(key)
            logs = "\n".join(st.session_state["log_map"].get(key, []))
            st.text_area("Logs", value=logs, height=180, key="gal_logs_"+safe_key)
            with st.expander("Send stdin (optional)"):
                send_txt_g = st.text_input("Line to send", key="stdin_gal_"+safe_key)
                if st.button("Send (gallery)", key="send_gal_"+safe_key, disabled=not _is_running(key)):
                    try:
                        p = st.session_state["proc_map"].get(key)
                        if p and p.poll() is None and p.stdin:
                            p.stdin.write((send_txt_g or "") + "\n")
                            p.stdin.flush()
                    except Exception as e:
                        _append_log(key, f"<<stdin error: {e}>>")
            st.markdown("**New assets (since start):**")
            since = st.session_state["start_time_map"].get(key, 0.0)
            assets = _list_assets_since(abs_path.parent, since) if since else []
            if not assets:
                st.caption("No new assets detected yet.")
            else:
                for asset in assets[:12]:
                    if asset.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                        st.image(str(asset), caption=asset.name, width='stretch')
                    elif asset.suffix.lower() == ".svg":
                        try:
                            svg_text = asset.read_text(encoding="utf-8", errors="ignore")
                            components.html(svg_text, height=300, scrolling=True)
                        except Exception:
                            st.write(f"[SVG] {asset.name}")
                    elif asset.suffix.lower() == ".html":
                        try:
                            html_text = asset.read_text(encoding="utf-8", errors="ignore")
                            components.html(html_text, height=360, scrolling=True)
                        except Exception:
                            st.write(f"[HTML] {asset.name}")
                    elif asset.suffix.lower() == ".csv":
                        try:
                            df_prev = _pd.read_csv(asset)
                            st.dataframe(df_prev.head(50))
                            st.download_button("Download CSV", data=asset.read_bytes(), file_name=asset.name, mime="text/csv", key="dlg_csv_"+safe_key+"_"+asset.name)
                        except Exception:
                            st.write(f"[CSV] {asset.name}")
                    elif asset.suffix.lower() == ".json":
                        try:
                            st.code((asset.read_text(encoding="utf-8", errors="ignore"))[:5000])
                            st.download_button("Download JSON", data=asset.read_bytes(), file_name=asset.name, mime="application/json", key="dlg_json_"+safe_key+"_"+asset.name)
                        except Exception:
                            st.write(f"[JSON] {asset.name}")
                if len(assets) > 12:
                    st.caption(f"... and {len(assets)-12} more")

def search_tab(idx):
    st.header("Search")
    q = st.text_input("Keyword or regex")
    if not q:
        st.info("Enter a search query.")
        return
    results = []
    for m in idx:
        rel = m["path"]
        text = read_text(SRC_DIR / rel)
        try:
            for match in re.finditer(q, text, flags=re.IGNORECASE):
                start = max(0, match.start()-80)
                end = min(len(text), match.end()+80)
                snippet = text[start:end].replace("\\n","↩")
                results.append((rel, snippet))
                if len(results) >= 200:
                    break
        except re.error as e:
            st.error(f"Invalid regex: {e}")
            return
    st.write(f"Found **{len(results)}** matches")
    for rel, snip in results:
        with st.expander(rel):
            st.write(snip)

tabs = st.tabs(["🏠 Home","▶️ Module/Script Runner","🖼 Script Gallery","⚡ Plotly Gallery","🧲 Rodin 3D","🌀 Saw Coil 3D","🔎 Function Explorer","📄 Code Viewer","🔍 Search"])

idx = load_index()
filtered_idx = sidebar_summary(idx)

with tabs[0]:
    home_tab(filtered_idx)
with tabs[1]:
    module_runner_tab(filtered_idx)
indexed_paths = [m["path"] for m in idx]
discovered_paths = discover_py_files_recursively(SRC_DIR)
all_paths = sorted(set(indexed_paths) | set(discovered_paths))
with tabs[2]:
    script_gallery_tab(all_paths)

def plotly_gallery_tab(paths):
    st.header("Plotly Renderer (inline)")
    st.caption("Render modules that expose st_app() or a function returning a plotly Figure.")
    q = st.text_input("Filter by path substring (Plotly Gallery)", "")
    candidates = []
    for rel in paths:
        abs_path = SRC_DIR / rel
        if _file_mentions_plotly(abs_path):
            candidates.append(rel)
    if q:
        candidates = [p for p in candidates if q.lower() in p.lower()]
    if not candidates:
        st.info("No Plotly-capable modules found (by heuristic).")
        return
    for rel in candidates:
        abs_path = SRC_DIR / rel
        with st.expander(nice_name(rel), expanded=False):
            st.code(read_text(abs_path)[:1200] + ("...\n" if abs_path.stat().st_size > 1200 else ""), language="python")
            mounted = st.session_state.get("plotly_active") == rel
            cols = st.columns(2)
            if not mounted:
                if cols[0].button("Render", key="plt_render_"+rel.replace("/","_")):
                    st.session_state["plotly_active"] = rel
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()
            else:
                if cols[0].button("Close view", key="plt_close_"+rel.replace("/","_")):
                    st.session_state["plotly_active"] = None
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()
            if mounted:
                st.info("Active Plotly view. Use the sidebar controls defined by this module; adjustments persist.")
                render_plotly_inline(abs_path)

with tabs[3]:
    plotly_gallery_tab(all_paths)
with tabs[4]:
    st.header("Rodin + Dipole Rings (embedded)")
    try:
        rodin_mod = load_module_from_path(SRC_DIR / "rodin_plotly_app.py")
        if hasattr(rodin_mod, "st_app") and callable(getattr(rodin_mod, "st_app")):
            rodin_mod.st_app()
        else:
            st.error("rodin_plotly_app.py does not expose st_app().")
    except Exception as e:
        st.exception(e)
with tabs[5]:
    st.header("Saw-Shape Coil (embedded)")
    try:
        saw_mod = load_module_from_path(SRC_DIR / "sawshape_plotly_app.py")
        if hasattr(saw_mod, "st_app") and callable(getattr(saw_mod, "st_app")):
            saw_mod.st_app()
        else:
            st.error("sawshape_plotly_app.py does not expose st_app().")
    except Exception as e:
        st.exception(e)
with tabs[6]:
    function_explorer_tab(filtered_idx)
with tabs[7]:
    code_viewer_tab(filtered_idx)
with tabs[8]:
    search_tab(filtered_idx)

def _sanitize_rel_key(rel: str) -> str:
    """Sanitize a path string for use in Streamlit keys."""
    return rel.replace('/', '_').replace('\\', '_').replace(' ', '_')