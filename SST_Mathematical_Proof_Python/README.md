# SST Streamlit App (Auto‑scaffold)

This app was generated to explore and run modules from **SST_Mathematical_Proof_Python**.

## Quick start

```bash
# 1) (optional) create a venv
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) install deps
pip install -r requirements.txt

# 3) run the app
streamlit run app.py
```

## How it works

- The app loads an index of all `*.py` files under `SST_Mathematical_Proof_Python/`.
- For each module it shows:
  - module docstring
  - functions/classes (with docstrings)
  - whether it imports `streamlit`
  - a **candidate entrypoint** if we detect `st_app`, `st_page`, `streamlit_app`, `dashboard`, `gui`, `app`, `main`, or `run`.
- You can **Run module** (calls the candidate entrypoint if found) or **Run function** (only if it needs no required parameters).
- A **Code Viewer** lets you read source files.
- A **Search** tab finds code by keyword.

> Tip: If you want a file to appear as a runnable page, define one of the entrypoint functions above (e.g. `def st_app(): ...`).

## Directory layout
```
sst_streamlit_app/
├── app.py
├── requirements.txt
├── README.md
├── module_index.json
└── SST_Mathematical_Proof_Python/   # your extracted codebase (not included here by default at runtime)
```
If you're running outside ChatGPT, place the original folder next to `app.py`:
```
sst_streamlit_app/
├── app.py
└── SST_Mathematical_Proof_Python/
    └── ... your files ...
```
