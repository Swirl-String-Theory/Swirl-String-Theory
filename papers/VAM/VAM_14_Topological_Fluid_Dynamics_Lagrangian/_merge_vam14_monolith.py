# Merge VAM-14 skeleton: inline \input sections + thebibliography from references.bib
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"c:/workspace/projects/SwirlStringTheory/papers/VAM/VAM_14_Topological_Fluid_Dynamics_Lagrangian")
MAIN_SKELETON = ROOT / "VAM-14-Topological_Fluid_Dynamics_Lagrangian_skeleton.tex"
MAIN_OUT = ROOT / "VAM-14-Topological_Fluid_Dynamics_Lagrangian.tex"
REF_BIB = Path(r"c:/workspace/projects/SwirlStringTheory/papers/VAM/references.bib")
LOCAL_BIB = ROOT / "Topological_Fluid_Dynamic_Lagrangian_In_VAM.bib"

MAIN_SECTIONS = [
    "sections/1-introduction",
    "sections/2-vortex-æther-model",
    "sections/3-vortex-mass-formula",
    "sections/4-topological-vortex-lagrangian",
    "sections/5-conclusion-outlook",
]

APPENDIX_SECTIONS = [
    "sections/Appendix_all",
    "sections/Appendix_deriveFmax",
    "sections/Appendix_PhotonCapacitor",
    "sections/Appendix_orbitals",
    "sections/Appendix_derivingGravitationalConstant",
]

ALIASES: dict[str, str] = {
    "VAM2": "VAM-2",
    "VAM3": "VAM-3",
    "VAM4": "VAM-4",
    "VAM13": "VAM-13",
    "gibbons2002": "Gibbons2002",
    "gibbons2002maximal": "Gibbons2002",
    "moffatt2014helicity": "moffatt_helicity",
}


def strip_full_line_comments(tex: str) -> str:
    return "\n".join(L for L in tex.splitlines() if not L.lstrip().startswith("%"))


