# Streamlit app to explore and run SST modules
import json, sys, pathlib, importlib.util, runpy, inspect
import streamlit as st

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

def sidebar_summary(idx):
    st.sidebar.header("SST Explorer")
    st.sidebar.write(f"Discovered **{len(idx)}** Python files")
    # Quick filters
    only_st = st.sidebar.checkbox("Only modules that import Streamlit", value=False)
    return [m for m in idx if (not only_st or m.get("imports_streamlit"))]

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
    st.header("Module Runner")
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

def function_explorer_tab(idx):
    st.header("Function Explorer")
    # Build a flat list of (module, function)
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
    # Allow running only if zero required args
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
                snippet = text[start:end].replace("\n","↩")
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

tabs = st.tabs(["🏠 Home","▶️ Module Runner","🔎 Function Explorer","📄 Code Viewer","🔍 Search"])

idx = load_index()
filtered_idx = sidebar_summary(idx)

with tabs[0]:
    home_tab(filtered_idx)
with tabs[1]:
    module_runner_tab(filtered_idx)
with tabs[2]:
    function_explorer_tab(filtered_idx)
with tabs[3]:
    code_viewer_tab(filtered_idx)
with tabs[4]:
    search_tab(filtered_idx)