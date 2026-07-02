#!/usr/bin/env python3
"""
SST Canon Zenodo publishing: scan local/online versions, push as draft.
"""

from __future__ import annotations

import argparse
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
    pdf_doi_matches,
    process_config_file,
    read_doi_from_pdf,
    resolve_pdf_path,
)
from zenodo_automation import ZenodoAutomation, get_papers_dir, read_token_from_zenodo_py

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
LATEST_ONLINE_DOI = "10.5281/zenodo.19682949"  # current head (v0.8.1) on Zenodo
CONCEPT_DOI = "10.5281/zenodo.16934535"  # version-family concept DOI
CANON_SUBTITLE = "Canonical Reference and Research Framework"

EDITION_CHANGELOG: dict[str, str] = {
    "0.8.2": "Horn/circulation radius, envelope density, highres terminology",
    "0.8.3": "Framed-tube ontology, trefoil closure, particle dictionary, Pauli a_core",
    "0.8.4": "EM–gravity bridge, finite-cell α obstruction, research-track extensions",
    "0.8.5": "Highres conversation audit + CALIBRATED circularity honesty",
    "0.8.6": "Framed self-linking / spinorial lepton ladder (subsec:framed_selflinking_spinorial)",
    "0.8.7": "Z₂ spinstats / CP¹ substrate paragraph + bibliography",
    "0.8.8": "Gemini epistemic/notation audit (P_cal, a_cut, etc.)",
    "0.8.9": "Triadic gravity-response corollary + flame/caustic/shell research-track diagnostics",
    "0.8.10": "Gemini round-2: vchar/uswirl discipline, delay sign, epistemic relabeling",
    "0.8.11": "Final hygiene: consistent P_cal, EMG/RT notation cleanup",
    "0.8.12": "Gemini round-3: epistemic relabels, Pauli a_cut, galaxy rhoF caveat",
}

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


def been_processed_root() -> Path:
    return get_papers_dir() / "SST-CANON" / "been_processed"


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
    return None


def parse_version_from_entry(entry: dict) -> Optional[str]:
    meta = entry.get('metadata', entry)
    version_field = meta.get('version', '') or entry.get('version', '')
    if version_field:
        m = re.search(r'0\.8\.\d+', str(version_field))
        if m:
            return m.group(0)
    return parse_version_from_title(meta.get('title', '') or entry.get('title', ''))


def canon_title(version: str) -> str:
    return f"Swirl-String-Theory Canon v{version} — {CANON_SUBTITLE}"


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
    # Double backslashes: re.sub still interprets \p in \paperdoi as invalid escape
    replacement = r'\\newcommand{\\paperdoi}{' + doi + r'}'
    content = re.sub(
        r'\\newcommand\{\\paperdoi\}\{[^}]+\}',
        replacement,
        content,
    )
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

    cfg_data = read_config_data(version) if loc.has_config else {}
    expected_doi = (cfg_data.get('doi') or doi).strip()

    if loc.has_config and expected_doi and loc.has_tex:
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

    return can_push, can_mint_doi and not can_push, errors


def build_changelog_html(up_to_version: str) -> str:
    lines = ['<hr>', '<h3>Version changelog</h3>', '<ul>']
    for ver, desc in sorted(EDITION_CHANGELOG.items(), key=lambda x: version_sort_key(x[0])):
        if version_sort_key(ver) > version_sort_key(up_to_version):
            break
        lines.append(f'<li><strong>v{ver}</strong> — {desc}</li>')
    lines.append('</ul>')
    return '\n'.join(lines)


def build_description(version: str, abstract: str, base_description: str = "") -> str:
    intro = base_description.strip() if base_description else ""
    if abstract and abstract not in intro:
        if intro:
            intro += f"\n<p>{abstract}</p>"
        else:
            intro = f"<p>{abstract}</p>"
    changelog = build_changelog_html(version)
    if intro:
        return intro + "\n" + changelog
    return changelog


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