def parse_bib(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "@":
            i += 1
            continue
        m = re.match(r"@\s*(\w+)\s*\{\s*([^,\s]+)\s*,", text[i:])
        if not m:
            i += 1
            continue
        key = m.group(2)
        brace_open = text.find("{", i)
        if brace_open < 0:
            i += 1
            continue
        depth = 0
        j = brace_open
        while j < n:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    inner = text[brace_open + 1 : j]
                    entries[key] = parse_bib_fields(inner)
                    i = j + 1
                    break
            j += 1
        else:
            i += 1
    return entries


def merge_bib_files(paths: list[Path]) -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for path in paths:
        if not path.exists():
            continue
        for k, v in parse_bib(path).items():
            if k not in merged:
                merged[k] = v
    return merged


def parse_bib_fields(inner: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    pos = 0
    ln = len(inner)
    while pos < ln:
        m = re.match(r"\s*(\w+)\s*=\s*(\{|\")", inner[pos:])
        if not m:
            pos += 1
            continue
        fname = m.group(1).lower()
        sep = m.group(2)
        start = pos + m.end() - 1
        if sep == "{":
            depth = 0
            k = start
            while k < ln:
                if inner[k] == "{":
                    depth += 1
                elif inner[k] == "}":
                    depth -= 1
                    if depth == 0:
                        val = inner[start + 1 : k]
                        fields[fname] = val.strip()
                        pos = k + 1
                        break
                k += 1
            else:
                break
        else:
            k = start + 1
            while k < ln and inner[k] != '"':
                k += 1
            val = inner[start + 1 : k]
            fields[fname] = val.strip()
            pos = (k + 1) if k < ln else k
        pos = inner.find(",", pos)
        if pos < 0:
            break
    return fields


def clean_bib_tex(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def field_to_latex(s: str) -> str:
    # Do not strip `{}`: bib entries often contain TeX like `\texttt{zenodo.org}`.
    return clean_bib_tex(s)


def field_to_latex_title(s: str) -> str:
    return clean_bib_tex(s)


def bib_http_url(raw: str) -> str:
    if not raw:
        return ""
    raw_n = re.sub(r"\s+", " ", raw).strip()
    m = re.search(r"https?://[^\s}\,]+", raw_n)
    return m.group(0) if m else ""


def resolve_bib_key(lk: str, bib: dict[str, dict[str, str]]) -> str | None:
    if lk in bib:
        return lk
    ll = lk.lower()
    for k in bib:
        if k.lower() == ll:
            return k
    return None


def format_bibitem(cite_key: str, bib: dict[str, dict[str, str]]) -> str:
    lk = ALIASES.get(cite_key, cite_key)
    rk = resolve_bib_key(lk, bib)
    if rk is None:
        return (
            f"\\bibitem{{{cite_key}}}\n"
            f"\\textbf{{MISSING}}: no entry for `{lk}` in merged bibliography.\n"
        )
    b = bib[rk]
    author = field_to_latex(b.get("author", ""))
    title = field_to_latex_title(b.get("title", ""))
    journal = field_to_latex(b.get("journal", b.get("booktitle", "")))
    volume = field_to_latex(b.get("volume", ""))
    number = field_to_latex(b.get("number", ""))
    pages = field_to_latex(b.get("pages", ""))
    year = field_to_latex(b.get("year", ""))
    publisher = field_to_latex(b.get("publisher", ""))
    doi = field_to_latex(b.get("doi", ""))
    note_raw = b.get("note", "")
    note = field_to_latex(note_raw)
    howpublished_raw = b.get("howpublished", "")
    url = bib_http_url(b.get("url", "")) or bib_http_url(howpublished_raw)
    if not url:
        url = bib_http_url(note_raw)
    howpublished_text = ""
    if howpublished_raw and not bib_http_url(howpublished_raw):
        howpublished_text = field_to_latex(howpublished_raw)

    lines = [f"\\bibitem{{{cite_key}}}"]
    if author:
        lines.append(author + ",")
    lines.append(f"\\newblock {title}.")
    tail = []
    if journal:
        j = f"\\textit{{{journal}}}"
        if volume:
            j += f" \\textbf{{{volume}}}"
        if number:
            j += f" ({number})"
        if pages:
            j += f", {pages}"
        if year:
            j += f" ({year})"
        tail.append(j + ".")
    elif publisher and year:
        tail.append(f"\\newblock {publisher}, {year}.")
    elif year:
        tail.append(f"\\newblock {year}.")
    if doi:
        tail.append(f"\\newblock DOI: \\href{{https://doi.org/{doi}}}{{{doi}}}.")
    if url and url not in (f"https://doi.org/{doi}" if doi else ""):
        tail.append(f"\\newblock \\url{{{url}}}.")
    if howpublished_text:
        tail.append(f"\\newblock {howpublished_text}.")
    if note and not note.lower().startswith("urlhttps"):
        tail.append(f"\\newblock {note}.")
    lines.extend(tail)
    return "\n".join(lines) + "\n"


def collect_cite_order(tex: str) -> list[str]:
    tex = strip_full_line_comments(tex)
    order: list[str] = []
    seen_lower: set[str] = set()
    for m in re.finditer(r"\\cite[a-zA-Z]*\{([^}]*)\}", tex):
        for k in re.split(r"\s*,\s*", m.group(1)):
            k = k.strip()
            if not k:
                continue
            kl = k.lower()
            if kl in seen_lower:
                continue
            seen_lower.add(kl)
            order.append(k)
    return order


def sanitize_merged_body(s: str) -> str:
    s = s.replace(r"\rho_\ae", r"\rho_{\text{\ae}}")
    s = s.replace(r"F_\ae", r"F_{\text{\ae}}")
    s = s.replace("Thorne & Blandford", r"Thorne \& Blandford")
    s = s.replace(
        r"\phi^2/F^{\text{max}}_{\text{\ae}}^2",
        r"\phi^2/(F^{\text{max}}_{\text{\ae}})^2",
    )
    return s


def read_section(rel: str) -> str:
    p = ROOT / f"{rel}.tex"
    if not p.exists():
        raise SystemExit(f"Missing {p}")
    return p.read_text(encoding="utf-8")


def main() -> None:
    if not MAIN_SKELETON.exists():
        raise SystemExit(f"Missing skeleton {MAIN_SKELETON}")
    main_txt = MAIN_SKELETON.read_text(encoding="utf-8")

    m_first = re.search(r"\\input\{sections/1-introduction\}", main_txt)
    m_last_main = re.search(r"\\input\{sections/5-conclusion-outlook\}", main_txt)
    m_app = re.search(r"\\appendix", main_txt)
    m_bib = re.search(
        r"\s*\\bibliographystyle\{[^}]+\}\s*\n\s*\\bibliography\{[^}]+\}",
        main_txt,
    )
    if not m_first or not m_last_main or not m_app or not m_bib:
        raise SystemExit("Could not parse VAM-14 skeleton structure.")

    prefix = main_txt[: m_first.start()]
    prefix = re.sub(
        r"\s*\\usepackage\[backend=biber,style=phys\]\{biblatex\}\s*\n\s*\\addbibresource\{[^}]+\}\s*\n",
        "\n",
        prefix,
    )

    main_bodies = [read_section(rel) for rel in MAIN_SECTIONS]
    merged_main = sanitize_merged_body("\n".join(main_bodies))

    mid = main_txt[m_last_main.end() : m_app.start()]

    app_bodies = [read_section(rel) for rel in APPENDIX_SECTIONS]
    merged_app = sanitize_merged_body("\n".join(app_bodies))

    cite_src = prefix + merged_main + mid + merged_app

    bib = merge_bib_files([REF_BIB, LOCAL_BIB])
    cite_order = collect_cite_order(cite_src)

    missing: list[str] = []
    for k in cite_order:
        lk = ALIASES.get(k, k)
        if resolve_bib_key(lk, bib) is None:
            missing.append(k)
    if missing:
        print("WARNING: missing bib keys:", missing)

    bib_lines = ["\\begin{thebibliography}{99}", ""]
    for k in cite_order:
        bib_lines.append(format_bibitem(k, bib))
        bib_lines.append("")
    bib_lines.append("\\end{thebibliography}")

    suffix = main_txt[m_bib.end() :]

    app_header = ""
    for line in main_txt[m_app.start() : m_bib.start()].splitlines():
        if line.strip().startswith("\\appendix"):
            app_header = line.rstrip() + "\n"
            break
    if not app_header:
        app_header = "\\appendix\n"

    new_main = (
        prefix
        + merged_main
        + mid
        + app_header
        + merged_app
        + "\n".join(bib_lines)
        + "\n"
        + suffix
    )

    MAIN_OUT.write_text(new_main, encoding="utf-8")
    print("Wrote", MAIN_OUT)
    print("Citations:", len(cite_order), cite_order)


if __name__ == "__main__":
    main()
