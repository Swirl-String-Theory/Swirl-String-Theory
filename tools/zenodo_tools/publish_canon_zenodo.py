#!/usr/bin/env python3
"""
SST Canon Zenodo publishing: scan local/online versions, push as draft.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from create_zenodo_configs import extract_metadata_from_latex
from render_and_update_zenodo import (
    compile_latex,
    expected_canon_pdf_path,
    format_pdf_doi_diagnostics,
    pdf_doi_matches,
    process_config_file,
    read_doi_from_pdf,
    resolve_pdf_path,
    update_zenodo_metadata,
)
from zenodo_automation import (
    ZenodoAutomation,
    get_been_processed_dir,
    get_repo_root,
    read_token_from_zenodo_py,
    tex_file_relative_path,
)

if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

ROOT_DOI = "10.5281/zenodo.19655881"  # v0.8.0 in the canon family
LATEST_ONLINE_DOI_FALLBACK = "10.5281/zenodo.19682949"  # legacy chain head if no local config
CONCEPT_DOI = "10.5281/zenodo.16934535"  # version-family concept DOI
CANON_CONCEPT_RECID = CONCEPT_DOI.rsplit(".", 1)[-1]  # "16934535"
CANON_SUBTITLE = "Canonical Reference and Research Framework"
ORPHAN_VERSION_PREFIX = "orphan:"

# Pre-v0.8.5 editions (not in canon_edition.py EDITION_CONFIG).
LEGACY_EDITION_CHANGELOG: dict[str, str] = {
    "0.8.2": "Horn/circulation radius, envelope density, highres terminology",
    "0.8.3": "Framed-tube ontology, trefoil closure, particle dictionary, Pauli a_core",
    "0.8.4": "EM–gravity bridge, finite-cell α obstruction, research-track extensions",
    "0.8.5": "Highres conversation audit + CALIBRATED circularity honesty",
    "0.8.6": "Framed self-linking / spinorial lepton ladder (subsec:framed_selflinking_spinorial)",
    "0.8.7": "Z₂ spinstats / CP¹ substrate paragraph + bibliography",
    "0.8.8": "Epistemic/notation audit (P_cal, a_cut, etc.)",
    "0.8.9": "Triadic gravity-response corollary + flame/caustic/shell research-track diagnostics",
    "0.8.10": "vchar/uswirl discipline, delay sign, epistemic relabeling",
    "0.8.11": "Final hygiene: consistent P_cal, EMG/RT notation cleanup",
    "0.8.12": "epistemic relabels, Pauli a_cut, galaxy rhoF caveat",
    "0.8.13": "Relativity emergence ladder, tensor-speed naturalness (c13=0), SR/GR audit research-track",
    "0.8.14": "Two-speed clock discipline, alpha-gate guard, core-torsion impedance-matching lemma",
    "0.8.15": "Lorentz-type swirl-stress (canon) + EM-to-swirl correspondence / SST-44 stress (research track)",
    "0.8.16": "Pressure–optical locking + no-monopole audit + relativity falsifier ladder (+ SST-73 notes)",
    "0.8.17": "T-foliation remark + ropelength/trefoil-α convention + Route-I SST-63/23/56 integration (+ SST-73/63/64/34 bundle); RC2 PDF polish",
    "0.8.18": "Calibration guardrails v2 + resolved-tube v3 (reach/thickness, contact-stress appendix, GW170817/pulsar falsifier bounds)",
}

_HEADER_EDITION_RE = re.compile(r"edition:\s*(.+?)\s*\(been_processed\)", re.IGNORECASE)

_edition_changelog_cache: dict[str, str] | None = None

DEFAULT_CREATORS = [
    {
        "name": "Iskandarani, Omar",
        "affiliation": "Independent Researcher, Groningen, The Netherlands",
        "orcid": "0009-0006-1686-3961",
    }
]


@dataclass
class CanonVersionInfo:
    version: str
    source: str  # 'local' | 'online'
    title: str = ""
    doi: str = ""
    deposit_id: str = ""
    html_url: str = ""
    state: str = ""  # published | draft | local_only
    has_tex: bool = False
    has_pdf: bool = False
    has_config: bool = False
    pdf_doi: str = ""
    pdf_doi_ok: bool = False
    tex_path: Optional[Path] = None
    pdf_path: Optional[Path] = None
    config_path: Optional[Path] = None
    publication_date: str = ""


@dataclass
class VersionStatus:
    version: str
    status: str  # synced | ahead_local | draft_online | online_only | duplicate_doi | missing_config | ready_to_push | ...
    local: Optional[CanonVersionInfo] = None
    online: Optional[CanonVersionInfo] = None
    message: str = ""
    errors: list[str] = field(default_factory=list)
    can_push: bool = False
    can_push_metadata: bool = False
    can_update_config: bool = False
    can_mint_doi: bool = False
    can_render: bool = False


@dataclass
class PushResult:
    version: str
    success: bool
    message: str = ""
    doi: str = ""
    deposit_id: str = ""
    html_url: str = ""
    actions: list[str] = field(default_factory=list)
    api_status: int | None = None
    api_detail: str = ""
    # remint | retry | check_token | reuse_draft | open_zenodo | ""
    suggested_action: str = ""


def classify_zenodo_api_error(
    status: int | None,
    detail: str = "",
    operation: str = "",
) -> tuple[str, str]:
    """
    Map Zenodo HTTP failures to (suggested_action, short_hint).

    suggested_action: remint | retry | check_token | reuse_draft | open_zenodo | ""
    """
    text = (detail or "").lower()
    op = (operation or "").lower()
    if status in (401, 403):
        return "check_token", "Zenodo-token ontbreekt of heeft geen rechten"
    if status == 404 or "not found" in text or "does not exist" in text:
        return "remint", "Deposit/record bestaat niet (meer) — Remint DOI + Config"
    if status == 429 or "rate" in text and "limit" in text:
        return "retry", "Zenodo rate-limit — even wachten en opnieuw"
    if status == 400 and (
        "new version" in text
        or "already exists" in text
        or "draft" in text and "exist" in text
    ):
        return "reuse_draft", "Er bestaat al een draft-versie — refresh en hergebruik/bind"
    if status and status >= 500:
        return "retry", f"Zenodo serverfout HTTP {status} — later opnieuw"
    if op == "create_new_version" and status in (400, 409):
        return "reuse_draft", "Kon geen nieuwe versie maken — mogelijk bestaat er al een draft"
    if status:
        return "open_zenodo", f"Zenodo API HTTP {status}"
    return "", ""


def apply_automation_api_error(
    result: PushResult,
    automation: Optional[ZenodoAutomation],
    fallback_message: str,
) -> PushResult:
    """Attach last Zenodo API error onto PushResult and refine the user message."""
    err = getattr(automation, "last_api_error", None) if automation else None
    if not err:
        if not result.message:
            result.message = fallback_message
        return result
    status = err.get("status")
    detail = err.get("detail") or ""
    operation = err.get("operation") or ""
    result.api_status = status if isinstance(status, int) else None
    result.api_detail = detail
    action, hint = classify_zenodo_api_error(result.api_status, detail, operation)
    result.suggested_action = action
    parts = [fallback_message]
    if result.api_status is not None:
        parts.append(f"HTTP {result.api_status} ({operation})")
    if hint:
        parts.append(hint)
    if detail:
        parts.append(detail[:300])
    result.message = " — ".join(p for p in parts if p)
    return result


def been_processed_root() -> Path:
    return get_been_processed_dir()


_canon_keywords_loader: Callable[[str], list[str]] | None = None


def strip_latex_to_plain(text: str) -> str:
    """Best-effort plain text from canon_edition.py LaTeX notes."""
    plain = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    plain = re.sub(r"\\(?:ref|eqref|S)\{[^}]*\}", "", plain)
    plain = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})?", " ", plain)
    plain = re.sub(r"\$[^$]*\$", "", plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    plain = re.sub(r"^v?\d+\.\d+\.\d+\s+adds\s+", "", plain, flags=re.IGNORECASE)
    return plain


def changelog_from_edition_config(cfg: dict) -> str:
    header = cfg.get("header", "")
    match = _HEADER_EDITION_RE.search(header)
    if match:
        return match.group(1).strip()
    note = cfg.get("note", "")
    if note:
        return strip_latex_to_plain(note)[:240]
    return ""


def get_edition_changelog(refresh: bool = False) -> dict[str, str]:
    """
    Edition blurbs for Zenodo descriptions.

    Merges LEGACY_EDITION_CHANGELOG with canon_edition.py EDITION_CONFIG so new
    been_processed folders (e.g. v0.8.19+) work without editing this file.
    """
    global _edition_changelog_cache
    if _edition_changelog_cache is not None and not refresh:
        return _edition_changelog_cache

    changelog = dict(LEGACY_EDITION_CHANGELOG)
    path = been_processed_root() / "canon_edition.py"
    if path.is_file():
        spec = importlib.util.spec_from_file_location("canon_edition", path)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            edition_config = getattr(mod, "EDITION_CONFIG", {})
            for version, cfg in edition_config.items():
                blurb = changelog_from_edition_config(cfg)
                if blurb:
                    changelog[str(version)] = blurb

    _edition_changelog_cache = changelog
    return changelog


def is_known_canon_version(version: str) -> bool:
    """True if version has changelog metadata or a local main tex file."""
    if version in get_edition_changelog():
        return True
    tex = main_tex(version)
    return tex.is_file()


def latest_canon_version(local: Optional[list[CanonVersionInfo]] = None) -> str:
    """Highest version string from changelog + local been_processed scan."""
    versions = set(get_edition_changelog())
    if local is None:
        local = scan_local_canon_versions()
    versions.update(v.version for v in local if v.has_tex)
    if not versions:
        return "0.8.18"
    return max(versions, key=version_sort_key)


def resolve_latest_head_doi(local: Optional[list[CanonVersionInfo]] = None) -> str:
    """DOI of the newest local edition with config — used to walk Zenodo version chain."""
    if local is None:
        local = scan_local_canon_versions()
    best_key: tuple[int, ...] | None = None
    best_doi = ""
    for entry in local:
        doi = (entry.doi or "").strip()
        if not doi or not entry.has_config:
            continue
        key = version_sort_key(entry.version)
        if best_key is None or key > best_key:
            best_key = key
            best_doi = doi
    return best_doi or LATEST_ONLINE_DOI_FALLBACK


def is_canon_deposit_title(title: str) -> bool:
    """True if a Zenodo title looks like an SST Canon deposit (not other SST papers)."""
    return bool(
        re.search(
            r"swirl[\s\-]*string[\s\-]*theory[\s\-]*canon",
            title or "",
            re.IGNORECASE,
        )
    )


def is_orphan_online_version(version: str) -> bool:
    return (version or "").startswith(ORPHAN_VERSION_PREFIX)


def deposit_belongs_to_canon_family(deposit: dict) -> bool:
    """True if deposit metadata/concept belongs to the SST Canon version family."""
    if not deposit:
        return False
    meta = deposit.get("metadata") or {}
    concept = str(
        deposit.get("conceptrecid")
        or meta.get("conceptrecid")
        or ""
    ).strip()
    if concept == CANON_CONCEPT_RECID:
        return True
    return is_canon_deposit_title(meta.get("title") or deposit.get("title") or "")


def deposit_is_published(deposit: dict) -> bool:
    """True for submitted/published Zenodo deposits (not unsubmitted drafts)."""
    if not deposit:
        return False
    if deposit.get("submitted"):
        return True
    state = str(deposit.get("state") or "").lower()
    return state in ("done", "published")


def resolve_canon_concept_anchor(
    local: Optional[list[CanonVersionInfo]] = None,
    automation: Optional[ZenodoAutomation] = None,
) -> str:
    """
    DOI/recid inside the SST Canon Zenodo family for listing versions.

    Prefer a verified *published* local deposit in the Canon concept.
    Never use a draft as the list anchor (that drops published siblings from
    parent.id search). Never trust the newest local DOI blindly.
    """
    if local is None:
        local = scan_local_canon_versions()

    candidates = sorted(
        [v for v in local if v.has_config and (v.doi or v.deposit_id)],
        key=lambda v: version_sort_key(v.version),
        reverse=True,
    )
    if automation:
        for entry in candidates[:12]:
            deposit_id = (entry.deposit_id or "").strip()
            if not deposit_id:
                continue
            deposit = automation.get_deposit_info(deposit_id, quiet=True)
            if not deposit_belongs_to_canon_family(deposit or {}):
                continue
            if not deposit_is_published(deposit or {}):
                # Drafts must not anchor the version list
                continue
            doi = (entry.doi or "").strip()
            if not doi:
                meta = (deposit or {}).get("metadata") or {}
                doi = (
                    (deposit or {}).get("doi")
                    or meta.get("doi")
                    or ""
                )
            return str(doi or deposit_id)

    return CONCEPT_DOI


def get_canon_keywords(version: str) -> list[str]:
    """Load edition keywords from been_processed/canon_edition.py."""
    global _canon_keywords_loader
    if _canon_keywords_loader is None:
        path = been_processed_root() / "canon_edition.py"
        spec = importlib.util.spec_from_file_location("canon_edition", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load canon_edition from {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _canon_keywords_loader = mod.canon_keywords
    return _canon_keywords_loader(version)


def version_sort_key(version: str) -> tuple[int, ...]:
    try:
        parts = version.lstrip('v').split('.')
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0, 0)


def is_canon_version_dir(name: str) -> bool:
    return bool(re.match(r'^v0\.8\.\d+$', name))


def parse_version_from_title(title: str) -> Optional[str]:
    m = re.search(r'v\s*[-]?\s*0\.8\.(\d+)', title, re.IGNORECASE)
    if m:
        return f"0.8.{m.group(1)}"
    m = re.search(r'Canon[-\s_]*v\s*[-]?\s*0\.8\.(\d+)', title, re.IGNORECASE)
    if m:
        return f"0.8.{m.group(1)}"
    m = re.search(r'v\s*[-]?\s*(\d+\.\d+(?:\.\d+)?)', title, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def parse_version_from_entry(entry: dict) -> Optional[str]:
    meta = entry.get('metadata', entry)
    version_field = meta.get('version', '') or entry.get('version', '')
    if version_field:
        m = re.search(r'0\.8\.\d+', str(version_field))
        if m:
            return m.group(0)
        m = re.search(r'\d+\.\d+(?:\.\d+)?', str(version_field))
        if m:
            return m.group(0)
    return parse_version_from_title(meta.get('title', '') or entry.get('title', ''))


def canon_title(version: str) -> str:
    return f"Swirl-String-Theory Canon v{version} — {CANON_SUBTITLE}"


def zenodo_version_label(version: str) -> str:
    return f"v{version.lstrip('v')}"


def edition_dir(version: str) -> Path:
    return been_processed_root() / f"v{version}"


def main_tex(version: str) -> Path:
    return edition_dir(version) / f"SST_CANON-v{version}.tex"


def config_path(version: str) -> Path:
    return edition_dir(version) / f"SST_CANON-v{version}.zenodo.json"


def read_doi_from_tex(tex_file: Path) -> str:
    try:
        content = tex_file.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return ""
    m = re.search(r'\\newcommand\{\\paperdoi\}\{(10\.5281/zenodo\.\d+)\}', content)
    if m:
        return m.group(1)
    m = re.search(r'10\.5281/zenodo\.\d+', content)
    return m.group(0) if m else ""


def update_doi_in_canon_tex(tex_file: Path, doi: str) -> None:
    content = tex_file.read_text(encoding='utf-8')
    if re.search(r'%!\s*DOI\s*=', content):
        content = re.sub(r'%!\s*DOI\s*=\s*[^\n]+', f'%! DOI = {doi}', content, count=1)
    else:
        content = f'%! DOI = {doi}\n' + content
    # Use * so empty \newcommand{\paperdoi}{} (post-ingest mint-ready) is filled too.
    # Callable replacement avoids re.sub backslash-escape pitfalls.
    newcommand_line = f'\\newcommand{{\\paperdoi}}{{{doi}}}'
    paperdoi_re = re.compile(r'\\newcommand\{\\paperdoi\}\{[^}]*\}')
    if paperdoi_re.search(content):
        content = paperdoi_re.sub(lambda _m: newcommand_line, content, count=1)
    else:
        # Insert after DOI comment if present, else at top.
        m = re.search(r'%!\s*DOI\s*=\s*[^\n]+\n?', content)
        if m:
            insert_at = m.end()
            content = content[:insert_at] + newcommand_line + '\n' + content[insert_at:]
        else:
            content = newcommand_line + '\n' + content
    tex_file.write_text(content, encoding='utf-8')


def read_config_data(version: str) -> dict:
    cfg = config_path(version)
    if not cfg.is_file():
        return {}
    try:
        return json.loads(cfg.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}


def find_duplicate_local_dois(local: list[CanonVersionInfo]) -> dict[str, list[str]]:
    """Map DOI -> list of local version strings that share it."""
    by_doi: dict[str, list[str]] = {}
    for v in local:
        if not v.doi:
            continue
        by_doi.setdefault(v.doi, []).append(v.version)
    return {doi: vers for doi, vers in by_doi.items() if len(vers) > 1}


def deposit_id_known_online(deposit_id: str, online: list[CanonVersionInfo]) -> bool:
    """True if deposit_id appears in the fetched online Canon list."""
    dep = str(deposit_id or "").strip()
    if not dep:
        return False
    return any(str(v.deposit_id) == dep for v in online)


def local_deposit_is_stale(
    version: str,
    local: list[CanonVersionInfo],
    online: list[CanonVersionInfo],
) -> bool:
    """
    True when local config points at a deposit that is gone from Zenodo
    (deleted draft/version) and the edition is not published online.

    Not stale when the same version+DOI appears online (published or draft),
    even if deposit_id is missing from an incomplete online list.
    """
    loc = next((v for v in local if v.version == version), None)
    if not loc or not loc.has_config:
        return False
    online_match = next((v for v in online if v.version == version), None)
    if online_match and online_match.state == "published":
        return False
    cfg = read_config_data(version)
    dep = str(cfg.get("deposit_id") or loc.deposit_id or "").strip()
    doi = str(cfg.get("doi") or loc.doi or "").strip()
    if not dep:
        return False
    if deposit_id_known_online(dep, online):
        return False
    # Same version + DOI still online (draft or published) ⇒ config not stale
    if online_match and doi and online_match.doi and online_match.doi == doi:
        return False
    if doi:
        for on in online:
            if on.version == version and on.doi == doi:
                return False
    return True


def validate_version_for_push(
    version: str,
    local: list[CanonVersionInfo],
    online: list[CanonVersionInfo],
) -> tuple[bool, bool, list[str]]:
    """
    Validate whether a local been_processed version may be pushed to Zenodo.

    Returns:
        (can_push, can_mint_doi, errors)
    """
    errors: list[str] = []
    local_map = {v.version: v for v in local}
    loc = local_map.get(version)
    if not loc:
        return False, False, [f"v{version} niet gevonden in been_processed"]

    online_map = {v.version: v for v in online}
    duplicates = find_duplicate_local_dois(local)
    can_mint_doi = True

    if not loc.has_tex:
        errors.append("Geen .tex bestand aanwezig")
        can_mint_doi = False

    doi = loc.doi.strip()
    if not doi:
        errors.append("Geen DOI in tex — mint eerst een unieke DOI voor deze versie")
        can_mint_doi = True
    elif doi in duplicates and version in duplicates[doi]:
        others = [f"v{v}" for v in duplicates[doi] if v != version]
        errors.append(
            f"DOI {doi} is niet uniek — gedeeld met {', '.join(others)}. "
            f"Elke been_processed versie moet een eigen DOI hebben."
        )
        can_mint_doi = True
    else:
        owner = online_map.get(version)
        if owner and owner.doi and owner.doi != doi:
            cfg = read_config_data(version) if loc.has_config else {}
            if str(cfg.get('deposit_id', '')) != owner.deposit_id:
                errors.append(
                    f"DOI {doi} komt niet overeen met online v{version} ({owner.doi})"
                )
        cfg_deposit = ""
        if loc.has_config:
            cfg_deposit = str(read_config_data(version).get('deposit_id', ''))
        for on_ver, on_info in online_map.items():
            if on_info.doi == doi and on_ver != version:
                if cfg_deposit and on_info.deposit_id == cfg_deposit:
                    continue
                errors.append(
                    f"DOI {doi} hoort bij online v{on_ver}, niet v{version} — "
                    f"mint een nieuwe DOI voor v{version}"
                )
                can_mint_doi = True
                break

    if not loc.has_config:
        errors.append(
            "Geen .zenodo.json config — mint eerst DOI en maak config aan vóór push"
        )
    else:
        cfg = read_config_data(version)
        if not cfg.get('deposit_id'):
            errors.append("Config mist deposit_id — mint eerst een nieuwe DOI voor deze versie")
        if not cfg.get('doi'):
            errors.append("Config mist DOI")
        elif doi and cfg.get('doi') != doi:
            errors.append(
                f"DOI in tex ({doi}) wijkt af van config ({cfg.get('doi')})"
            )
        if doi and cfg.get('doi') == doi and cfg.get('deposit_id'):
            if doi in duplicates and version in duplicates[doi]:
                pass  # duplicate already flagged
            elif any(on_info.doi == doi and on_ver != version for on_ver, on_info in online_map.items()):
                pass  # wrong owner already flagged
            else:
                # Config OK but still need unique doi check above
                pass
        stale_dep = str(cfg.get("deposit_id") or "").strip()
        if stale_dep and local_deposit_is_stale(version, local, online):
            errors.append(
                f"Zenodo deposit {stale_dep} bestaat niet (meer) online — "
                f"gebruik Mint DOI + Config opnieuw (Remint)"
            )
            can_mint_doi = True

    cfg_data = read_config_data(version) if loc.has_config else {}
    expected_doi = (cfg_data.get('doi') or doi).strip()

    owner = online_map.get(version)
    is_published_online = bool(
        owner and owner.state == 'published' and owner.doi and doi and owner.doi == doi
    )

    if not is_published_online and loc.has_config and expected_doi and loc.has_tex:
        # Skip PDF gate when deposit is gone — remint first
        if not local_deposit_is_stale(version, local, online):
            tex = loc.tex_path or main_tex(version)
            cfg_for_pdf = cfg_data if cfg_data else {'pdf_output_dir': '$out'}
            pdf = expected_canon_pdf_path(tex, cfg_for_pdf)
            if not pdf.is_file():
                pdf = resolve_pdf_path(tex, cfg_for_pdf)
            if not pdf.is_file():
                errors.append("Geen PDF gevonden — render eerst opnieuw")
            else:
                matches, found_doi = pdf_doi_matches(pdf, expected_doi)
                if not matches:
                    if found_doi:
                        errors.append(
                            f"PDF bevat verouderde DOI ({found_doi}); "
                            f"tex heeft {expected_doi} — render eerst opnieuw"
                        )
                    else:
                        errors.append(
                            f"Geen DOI gevonden in PDF (verwacht {expected_doi}) — render eerst opnieuw"
                        )

    can_push = len(errors) == 0 and loc.has_config and bool(doi)
    if can_push:
        cfg = read_config_data(version)
        can_push = bool(cfg.get('deposit_id')) and cfg.get('doi') == doi
        if can_push and local_deposit_is_stale(version, local, online):
            can_push = False

    if is_published_online:
        can_push = False
        can_mint_doi = False

    return can_push, can_mint_doi and not can_push, errors


def build_changelog_html(up_to_version: str) -> str:
    lines = ['<hr>', '<h3>Version changelog</h3>', '<ul>']
    for ver, desc in sorted(get_edition_changelog().items(), key=lambda x: version_sort_key(x[0])):
        if version_sort_key(ver) > version_sort_key(up_to_version):
            break
        lines.append(f'<li><strong>v{ver}</strong> &mdash; {desc}</li>')
    lines.append('</ul>')
    return '\n'.join(lines)


def canon_base_description_html(version: str) -> str:
    """Version-aware Zenodo description body (avoids stale v0.8.1 text from parent deposits)."""
    patch = get_edition_changelog().get(version, "")
    patch_p = (
        f"<p><strong>This edition (v{version})</strong> adds on top of the prior canon line: {patch}.</p>"
        if patch
        else ""
    )
    return (
        f"<p>Swirl-String-Theory Canon v{version} is the formal reference document for "
        f"Swirl-String Theory (SST), a continuum-based hydrodynamic and topological framework in which "
        f"physical structure is modeled as arising from stable circulation-bearing configurations in an "
        f"incompressible, inviscid medium. This edition consolidates the core axiomatic layer of the theory, "
        f"defines a minimal primitive structure, and organizes the framework through an explicit epistemic "
        f"classification that distinguishes orthodox input, internally derived consequences, and speculative "
        f"extensions.</p>\n"
        f"<p>The document is designed as a logically stratified canon rather than as a single-claim research "
        f"article. Its primary purpose is to provide a stable source of definitions, canonical constants, "
        f"dependency structure, master relations, and theory-internal consistency rules for subsequent SST "
        f"papers, notes, simulations, and benchmarks. Version {version} places particular emphasis on "
        f"non-circular closure, traceability of assumptions, and compatibility checks against established "
        f"physics in appropriate limits.</p>\n"
        f"<p>The canon includes: (i) formal foundations based on a minimal primitive set; (ii) an axiomatic "
        f"framework for circulation, topology, delay dynamics, and relational time; (iii) a consistency and "
        f"classification layer for epistemic status tracking; (iv) a geometric and topological sector; "
        f"(v) delay-induced mode-selection theory as a route to spectral discreteness; (vi) a conservative "
        f"atomic bridge model and spectroscopic constraints; (vii) a relational time framework with Swirl-Clock, "
        f"foliation, and effective-field-theory bridge structures; and (viii) an integration layer that "
        f"selectively recovers transferable material from earlier SST canon versions without treating those "
        f"versions as external authorities.</p>\n"
        f"<p>Compared with earlier canon releases, v{version} strengthens the formal architecture of SST by "
        f"separating canonical definitions from phenomenological bridge models and by explicitly labeling which "
        f"statements are orthodox, derived within the present framework, or still speculative. It also preserves "
        f"selected higher-level sectors&mdash;such as particle-candidate topology, hydrodynamic exchange barriers, "
        f"benchmark structure, gauge-roadmap elements, and clock/gravity bridge constructions&mdash;while recasting "
        f"them in a stricter and more transparent format.</p>\n"
        f"{patch_p}"
        f"<p>This deposit is intended as a citable canonical reference for the SST framework in its v{version} "
        f"state. It is suitable for use as the primary background document for related technical notes, "
        f"mass-functional derivations, atomic bridge analyses, topological classification work, and future "
        f"computational or phenomenological developments.</p>"
    )


def build_description(version: str, abstract: str = "", base_description: str = "") -> str:
    intro = canon_base_description_html(version)
    if abstract and abstract not in intro:
        intro += f"\n<p>{abstract}</p>"
    changelog = build_changelog_html(version)
    return intro + "\n" + changelog


def refresh_zenodo_config_description(version: str, create_if_missing: bool = True) -> Path | None:
    """Update title/description (and create skeleton config) for a canon edition."""
    if not is_known_canon_version(version):
        return None
    tex = main_tex(version)
    if not tex.is_file():
        return None

    cfg = config_path(version)
    description = build_description(version)
    title = canon_title(version)
    tex_rel = tex_file_relative_path(tex)

    if cfg.is_file():
        data = read_config_data(version)
    elif create_if_missing:
        data = {
            "creators": DEFAULT_CREATORS,
            "keywords": get_canon_keywords(version),
            "upload_type": "publication",
            "publication_type": "preprint",
            "publication_date": datetime.now().strftime('%Y-%m-%d'),
            "language": "eng",
            "access_right": "open",
            "license": "cc-by-4.0",
            "communities": [{"identifier": "sst"}],
            "tex_file": tex_rel,
            "pdf_output_dir": "$out",
            "compile_timeout": 300,
            "related_identifiers": [
                {"identifier": CONCEPT_DOI, "relation": "isVersionOf"},
            ],
        }
    else:
        return None

    data["title"] = title
    data["description"] = description
    data["version"] = zenodo_version_label(version)
    data["keywords"] = get_canon_keywords(version)
    if not data.get("tex_file"):
        data["tex_file"] = tex_rel
    cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return cfg


def refresh_all_canon_zenodo_descriptions(create_if_missing: bool = True) -> list[str]:
    updated: list[str] = []
    root = been_processed_root()
    if not root.is_dir():
        return updated
    for folder in sorted(root.iterdir(), key=lambda p: version_sort_key(p.name.lstrip('v'))):
        if not folder.is_dir() or not is_canon_version_dir(folder.name):
            continue
        version = folder.name.lstrip('v')
        if refresh_zenodo_config_description(version, create_if_missing=create_if_missing):
            updated.append(version)
    return updated


def scan_local_canon_versions() -> list[CanonVersionInfo]:
    root = been_processed_root()
    versions: list[CanonVersionInfo] = []
    if not root.is_dir():
        return versions

    version_dirs = [p for p in root.iterdir() if p.is_dir() and is_canon_version_dir(p.name)]
    for folder in sorted(version_dirs, key=lambda p: version_sort_key(p.name.lstrip('v'))):
        version = folder.name.lstrip('v')
        tex = main_tex(version)
        cfg = config_path(version)
        info = CanonVersionInfo(
            version=version,
            source='local',
            state='local_only',
            has_tex=tex.is_file(),
            tex_path=tex if tex.is_file() else None,
            has_config=cfg.is_file(),
            config_path=cfg if cfg.is_file() else None,
        )
        if tex.is_file():
            meta = extract_metadata_from_latex(tex)
            info.title = meta.get('title') or canon_title(version)
            info.doi = read_doi_from_tex(tex)
            if cfg.is_file():
                try:
                    cfg_data = json.loads(cfg.read_text(encoding='utf-8'))
                    info.deposit_id = str(cfg_data.get('deposit_id', ''))
                    if cfg_data.get('doi'):
                        info.doi = cfg_data['doi']
                except (json.JSONDecodeError, OSError):
                    cfg_data = {}
            else:
                cfg_data = {}
            pdf_cfg = cfg_data if cfg_data else {'pdf_output_dir': '$out'}
            pdf = expected_canon_pdf_path(tex, pdf_cfg)
            if not pdf.is_file():
                pdf = resolve_pdf_path(tex, pdf_cfg)
            info.has_pdf = pdf.is_file()
            info.pdf_path = pdf if pdf.is_file() else None
            if info.has_pdf and info.doi:
                matches, found_doi = pdf_doi_matches(pdf, info.doi)
                info.pdf_doi_ok = matches
                info.pdf_doi = found_doi or read_doi_from_pdf(pdf)
        versions.append(info)
    return versions


def overlay_local_deposit_versions(
    online: list[CanonVersionInfo],
    local: Optional[list[CanonVersionInfo]] = None,
) -> list[CanonVersionInfo]:
    """Re-label online drafts using local deposit_id (Zenodo title may still say v0.8.1)."""
    if not local:
        return online
    by_deposit = {v.deposit_id: v.version for v in local if v.deposit_id}
    if not by_deposit:
        return online
    adjusted: list[CanonVersionInfo] = []
    for entry in online:
        local_ver = by_deposit.get(entry.deposit_id)
        if local_ver and local_ver != entry.version:
            entry = CanonVersionInfo(
                version=local_ver,
                source=entry.source,
                title=entry.title,
                doi=entry.doi,
                deposit_id=entry.deposit_id,
                html_url=entry.html_url,
                state=entry.state,
                publication_date=entry.publication_date,
            )
        adjusted.append(entry)
    return adjusted


def canon_info_from_zenodo_entry(
    entry: dict,
    automation: Optional[ZenodoAutomation] = None,
) -> Optional[CanonVersionInfo]:
    """Build CanonVersionInfo from a list_record_versions / deposit entry."""
    title = entry.get("title") or (entry.get("metadata") or {}).get("title") or ""
    if not is_canon_deposit_title(title):
        return None
    version = parse_version_from_entry(entry)
    deposit_id = str(entry.get("id") or "")
    if not version:
        if not deposit_id:
            return None
        version = f"{ORPHAN_VERSION_PREFIX}{deposit_id}"
    is_published = bool(entry.get("is_published", False))
    state = "published" if is_published else "draft"
    links = entry.get("links") or {}
    html_url = links.get("html") or links.get("self_html") or links.get("latest_html") or ""
    if not html_url and deposit_id:
        base = getattr(automation, "base_url", "https://zenodo.org") if automation else "https://zenodo.org"
        if state == "draft":
            html_url = f"{base}/deposit/{deposit_id}"
        else:
            html_url = f"{base}/records/{deposit_id}"
    doi = entry.get("doi") or ""
    if not doi:
        meta = entry.get("metadata") or {}
        prereserve = meta.get("prereserve_doi") or {}
        doi = meta.get("doi") or prereserve.get("doi") or ""
    return CanonVersionInfo(
        version=version,
        source="online",
        title=title,
        doi=str(doi),
        deposit_id=deposit_id,
        html_url=html_url,
        state=state,
        publication_date=entry.get("publication_date") or "",
    )


def collect_canon_draft_deposits(
    automation: ZenodoAutomation,
    seen_ids: set[str],
) -> list[CanonVersionInfo]:
    """All unpublished token deposits with a Canon-like title (including orphans)."""
    extras: list[CanonVersionInfo] = []
    for deposit in automation.list_deposits(published_only=False, limit=100):
        if deposit.get("submitted", False):
            continue
        dep_id = str(deposit.get("id") or "")
        if not dep_id or dep_id in seen_ids:
            continue
        meta = deposit.get("metadata") or {}
        title = meta.get("title") or ""
        if not is_canon_deposit_title(title):
            continue
        entry = {
            "id": dep_id,
            "title": title,
            "version": meta.get("version", ""),
            "doi": meta.get("doi") or (meta.get("prereserve_doi") or {}).get("doi", ""),
            "publication_date": meta.get("publication_date", ""),
            "is_published": False,
            "links": deposit.get("links") or {},
            "metadata": meta,
        }
        info = canon_info_from_zenodo_entry(entry, automation)
        if info:
            seen_ids.add(dep_id)
            extras.append(info)
    return extras


def collect_local_linked_drafts(
    automation: ZenodoAutomation,
    local: Optional[list[CanonVersionInfo]],
    seen_ids: set[str],
) -> list[CanonVersionInfo]:
    """Probe local deposit_ids that may fall outside the recent deposits page."""
    extras: list[CanonVersionInfo] = []
    if not local:
        return extras
    for loc in local:
        dep_id = str(loc.deposit_id or "").strip()
        if not dep_id or dep_id in seen_ids:
            continue
        deposit = automation.get_deposit_info(dep_id, quiet=True)
        if not deposit or deposit.get("submitted"):
            continue
        meta = deposit.get("metadata") or {}
        title = meta.get("title") or loc.title or ""
        if title and not is_canon_deposit_title(title):
            # Local claim still wins if config points here
            title = title or canon_title(loc.version)
        entry = {
            "id": dep_id,
            "title": title or canon_title(loc.version),
            "version": meta.get("version") or zenodo_version_label(loc.version),
            "doi": meta.get("doi")
            or (meta.get("prereserve_doi") or {}).get("doi")
            or loc.doi
            or "",
            "publication_date": meta.get("publication_date", ""),
            "is_published": False,
            "links": deposit.get("links") or {},
            "metadata": meta,
        }
        # Force version from local when known
        info = canon_info_from_zenodo_entry(entry, automation)
        if not info:
            info = CanonVersionInfo(
                version=loc.version,
                source="online",
                title=entry["title"],
                doi=str(entry["doi"]),
                deposit_id=dep_id,
                html_url=(deposit.get("links") or {}).get("html")
                or f"{automation.base_url}/deposit/{dep_id}",
                state="draft",
            )
        elif is_orphan_online_version(info.version) and loc.version:
            info = CanonVersionInfo(
                version=loc.version,
                source=info.source,
                title=info.title,
                doi=info.doi,
                deposit_id=info.deposit_id,
                html_url=info.html_url,
                state="draft",
                publication_date=info.publication_date,
            )
        seen_ids.add(dep_id)
        extras.append(info)
    return extras


def dedupe_online_canon_versions(versions: list[CanonVersionInfo]) -> list[CanonVersionInfo]:
    """Keep one entry per version key; drafts win over published for the same version."""
    by_version: dict[str, CanonVersionInfo] = {}
    by_deposit: dict[str, CanonVersionInfo] = {}
    for v in versions:
        if v.deposit_id:
            existing_dep = by_deposit.get(v.deposit_id)
            if existing_dep and existing_dep.version != v.version:
                if is_orphan_online_version(existing_dep.version) and not is_orphan_online_version(v.version):
                    by_version.pop(existing_dep.version, None)
                elif not is_orphan_online_version(existing_dep.version) and is_orphan_online_version(v.version):
                    continue
            by_deposit[v.deposit_id] = v
        existing = by_version.get(v.version)
        if not existing:
            by_version[v.version] = v
        elif v.state == "draft" and existing.state != "draft":
            by_version[v.version] = v
        elif is_orphan_online_version(existing.version) and not is_orphan_online_version(v.version):
            by_version[v.version] = v
        elif version_sort_key(v.version) >= version_sort_key(existing.version) and v.state == existing.state:
            by_version[v.version] = v
    return sorted(
        by_version.values(),
        key=lambda v: (is_orphan_online_version(v.version), version_sort_key(v.version)),
    )


def fetch_online_canon_versions(
    automation: ZenodoAutomation,
    local: Optional[list[CanonVersionInfo]] = None,
) -> list[CanonVersionInfo]:
    versions: list[CanonVersionInfo] = []
    anchor = resolve_canon_concept_anchor(local, automation)
    raw = automation.list_record_versions(anchor)
    seen_ids: set[str] = set()
    for entry in raw:
        info = canon_info_from_zenodo_entry(entry, automation)
        if not info:
            continue
        if info.deposit_id:
            seen_ids.add(info.deposit_id)
        versions.append(info)

    versions.extend(collect_canon_draft_deposits(automation, seen_ids))
    versions.extend(collect_local_linked_drafts(automation, local, seen_ids))
    versions = overlay_local_deposit_versions(versions, local)
    return dedupe_online_canon_versions(versions)


def list_online_drafts(online: list[CanonVersionInfo]) -> list[CanonVersionInfo]:
    return [v for v in online if v.state == "draft"]


def list_online_published(online: list[CanonVersionInfo]) -> list[CanonVersionInfo]:
    return [v for v in online if v.state == "published"]


def list_bindable_local_versions(
    local: list[CanonVersionInfo],
    online: list[CanonVersionInfo],
    draft_deposit_id: str = "",
) -> list[CanonVersionInfo]:
    """Local editions that can claim an online draft (tex present; not published elsewhere)."""
    published_versions = {
        v.version for v in online if v.state == "published" and not is_orphan_online_version(v.version)
    }
    draft_deposit_id = str(draft_deposit_id or "")
    bindable: list[CanonVersionInfo] = []
    for loc in local:
        if not loc.has_tex or is_orphan_online_version(loc.version):
            continue
        if loc.version in published_versions:
            continue
        if loc.deposit_id and draft_deposit_id and loc.deposit_id != draft_deposit_id:
            online_match = next((o for o in online if o.deposit_id == loc.deposit_id), None)
            if online_match and online_match.state == "published":
                continue
            if online_match and online_match.state == "draft" and online_match.deposit_id != draft_deposit_id:
                continue
        bindable.append(loc)
    return sorted(bindable, key=lambda v: version_sort_key(v.version))


def compare_versions(
    local: list[CanonVersionInfo],
    online: list[CanonVersionInfo],
) -> list[VersionStatus]:
    local_map = {v.version: v for v in local}
    online_map = {v.version: v for v in online if not is_orphan_online_version(v.version)}
    all_versions = sorted(set(local_map) | set(online_map), key=version_sort_key)
    duplicates = find_duplicate_local_dois(local)

    statuses: list[VersionStatus] = []
    for ver in all_versions:
        loc = local_map.get(ver)
        on = online_map.get(ver)
        can_push, can_mint, errors = (False, False, [])
        can_push_metadata = False
        can_update_config = False
        can_render = False
        if loc:
            can_push, can_mint, errors = validate_version_for_push(ver, local, online)
            can_render = bool(
                loc.has_tex
                and loc.has_config
                and loc.doi
                and (not loc.has_pdf or not loc.pdf_doi_ok)
            )

        stale_pdf = bool(
            loc
            and loc.has_tex
            and loc.has_config
            and loc.doi
            and (not loc.has_pdf or not loc.pdf_doi_ok)
        )

        if loc and on:
            if (
                on.state == 'published'
                and loc.has_config
                and loc.doi
                and on.doi
                and loc.doi == on.doi
            ):
                can_push_metadata = True
                can_update_config = True
                can_render = False
                status = 'published'
                msg = f"v{ver} gepubliceerd — metadata kan worden bijgewerkt"
            elif on.state == 'draft':
                status = 'draft_online'
                msg = f"v{ver} heeft draft op Zenodo"
                if stale_pdf:
                    msg += " — PDF-DOI wijkt af (render eerst opnieuw)"
                if loc.has_config and loc.doi and on.deposit_id:
                    can_update_config = True
            elif stale_pdf and on.state != 'published':
                status = 'stale_pdf'
                msg = "PDF-DOI wijkt af van tex — render eerst opnieuw"
            elif loc.doi and on.doi and loc.doi == on.doi:
                status = 'synced'
                msg = f"v{ver} gesynchroniseerd (DOI match)"
            elif can_push:
                status = 'ready_to_push'
                msg = f"v{ver} klaar om te pushen (unieke DOI + config)"
            else:
                status = 'synced'
                msg = f"v{ver} lokaal en online aanwezig"
        elif loc and not on:
            if local_deposit_is_stale(ver, local, online):
                status = 'stale_deposit'
                msg = (
                    f"v{ver} — lokale deposit bestaat niet (meer) op Zenodo; "
                    f"Remint DOI + Config"
                )
            elif stale_pdf:
                status = 'stale_pdf'
                msg = "PDF-DOI wijkt af van tex — render eerst opnieuw"
            elif can_push:
                status = 'ready_to_push'
                msg = f"v{ver} klaar om te pushen naar Zenodo"
            elif loc.doi and loc.doi in duplicates:
                status = 'duplicate_doi'
                msg = f"v{ver} — DOI niet uniek (gedeeld met andere lokale versies)"
            elif not loc.has_config:
                status = 'missing_config'
                msg = f"v{ver} — geen .zenodo.json; mint eerst DOI"
            elif errors:
                status = 'blocked'
                msg = f"v{ver} — niet klaar voor push"
            else:
                status = 'ahead_local'
                msg = f"v{ver} alleen lokaal — nog niet op Zenodo"
        elif on and not loc:
            status = 'online_only'
            msg = f"v{on.version} alleen op Zenodo"
        else:
            status = 'local_only'
            msg = f"v{ver} onbekend"

        if errors and status not in (
            'duplicate_doi', 'missing_config', 'stale_pdf', 'published', 'stale_deposit'
        ):
            msg = errors[0]

        statuses.append(VersionStatus(
            version=ver,
            status=status,
            local=loc,
            online=on,
            message=msg,
            errors=errors,
            can_push=can_push,
            can_push_metadata=can_push_metadata,
            can_update_config=can_update_config,
            can_mint_doi=can_mint,
            can_render=can_render,
        ))
    return statuses


def find_parent_record_id(
    version: str,
    online: list[CanonVersionInfo],
    automation: ZenodoAutomation,
    local: Optional[list[CanonVersionInfo]] = None,
) -> str:
    """Latest record id before `version` (online published, or locally minted)."""
    candidates: list[tuple[tuple[int, ...], str, bool]] = []
    for v in online:
        if is_orphan_online_version(v.version):
            continue
        if version_sort_key(v.version) < version_sort_key(version) and v.deposit_id:
            candidates.append((
                version_sort_key(v.version),
                v.deposit_id,
                v.state == 'published',
            ))
    if local:
        for v in local:
            if version_sort_key(v.version) < version_sort_key(version) and v.deposit_id:
                candidates.append((
                    version_sort_key(v.version),
                    v.deposit_id,
                    False,
                ))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        published = [c for c in candidates if c[2]]
        pool = published if published else candidates
        return pool[-1][1]
    head_doi = resolve_canon_concept_anchor(local, automation)
    latest = automation.fetch_record_by_doi(head_doi)
    if latest:
        return str(latest.get('id', ''))
    root = automation.fetch_record_by_doi(ROOT_DOI)
    if root:
        return str(root.get('id', ''))
    return automation._record_id_from_doi(head_doi)


def find_existing_online_draft(version: str, online: list[CanonVersionInfo]) -> Optional[CanonVersionInfo]:
    for v in online:
        if v.version == version and v.state == 'draft':
            return v
    cfg = read_config_data(version)
    deposit_id = str(cfg.get('deposit_id', ''))
    if deposit_id:
        for v in online:
            if v.deposit_id == deposit_id and v.state == 'draft':
                return v
    return None


def write_zenodo_config(
    version: str,
    deposit_id: str,
    doi: str,
    description: str,
    tex_rel: str,
) -> Path:
    cfg = config_path(version)
    data = {
        "title": canon_title(version),
        "version": zenodo_version_label(version),
        "creators": DEFAULT_CREATORS,
        "description": description,
        "keywords": get_canon_keywords(version),
        "upload_type": "publication",
        "publication_type": "preprint",
        "publication_date": datetime.now().strftime('%Y-%m-%d'),
        "language": "eng",
        "access_right": "open",
        "license": "cc-by-4.0",
        "communities": [{"identifier": "sst"}],
        "doi": doi,
        "deposit_id": deposit_id,
        "tex_file": tex_rel.replace('\\', '/'),
        "pdf_output_dir": "$out",
        "compile_timeout": 300,
        "related_identifiers": [
            {"identifier": CONCEPT_DOI, "relation": "isVersionOf"},
        ],
    }
    cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return cfg


def mint_version_doi(
    version: str,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    force: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    """Create a new Zenodo version draft, assign unique DOI to tex, write .zenodo.json (no PDF upload).

    If local config points at a deleted deposit, remints automatically.
    Pass force=True to remint even when a live draft/config already exists.
    """
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PushResult(version=version, success=False)

    if not is_known_canon_version(version):
        result.message = (
            f"Unknown version {version} — geen been_processed/SST_CANON-v{version}.tex "
            f"en geen entry in canon_edition.py"
        )
        return result

    tex = main_tex(version)
    if not tex.is_file():
        result.message = f"LaTeX not found: {tex}"
        return result

    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)

    local_versions = scan_local_canon_versions()
    online_versions: list[CanonVersionInfo] = []
    if automation:
        online_versions = fetch_online_canon_versions(automation, local_versions)

    existing_draft = find_existing_online_draft(version, online_versions)
    cfg_existing = read_config_data(version)
    stale_local = local_deposit_is_stale(version, local_versions, online_versions)
    if (
        cfg_existing.get('deposit_id')
        and cfg_existing.get('doi')
        and not force
        and not stale_local
    ):
        _, _, errors = validate_version_for_push(version, local_versions, online_versions)
        if not errors:
            result.message = f"v{version} heeft al unieke DOI en config ({cfg_existing.get('doi')})"
            result.doi = cfg_existing.get('doi', '')
            result.deposit_id = str(cfg_existing.get('deposit_id', ''))
            return result

    if stale_local:
        log(
            f"Stale local deposit {cfg_existing.get('deposit_id')} not online — "
            f"reminting new Zenodo draft for v{version}"
        )

    meta = extract_metadata_from_latex(tex)
    abstract = meta.get('description', '')
    description = build_description(version, abstract)
    tex_rel = tex_file_relative_path(tex)

    if dry_run:
        parent_id = (
            find_parent_record_id(version, online_versions, automation, local_versions)
            if automation else resolve_latest_head_doi(local_versions).split('.')[-1]
        )
        result.success = True
        result.message = "Dry run OK (mint DOI)"
        result.actions = [
            f"Would create new version from record {parent_id}" if not existing_draft else f"Would reuse draft {existing_draft.deposit_id}",
            f"Would assign unique DOI in {tex.name}",
            f"Would write {config_path(version).name}",
        ]
        log(f"[DRY RUN mint] v{version}: " + "; ".join(result.actions))
        return result

    deposit_id = ""
    doi = ""
    html_url = ""

    if existing_draft:
        deposit_id = existing_draft.deposit_id
        doi = existing_draft.doi or automation.get_prereserved_doi(deposit_id) or ""
        html_url = existing_draft.html_url
        log(f"Reusing existing Zenodo draft for v{version}: {deposit_id}")
        result.actions.append('Reused existing Zenodo draft')
    else:
        parent_id = find_parent_record_id(version, online_versions, automation, local_versions)
        log(f"Minting new Zenodo version from record {parent_id}...")
        nv = automation.create_new_version(parent_id)
        if not nv:
            apply_automation_api_error(
                result, automation, "Failed to create new Zenodo version"
            )
            return result
        deposit_id = nv['deposit_id']
        doi = nv.get('doi') or automation.get_prereserved_doi(deposit_id) or ""
        html_url = nv.get('html_url', '')
        result.actions.append('Created new Zenodo version draft')
        time.sleep(1)

    if not doi:
        doi = automation.get_prereserved_doi(deposit_id) or f"10.5281/zenodo.{deposit_id}"

    log(f"DOI: {doi}")
    update_doi_in_canon_tex(tex, doi)
    result.actions.append('Updated DOI in LaTeX')

    cfg = write_zenodo_config(version, deposit_id, doi, description, tex_rel)
    result.actions.append(f'Wrote config {cfg.name}')

    cfg_data = read_config_data(version)
    if update_zenodo_metadata(automation, deposit_id, cfg_data):
        result.actions.append('Synced version metadata to Zenodo')
        log(f"Zenodo version set to {cfg_data.get('version')}")
    else:
        apply_automation_api_error(
            result,
            automation,
            "Config written but failed to sync version metadata to Zenodo",
        )
        result.deposit_id = deposit_id
        result.doi = doi
        result.html_url = html_url or f"https://zenodo.org/deposit/{deposit_id}"
        return result

    result.success = True
    result.message = f"Unieke DOI en config aangemaakt voor v{version}"
    result.deposit_id = deposit_id
    result.doi = doi
    result.html_url = html_url or f"https://zenodo.org/deposit/{deposit_id}"
    return result


def render_version_pdf(
    version: str,
    dry_run: bool = False,
    verbose: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    """Compile LaTeX to PDF locally and verify DOI matches tex/config (no Zenodo upload)."""
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    def log_diagnostics(pdf_file: Path) -> None:
        if not verbose:
            return
        log(f"--- PDF-DOI diagnostiek v{version} ---")
        for line in format_pdf_doi_diagnostics(
            pdf_file,
            expected_doi,
            tex_file=tex,
            config_data=cfg_data,
        ):
            log(f"  {line}")

    result = PushResult(version=version, success=False)

    tex = main_tex(version)
    if not tex.is_file():
        result.message = f"LaTeX not found: {tex}"
        return result

    cfg_data = read_config_data(version)
    expected_doi = (cfg_data.get('doi') or read_doi_from_tex(tex)).strip()
    if not expected_doi:
        result.message = "Geen DOI in tex/config — mint eerst DOI"
        return result

    pdf_output_dir = cfg_data.get('pdf_output_dir', '$out')
    out_dir = tex.parent / pdf_output_dir if pdf_output_dir else tex.parent / '$out'
    compile_timeout = int(cfg_data.get('compile_timeout', 300))

    if dry_run:
        result.success = True
        result.message = "Dry run OK (render PDF)"
        result.doi = expected_doi
        result.actions = [f"Would compile {tex.name} -> {out_dir.name}/", f"Would verify DOI {expected_doi}"]
        log(f"[DRY RUN render] v{version}: " + "; ".join(result.actions))
        return result

    log(f"Rendering PDF for v{version}...")
    success, pdf_file = compile_latex(
        tex,
        num_passes=2,
        output_dir=out_dir,
        timeout=compile_timeout,
    )
    if not success or not pdf_file:
        result.message = "LaTeX compile mislukt"
        if verbose:
            log_diagnostics(out_dir / f"{tex.stem}.pdf")
        return result

    result.actions.append(f"Compiled {pdf_file.name}")
    matches, found_doi = pdf_doi_matches(pdf_file, expected_doi)
    if not matches:
        if found_doi:
            result.message = (
                f"PDF bevat verkeerde DOI ({found_doi}); verwacht {expected_doi}"
            )
        else:
            result.message = f"Geen DOI gevonden in PDF (verwacht {expected_doi})"
        log_diagnostics(pdf_file)
        return result

    result.success = True
    result.message = f"PDF gerenderd met DOI {expected_doi}"
    result.doi = expected_doi
    result.actions.append(f"PDF DOI verified: {expected_doi}")
    log(result.message)
    if verbose:
        log(f"  verified PDF: {pdf_file}")
    return result


def push_version_as_draft(
    version: str,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    publish: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PushResult(version=version, success=False)

    if not is_known_canon_version(version):
        result.message = (
            f"Unknown version {version} — geen been_processed/SST_CANON-v{version}.tex "
            f"en geen entry in canon_edition.py"
        )
        return result

    tex = main_tex(version)
    if not tex.is_file():
        result.message = f"LaTeX not found: {tex}"
        return result

    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)

    local_versions = scan_local_canon_versions()
    online_versions: list[CanonVersionInfo] = []
    if automation:
        online_versions = fetch_online_canon_versions(automation, local_versions)

    online_entry = next((v for v in online_versions if v.version == version), None)
    if online_entry and online_entry.state == 'published':
        result.message = f"v{version} is gepubliceerd — gebruik metadata-push (geen PDF)"
        log(f"✗ {result.message}")
        return result

    can_push, _, errors = validate_version_for_push(version, local_versions, online_versions)
    if not can_push:
        result.message = "Push geblokkeerd — los eerst deze punten op:"
        result.actions = errors
        for err in errors:
            log(f"✗ {err}")
        return result

    cfg = read_config_data(version)
    deposit_id = str(cfg.get('deposit_id', ''))
    doi = cfg.get('doi', '')
    cfg_file = config_path(version)

    meta = extract_metadata_from_latex(tex)
    abstract = meta.get('description', '')
    description = build_description(version, abstract)

    if dry_run:
        result.success = True
        result.message = "Dry run OK (push)"
        result.actions = [
            f"Would use config {cfg_file.name} (deposit {deposit_id}, DOI {doi})",
            f"Would render PDF to $out/",
            f"Would upload PDF and metadata (draft={not publish})",
        ]
        log(f"[DRY RUN push] v{version}: " + "; ".join(result.actions))
        return result

    # Refresh description in config before upload
    tex_rel = tex_file_relative_path(tex)
    write_zenodo_config(version, deposit_id, doi, description, tex_rel)
    result.actions.append(f'Updated config {cfg_file.name}')

    log("Rendering PDF and uploading to Zenodo...")
    proc = process_config_file(cfg_file, automation, get_repo_root())
    if proc['status'] != 'success':
        apply_automation_api_error(
            result, automation, proc.get('message', 'Render/upload failed')
        )
        result.actions.extend(proc.get('actions', []))
        return result
    result.actions.extend(proc.get('actions', []))

    html_url = f"https://zenodo.org/deposit/{deposit_id}"

    if publish:
        log("Publishing deposit...")
        if automation.publish_deposit(deposit_id):
            result.actions.append('Published on Zenodo')
        else:
            apply_automation_api_error(result, automation, "Upload OK but publish failed")
            result.deposit_id = deposit_id
            result.doi = doi
            result.html_url = html_url
            return result
    else:
        result.actions.append('Left as draft on Zenodo')

    result.success = True
    result.message = "Draft pushed successfully" if not publish else "Published successfully"
    result.deposit_id = deposit_id
    result.doi = doi
    result.html_url = html_url
    return result


def push_published_metadata(
    version: str,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    publish: bool = True,
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    """Update metadata on a published Zenodo record (no PDF compile/upload)."""
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PushResult(version=version, success=False)

    if not is_known_canon_version(version):
        result.message = (
            f"Unknown version {version} — geen been_processed/SST_CANON-v{version}.tex "
            f"en geen entry in canon_edition.py"
        )
        return result

    if automation is None:
        token = read_token_from_zenodo_py()
        if not token:
            if dry_run:
                result.message = "No Zenodo token found (needed to verify published status)"
            else:
                result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)

    local_versions = scan_local_canon_versions()
    online_versions: list[CanonVersionInfo] = []
    if automation:
        online_versions = fetch_online_canon_versions(automation, local_versions)

    online_entry = next((v for v in online_versions if v.version == version), None)
    if not online_entry or online_entry.state != 'published':
        result.message = f"v{version} is niet gepubliceerd op Zenodo — gebruik draft-push"
        return result

    cfg_file = config_path(version)
    if not cfg_file.is_file():
        result.message = "Geen .zenodo.json config"
        return result

    loc = next((v for v in local_versions if v.version == version), None)
    cfg_data = read_config_data(version)
    deposit_id = str(cfg_data.get('deposit_id', '') or online_entry.deposit_id)
    doi = cfg_data.get('doi', '') or online_entry.doi

    if not deposit_id:
        result.message = "Config mist deposit_id"
        return result
    if loc and loc.doi and online_entry.doi and loc.doi != online_entry.doi:
        result.message = f"DOI mismatch: lokaal {loc.doi} vs online {online_entry.doi}"
        return result

    if dry_run:
        result.success = True
        result.message = "Dry run OK (metadata push)"
        result.doi = doi
        result.deposit_id = deposit_id
        result.actions = [
            f"Would refresh local {cfg_file.name}",
            f"Would edit deposit {deposit_id}",
            "Would update metadata (no PDF)",
            "Would publish" if publish else "Would leave as draft after edit",
        ]
        log(f"[DRY RUN metadata] v{version}: " + "; ".join(result.actions))
        return result

    log(f"Refreshing local config for v{version}...")
    refreshed = refresh_zenodo_config_description(version, create_if_missing=False)
    if not refreshed:
        result.message = f"Kon config niet verversen voor v{version}"
        return result
    result.actions.append(f'Refreshed local {cfg_file.name}')

    with open(cfg_file, encoding='utf-8') as f:
        cfg_data = json.load(f)

    log(f"Opening deposit {deposit_id} for edit...")
    if not automation.edit_deposit(deposit_id):
        apply_automation_api_error(
            result, automation, "Kon gepubliceerd record niet openen voor bewerking"
        )
        return result
    result.actions.append('Opened deposit for edit')

    log("Updating Zenodo metadata (no PDF)...")
    if not update_zenodo_metadata(automation, deposit_id, cfg_data):
        apply_automation_api_error(result, automation, "Metadata-update mislukt")
        return result
    result.actions.append('Updated metadata on Zenodo')

    if publish:
        log("Publishing metadata update...")
        if automation.publish_deposit(deposit_id):
            result.actions.append('Published metadata update')
        else:
            apply_automation_api_error(
                result, automation, "Metadata bijgewerkt maar publiceren mislukt"
            )
            result.deposit_id = deposit_id
            result.doi = doi
            result.html_url = online_entry.html_url or f"https://zenodo.org/records/{deposit_id}"
            return result
    else:
        result.actions.append('Left as draft after metadata edit')

    result.success = True
    result.message = "Metadata gepubliceerd op Zenodo" if publish else "Metadata bijgewerkt (draft)"
    result.deposit_id = deposit_id
    result.doi = doi
    result.html_url = online_entry.html_url or f"https://zenodo.org/records/{deposit_id}"
    return result


def update_config_no_pdf(
    version: str,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    publish_if_published: bool = True,
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    """
    Refresh local .zenodo.json and push metadata only (no PDF compile/upload).

    Drafts: PUT metadata. Published records: edit → update → optional publish.
    """
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PushResult(version=version, success=False)
    if not is_known_canon_version(version):
        result.message = f"Unknown version {version}"
        return result
    if is_orphan_online_version(version):
        result.message = "Orphan draft — bind eerst aan een lokale versie"
        return result

    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)

    local_versions = scan_local_canon_versions()
    online_versions: list[CanonVersionInfo] = []
    if automation:
        online_versions = fetch_online_canon_versions(automation, local_versions)

    online_entry = next((v for v in online_versions if v.version == version), None)
    cfg_data = read_config_data(version)
    deposit_id = str(cfg_data.get("deposit_id") or (online_entry.deposit_id if online_entry else "") or "")
    doi = str(cfg_data.get("doi") or (online_entry.doi if online_entry else "") or "")

    if not config_path(version).is_file():
        result.message = "Geen .zenodo.json config"
        return result
    if not deposit_id:
        result.message = "Config mist deposit_id (bind/mint eerst)"
        return result
    if not online_entry:
        result.message = f"Geen online Canon-record voor v{version}"
        return result

    if dry_run:
        result.success = True
        result.doi = doi
        result.deposit_id = deposit_id
        result.message = "Dry run OK (update config, no PDF)"
        actions = [
            f"Would refresh local {config_path(version).name}",
            f"Would update metadata on deposit {deposit_id} (no PDF)",
        ]
        if online_entry.state == "published":
            actions.append("Would open published record for edit")
            if publish_if_published:
                actions.append("Would publish metadata update")
        result.actions = actions
        log(f"[DRY RUN update-config] v{version}: " + "; ".join(actions))
        return result

    log(f"Refreshing local config for v{version}...")
    refreshed = refresh_zenodo_config_description(version, create_if_missing=False)
    if not refreshed:
        result.message = f"Kon config niet verversen voor v{version}"
        return result
    result.actions.append(f"Refreshed local {config_path(version).name}")
    cfg_data = read_config_data(version)
    # Preserve deposit/doi after refresh
    cfg_data["deposit_id"] = deposit_id
    if doi:
        cfg_data["doi"] = doi
    config_path(version).write_text(json.dumps(cfg_data, indent=2, ensure_ascii=False), encoding="utf-8")

    if online_entry.state == "published":
        log(f"Opening published deposit {deposit_id} for edit...")
        if not automation.edit_deposit(deposit_id):
            apply_automation_api_error(
                result, automation, "Kon gepubliceerd record niet openen voor bewerking"
            )
            return result
        result.actions.append("Opened deposit for edit")

    log("Updating Zenodo metadata (no PDF)...")
    if not update_zenodo_metadata(automation, deposit_id, cfg_data):
        apply_automation_api_error(result, automation, "Metadata-update mislukt")
        return result
    result.actions.append("Updated metadata on Zenodo")

    if online_entry.state == "published" and publish_if_published:
        log("Publishing metadata update...")
        if not automation.publish_deposit(deposit_id):
            apply_automation_api_error(
                result, automation, "Metadata bijgewerkt maar publiceren mislukt"
            )
            result.deposit_id = deposit_id
            result.doi = doi
            result.html_url = online_entry.html_url
            return result
        result.actions.append("Published metadata update")
        result.message = "Config + metadata gepubliceerd (geen PDF)"
    else:
        result.message = "Config + draft metadata bijgewerkt (geen PDF)"

    result.success = True
    result.deposit_id = deposit_id
    result.doi = doi
    result.html_url = online_entry.html_url or f"https://zenodo.org/deposit/{deposit_id}"
    return result


def bind_draft_to_local_version(
    deposit_id: str,
    version: str,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    """
    Bind an existing Zenodo draft to a local canon edition (metadata + config only).

    Does not create a new Zenodo version and does not upload PDF/files.
    """
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PushResult(version=version, success=False)
    deposit_id = str(deposit_id or "").strip()
    if not deposit_id:
        result.message = "deposit_id ontbreekt"
        return result
    if not is_known_canon_version(version) or is_orphan_online_version(version):
        result.message = f"Ongeldige lokale versie {version}"
        return result

    tex = main_tex(version)
    if not tex.is_file():
        result.message = f"LaTeX not found: {tex}"
        return result

    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)

    local_versions = scan_local_canon_versions()
    online_versions: list[CanonVersionInfo] = []
    if automation:
        online_versions = fetch_online_canon_versions(automation, local_versions)

    published = {
        v.version for v in online_versions
        if v.state == "published" and not is_orphan_online_version(v.version)
    }
    if version in published:
        result.message = f"v{version} is al gepubliceerd op Zenodo — kies een andere versie"
        return result

    draft = next(
        (v for v in online_versions if v.deposit_id == deposit_id and v.state == "draft"),
        None,
    )
    doi = ""
    html_url = ""
    if draft:
        doi = draft.doi or ""
        html_url = draft.html_url or ""
    elif automation:
        dep = automation.get_deposit_info(deposit_id)
        if not dep:
            result.message = f"Deposit {deposit_id} niet gevonden"
            return result
        if dep.get("submitted"):
            result.message = f"Deposit {deposit_id} is geen draft"
            return result
        meta = dep.get("metadata") or {}
        prereserve = meta.get("prereserve_doi") or {}
        doi = meta.get("doi") or prereserve.get("doi") or ""
        html_url = (dep.get("links") or {}).get("html") or f"https://zenodo.org/deposit/{deposit_id}"

    if automation and not doi:
        doi = automation.get_prereserved_doi(deposit_id) or ""

    if dry_run:
        result.success = True
        result.deposit_id = deposit_id
        result.doi = doi
        result.message = "Dry run OK (bind draft)"
        result.actions = [
            f"Would write config for v{version} → deposit {deposit_id}",
            "Would update draft metadata (no PDF)",
            "Would sync tex DOI if needed",
        ]
        log(f"[DRY RUN bind] draft {deposit_id} → v{version}: " + "; ".join(result.actions))
        return result

    description = build_description(version)
    tex_rel = tex_file_relative_path(tex)
    log(f"Binding draft {deposit_id} to local v{version}...")
    write_zenodo_config(version, deposit_id, doi, description, tex_rel)
    result.actions.append(f"Wrote {config_path(version).name}")

    # Re-refresh keeps changelog current while preserving deposit/doi
    refresh_zenodo_config_description(version, create_if_missing=False)
    cfg_data = read_config_data(version)
    cfg_data["deposit_id"] = deposit_id
    if doi:
        cfg_data["doi"] = doi
    config_path(version).write_text(json.dumps(cfg_data, indent=2, ensure_ascii=False), encoding="utf-8")

    current_tex_doi = read_doi_from_tex(tex)
    if doi and current_tex_doi != doi:
        log(f"Updating tex DOI → {doi}")
        update_doi_in_canon_tex(tex, doi)
        result.actions.append("Updated tex DOI")

    log("Updating draft metadata on Zenodo (no PDF)...")
    if not update_zenodo_metadata(automation, deposit_id, cfg_data):
        apply_automation_api_error(
            result, automation, "Config geschreven maar Zenodo metadata-update mislukt"
        )
        result.deposit_id = deposit_id
        result.doi = doi
        result.html_url = html_url
        return result
    result.actions.append("Updated draft metadata on Zenodo")

    result.success = True
    result.message = f"Draft {deposit_id} gebonden aan v{version} (geen PDF)"
    result.deposit_id = deposit_id
    result.doi = doi
    result.html_url = html_url or f"https://zenodo.org/deposit/{deposit_id}"
    return result


def push_versions_range(
    from_version: str,
    to_version: str,
    dry_run: bool = False,
    publish: bool = False,
    automation: Optional[ZenodoAutomation] = None,
    on_log: Optional[Callable[[str], None]] = None,
) -> list[PushResult]:
    results = []
    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            return [PushResult(version=from_version, success=False, message="No Zenodo token found")]
        automation = ZenodoAutomation(token, sandbox=False)

    for ver in sorted(get_edition_changelog().keys(), key=version_sort_key):
        if version_sort_key(ver) < version_sort_key(from_version):
            continue
        if version_sort_key(ver) > version_sort_key(to_version):
            break
        r = push_version_as_draft(ver, automation=automation, dry_run=dry_run, publish=publish, on_log=on_log)
        results.append(r)
        if not dry_run and not r.success:
            break
        if not dry_run:
            time.sleep(1)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description='Push SST Canon versions to Zenodo')
    parser.add_argument('--version', help='Single version e.g. 0.8.5')
    parser.add_argument('--from', dest='from_version', default='0.8.2', help='Start version')
    parser.add_argument('--to', dest='to_version', default=None, help='End version (default: latest local/canon)')
    parser.add_argument('--dry-run', action='store_true', help='Show actions without API calls')
    parser.add_argument('--publish', action='store_true', help='Publish after upload (default: draft)')
    parser.add_argument('--list-local', action='store_true', help='List local canon versions')
    parser.add_argument('--list-online', action='store_true', help='List online canon versions')
    parser.add_argument('--compare', action='store_true', help='Compare local vs online')
    parser.add_argument('--mint-doi', action='store_true', help='Mint unique DOI + create config (no PDF upload)')
    parser.add_argument('--render-only', action='store_true', help='Render PDF locally (no Zenodo upload)')
    parser.add_argument(
        '--refresh-descriptions',
        action='store_true',
        help='Refresh title/description in local .zenodo.json files (create skeleton if missing)',
    )
    parser.add_argument(
        '--push-metadata',
        action='store_true',
        help='Push metadata only to a published record (no PDF); use with --version',
    )
    parser.add_argument(
        '--no-publish',
        action='store_true',
        help='With --push-metadata: update metadata but do not publish',
    )
    args = parser.parse_args()

    token = read_token_from_zenodo_py()
    automation = ZenodoAutomation(token, sandbox=False) if token else None

    if args.refresh_descriptions:
        versions = refresh_all_canon_zenodo_descriptions(create_if_missing=True)
        for ver in versions:
            print(f"Updated v{ver}: {config_path(ver)}")
        print(f"Refreshed {len(versions)} config(s)")
        return

    if args.list_local:
        for v in scan_local_canon_versions():
            pdf_flag = '✓' if v.pdf_doi_ok else ('⚠' if v.has_pdf else '✗')
            print(f"v{v.version}: tex={v.has_tex} pdf={pdf_flag} doi={v.doi or '-'} pdf_doi={v.pdf_doi or '-'}")
        return

    if args.list_online:
        if not automation:
            print("No Zenodo token")
            return
        for v in fetch_online_canon_versions(automation):
            print(f"v{v.version} [{v.state}]: {v.doi or '-'} {v.title[:60]}")
        return

    if args.compare:
        local = scan_local_canon_versions()
        online = fetch_online_canon_versions(automation, local) if automation else []
        for s in compare_versions(local, online):
            flag = ""
            if s.errors:
                flag = " [FOUT]"
            print(f"v{s.version}: {s.status}{flag} — {s.message}")
            for err in s.errors:
                print(f"    ! {err}")
        return

    if args.version and args.render_only:
        r = render_version_pdf(args.version, dry_run=args.dry_run)
    elif args.version and args.mint_doi:
        r = mint_version_doi(args.version, dry_run=args.dry_run)
    elif args.version and args.push_metadata:
        r = push_published_metadata(
            args.version,
            dry_run=args.dry_run,
            publish=not args.no_publish,
        )
    elif args.version:
        r = push_version_as_draft(args.version, dry_run=args.dry_run, publish=args.publish)
    else:
        to_version = args.to_version or latest_canon_version()
        results = push_versions_range(args.from_version, to_version, args.dry_run, args.publish)
        for r in results:
            print(f"v{r.version}: {'OK' if r.success else 'FAIL'} — {r.message}")
        return

    print(f"{'OK' if r.success else 'FAIL'}: {r.message}")
    for a in r.actions:
        print(f"  - {a}")
    if r.html_url:
        print(f"  URL: {r.html_url}")
    sys.exit(0 if r.success else 1)


if __name__ == '__main__':
    main()