def fetch_online_canon_versions(
    automation: ZenodoAutomation,
    local: Optional[list[CanonVersionInfo]] = None,
) -> list[CanonVersionInfo]:
    versions: list[CanonVersionInfo] = []
    raw = automation.list_record_versions(LATEST_ONLINE_DOI)
    for entry in raw:
        title = entry.get('title', '')
        if 'canon' not in title.lower() and 'swirl-string' not in title.lower():
            continue
        version = parse_version_from_entry(entry)
        if not version:
            continue
        is_published = entry.get('is_published', False)
        state = 'published' if is_published else 'draft'
        links = entry.get('links', {})
        html_url = links.get('html', links.get('self_html', ''))
        if not html_url and entry.get('id'):
            html_url = f"{automation.base_url}/records/{entry['id']}"
        versions.append(CanonVersionInfo(
            version=version,
            source='online',
            title=title,
            doi=entry.get('doi', ''),
            deposit_id=str(entry.get('id', '')),
            html_url=html_url,
            state=state,
            publication_date=entry.get('publication_date', ''),
        ))

    versions = overlay_local_deposit_versions(versions, local)

    # De-duplicate: keep latest entry per version (draft wins over older published)
    by_version: dict[str, CanonVersionInfo] = {}
    for v in versions:
        existing = by_version.get(v.version)
        if not existing:
            by_version[v.version] = v
        elif v.state == 'draft':
            by_version[v.version] = v
        elif version_sort_key(v.version) >= version_sort_key(existing.version):
            by_version[v.version] = v

    versions = sorted(by_version.values(), key=lambda v: version_sort_key(v.version))
    return versions


