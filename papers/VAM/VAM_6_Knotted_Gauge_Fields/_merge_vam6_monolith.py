# Merge VAM-6 main + section/*.tex + inline vam_appendix_setup + thebibliography from ../references.bib
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"c:/workspace/projects/SwirlStringTheory/papers/VAM/VAM_6_Knotted_Gauge_Fields")
MAIN = ROOT / "VAM-6-Knotted_Gauge_Fields.tex"
BIB = Path(r"c:/workspace/projects/SwirlStringTheory/papers/VAM/references.bib")
APPENDIX_SETUP = Path(
    r"c:/workspace/projects/SwirlStringTheory/docs/template/vam_appendix_setup.sty"
)

ALIASES: dict[str, str] = {}


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
    s = s.replace("{", "").replace("}", "")
    return clean_bib_tex(s)


def bib_http_url(raw: str) -> str:
    if not raw:
        return ""
    raw_n = re.sub(r"\s+", " ", raw).strip()
    m = re.search(r"https?://[^\s}\,]+", raw_n)
    return m.group(0) if m else ""


def format_bibitem(cite_key: str, bib: dict[str, dict[str, str]]) -> str:
    lk = ALIASES.get(cite_key, cite_key)
    if lk not in bib:
        return (
            f"\\bibitem{{{cite_key}}}\n"
            f"\\textbf{{MISSING}}: no entry `{lk}` in references.bib.\n"
        )
    b = bib[lk]
    author = field_to_latex(b.get("author", ""))
    title = field_to_latex(b.get("title", ""))
    journal = field_to_latex(b.get("journal", b.get("booktitle", "")))
    volume = field_to_latex(b.get("volume", ""))
    number = field_to_latex(b.get("number", ""))
    pages = field_to_latex(b.get("pages", ""))
    year = field_to_latex(b.get("year", ""))
    publisher = field_to_latex(b.get("publisher", ""))
    doi = field_to_latex(b.get("doi", ""))
    note = field_to_latex(b.get("note", ""))
    howpublished_raw = b.get("howpublished", "")
    url = bib_http_url(b.get("url", "")) or bib_http_url(howpublished_raw)
    if not url:
        url = bib_http_url(b.get("note", ""))
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


def sanitize_merged_body(s: str) -> str:
    s = s.replace(r"\begin{tabularx}{@{}lll@{}}", r"\begin{tabular}{@{}lll@{}}")
    s = s.replace(r"\end{tabularx}", r"\end{tabular}")
    s = s.replace(r"\omega_\text{obs}", r"\omega_{\text{obs}}")
    s = s.replace(
        r"\omega_\text{drag}^\text{VAM}(r) =",
        r"{\omega_{\text{drag}}}^{\text{VAM}}(r) =",
    )
    s = s.replace("Thorne & Blandford", r"Thorne \& Blandford")
    s = s.replace(
        r"\phi^2/F^{\text{max}}_{\text{\ae}}^2",
        r"\phi^2/(F^{\text{max}}_{\text{\ae}})^2",
    )
    s = s.replace(
        r"F^{\text{max}}_{\text{\ae}}^2)^2",
        r"(F^{\text{max}}_{\text{\ae}})^2)^2",
    )
    return s


def collect_cite_order(tex: str) -> list[str]:
    tex = strip_full_line_comments(tex)
    order: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"\\cite[a-zA-Z]*\{([^}]*)\}", tex):
        for k in re.split(r"\s*,\s*", m.group(1)):
            k = k.strip()
            if not k or k in seen:
                continue
            seen.add(k)
            order.append(k)
    return order


def inline_appendix_setup(main_txt: str) -> str:
    if not APPENDIX_SETUP.exists():
        return main_txt
    setup = APPENDIX_SETUP.read_text(encoding="utf-8").rstrip() + "\n"
    for pat in (
        r"\input{/C:/workspace/projects/SwirlStringTheory/vam_appendix_setup}",
        r"\input{vam_appendix_setup}",
    ):
        if pat in main_txt:
            main_txt = main_txt.replace(pat, setup)
            return main_txt
    main_txt = re.sub(
        r"\\input\{[^}]*vam_appendix_setup[^}]*\}",
        lambda _m: setup,
        main_txt,
        count=1,
    )
    return main_txt


def main() -> None:
    main_txt = MAIN.read_text(encoding="utf-8")
    main_txt = inline_appendix_setup(main_txt)

    input_paths = re.findall(r"\\input\{([^}]+)\}", main_txt)
    # Keep vamstyle as external \input; merge only section/... and appendix sections
    section_inputs = [
        p
        for p in input_paths
        if p.startswith("section/") and "vamstyle" not in p.lower()
    ]
    bodies: list[str] = []
    for rel in section_inputs:
        p = ROOT / f"{rel}.tex"
        if not p.exists():
            raise SystemExit(f"Missing input: {p}")
        bodies.append(p.read_text(encoding="utf-8"))
    merged_body = sanitize_merged_body("\n".join(bodies))

    bib = parse_bib(BIB)
    cite_order = collect_cite_order(main_txt + "\n" + merged_body)

    missing = [k for k in cite_order if ALIASES.get(k, k) not in bib]
    if missing:
        print("WARNING: missing bib keys:", missing)

    bib_lines = ["\\begin{thebibliography}{99}", ""]
    for k in cite_order:
        bib_lines.append(format_bibitem(k, bib))
        bib_lines.append("")
    bib_lines.append("\\end{thebibliography}")

    m_start = re.search(r"\\input\{section/01_Introduction\}", main_txt)
    m_end = re.search(
        r"\\bibliography\{[^}]+\}\s*\n\s*\\bibliographystyle\{[^}]+\}",
        main_txt,
    )
    if not m_start or not m_end:
        raise SystemExit("Could not find section input block or bibliography lines")
    prefix = main_txt[: m_start.start()]
    prefix = re.sub(r"\\usepackage\{doi\}\s*\n", "", prefix)
    if r"\providecommand{\grqq}" not in prefix:
        needle = r"\usepackage[T1]{fontenc}"
        ins = (
            needle
            + "\n\\providecommand{\\glqq}{\\textquotedblleft}\n"
            + "\\providecommand{\\grqq}{\\textquotedblright}"
        )
        if needle in prefix:
            prefix = prefix.replace(needle, ins, 1)
    suffix = main_txt[m_end.end() :]
    new_main = prefix + merged_body + "\n\n" + "\n".join(bib_lines) + suffix

    MAIN.write_text(new_main, encoding="utf-8")
    print("Wrote", MAIN)
    print("Citations:", len(cite_order))


if __name__ == "__main__":
    main()