def compare_versions(
    local: list[CanonVersionInfo],
    online: list[CanonVersionInfo],
) -> list[VersionStatus]:
    local_map = {v.version: v for v in local}
    online_map = {v.version: v for v in online}
    all_versions = sorted(set(local_map) | set(online_map), key=version_sort_key)
    duplicates = find_duplicate_local_dois(local)

    statuses: list[VersionStatus] = []
    for ver in all_versions:
        loc = local_map.get(ver)
        on = online_map.get(ver)
        can_push, can_mint, errors = (False, False, [])
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
            if stale_pdf:
                status = 'stale_pdf'
                msg = "PDF-DOI wijkt af van tex — render eerst opnieuw"
            elif on.state == 'draft':
                status = 'draft_online'
                msg = f"v{ver} heeft draft op Zenodo"
            elif can_push:
                status = 'ready_to_push'
                msg = f"v{ver} klaar om te pushen (unieke DOI + config)"
            elif loc.doi and on.doi and loc.doi == on.doi:
                status = 'synced'
                msg = f"v{ver} gesynchroniseerd (DOI match)"
            else:
                status = 'synced'
                msg = f"v{ver} lokaal en online aanwezig"
        elif loc and not on:
            if stale_pdf:
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

        if errors and status not in ('duplicate_doi', 'missing_config', 'stale_pdf'):
            msg = errors[0]

        statuses.append(VersionStatus(
            version=ver,
            status=status,
            local=loc,
            online=on,
            message=msg,
            errors=errors,
            can_push=can_push,
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
    latest = automation.fetch_record_by_doi(LATEST_ONLINE_DOI)
    if latest:
        return str(latest.get('id', ''))
    root = automation.fetch_record_by_doi(ROOT_DOI)
    if root:
        return str(root.get('id', ''))
    return automation._record_id_from_doi(LATEST_ONLINE_DOI)


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
        "creators": DEFAULT_CREATORS,
        "description": description,
        "keywords": [
            "Swirl String Theory",
            "Canon",
            "Theoretical Physics",
            "Formal Systems",
        ],
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
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    """Create a new Zenodo version draft, assign unique DOI to tex, write .zenodo.json (no PDF upload)."""
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PushResult(version=version, success=False)

    if version not in EDITION_CHANGELOG:
        result.message = f"Unknown version {version}"
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
    if cfg_existing.get('deposit_id') and cfg_existing.get('doi'):
        _, _, errors = validate_version_for_push(version, local_versions, online_versions)
        if not errors:
            result.message = f"v{version} heeft al unieke DOI en config ({cfg_existing.get('doi')})"
            result.doi = cfg_existing.get('doi', '')
            result.deposit_id = str(cfg_existing.get('deposit_id', ''))
            return result

    meta = extract_metadata_from_latex(tex)
    abstract = meta.get('description', '')
    base_desc = ""
    if automation:
        parent_record = automation.fetch_record_by_doi(LATEST_ONLINE_DOI)
        if parent_record:
            base_desc = parent_record.get('metadata', {}).get('description', '')
    description = build_description(version, abstract, base_desc)
    papers_dir = get_papers_dir()
    tex_rel = str(tex.relative_to(papers_dir))

    if dry_run:
        parent_id = (
            find_parent_record_id(version, online_versions, automation, local_versions)
            if automation else LATEST_ONLINE_DOI.split('.')[-1]
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
            result.message = "Failed to create new Zenodo version"
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

    result.success = True
    result.message = f"Unieke DOI en config aangemaakt voor v{version}"
    result.deposit_id = deposit_id
    result.doi = doi
    result.html_url = html_url or f"https://zenodo.org/deposit/{deposit_id}"
    return result


def render_version_pdf(
    version: str,
    dry_run: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PushResult:
    """Compile LaTeX to PDF locally and verify DOI matches tex/config (no Zenodo upload)."""
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

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
        return result

    result.success = True
    result.message = f"PDF gerenderd met DOI {expected_doi}"
    result.doi = expected_doi
    result.actions.append(f"PDF DOI verified: {expected_doi}")
    log(result.message)
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

    if version not in EDITION_CHANGELOG:
        result.message = f"Unknown version {version}"
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
    base_desc = ""
    if automation:
        parent_record = automation.fetch_record_by_doi(LATEST_ONLINE_DOI)
        if parent_record:
            base_desc = parent_record.get('metadata', {}).get('description', '')
    description = build_description(version, abstract, base_desc)
    papers_dir = get_papers_dir()

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
    tex_rel = str(tex.relative_to(papers_dir))
    write_zenodo_config(version, deposit_id, doi, description, tex_rel)
    result.actions.append(f'Updated config {cfg_file.name}')

    log("Rendering PDF and uploading to Zenodo...")
    proc = process_config_file(cfg_file, automation, papers_dir)
    if proc['status'] != 'success':
        result.message = proc.get('message', 'Render/upload failed')
        result.actions.extend(proc.get('actions', []))
        return result
    result.actions.extend(proc.get('actions', []))

    html_url = f"https://zenodo.org/deposit/{deposit_id}"

    if publish:
        log("Publishing deposit...")
        if automation.publish_deposit(deposit_id):
            result.actions.append('Published on Zenodo')
        else:
            result.message = "Upload OK but publish failed"
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

    for ver in sorted(EDITION_CHANGELOG.keys(), key=version_sort_key):
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
    parser.add_argument('--to', dest='to_version', default='0.8.12', help='End version')
    parser.add_argument('--dry-run', action='store_true', help='Show actions without API calls')
    parser.add_argument('--publish', action='store_true', help='Publish after upload (default: draft)')
    parser.add_argument('--list-local', action='store_true', help='List local canon versions')
    parser.add_argument('--list-online', action='store_true', help='List online canon versions')
    parser.add_argument('--compare', action='store_true', help='Compare local vs online')
    parser.add_argument('--mint-doi', action='store_true', help='Mint unique DOI + create config (no PDF upload)')
    parser.add_argument('--render-only', action='store_true', help='Render PDF locally (no Zenodo upload)')
    args = parser.parse_args()

    token = read_token_from_zenodo_py()
    automation = ZenodoAutomation(token, sandbox=False) if token else None

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
    elif args.version:
        r = push_version_as_draft(args.version, dry_run=args.dry_run, publish=args.publish)
    else:
        results = push_versions_range(args.from_version, args.to_version, args.dry_run, args.publish)
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
