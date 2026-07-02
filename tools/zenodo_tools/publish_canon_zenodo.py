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
from render_and_update_zenodo import process_config_file, resolve_pdf_path
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

PARENT_DOI = "10.5281/zenodo.19655881"  # v0.8.0 published canon
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
    tex_path: Optional[Path] = None
    pdf_path: Optional[Path] = None
    config_path: Optional[Path] = None
    publication_date: str = ""


@dataclass
class VersionStatus:
    version: str
    status: str  # synced | ahead_local | draft_online | online_only | local_only
    local: Optional[CanonVersionInfo] = None
    online: Optional[CanonVersionInfo] = None
    message: str = ""


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
    content = re.sub(
        r'\\newcommand\{\\paperdoi\}\{[^}]+\}',
        f'\\newcommand{{\\paperdoi}}{{{doi}}}',
        content,
    )
    tex_file.write_text(content, encoding='utf-8')


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
                    pass
            pdf = resolve_pdf_path(tex, {'pdf_output_dir': '$out'})
            info.has_pdf = pdf.is_file()
            info.pdf_path = pdf if pdf.is_file() else None
        versions.append(info)
    return versions


def fetch_online_canon_versions(automation: ZenodoAutomation) -> list[CanonVersionInfo]:
    versions: list[CanonVersionInfo] = []
    raw = automation.list_record_versions(PARENT_DOI)
    for entry in raw:
        title = entry.get('title', '')
        if 'canon' not in title.lower() and 'swirl-string' not in title.lower():
            continue
        version = parse_version_from_title(title)
        if not version:
            continue
        is_published = entry.get('is_published', False)
        state = 'published' if is_published else 'draft'
        links = entry.get('links', {})
        html_url = links.get('html', links.get('self_html', ''))
        if not html_url and entry.get('id'):
            html_url = f"{automation.base_url}/record/{entry['id']}"
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

    # Ensure v0.8.0 parent is listed if not in versions API response
    if not any(v.version == '0.8.0' for v in versions):
        parent = automation.fetch_record_by_doi(PARENT_DOI)
        if parent:
            meta = parent.get('metadata', {})
            versions.append(CanonVersionInfo(
                version='0.8.0',
                source='online',
                title=meta.get('title', 'Swirl-String-Theory Canon v0.8.0'),
                doi=meta.get('doi', PARENT_DOI),
                deposit_id=str(parent.get('id', '')),
                html_url=parent.get('links', {}).get('html', ''),
                state='published',
                publication_date=meta.get('publication_date', ''),
            ))

    versions.sort(key=lambda v: version_sort_key(v.version))
    return versions


def compare_versions(
    local: list[CanonVersionInfo],
    online: list[CanonVersionInfo],
) -> list[VersionStatus]:
    local_map = {v.version: v for v in local}
    online_map = {v.version: v for v in online}
    all_versions = sorted(set(local_map) | set(online_map), key=version_sort_key)

    statuses: list[VersionStatus] = []
    for ver in all_versions:
        loc = local_map.get(ver)
        on = online_map.get(ver)
        if loc and on:
            if on.state == 'draft':
                status = 'draft_online'
                msg = f"v{ver} has draft on Zenodo"
            elif loc.doi and on.doi and loc.doi == on.doi:
                status = 'synced'
                msg = f"v{ver} synced (DOI match)"
            else:
                status = 'synced'
                msg = f"v{ver} present locally and on Zenodo"
        elif loc and not on:
            status = 'ahead_local'
            msg = f"v{ver} local only — not on Zenodo yet"
        elif on and not loc:
            status = 'online_only'
            msg = f"v{ver} on Zenodo only"
        else:
            status = 'local_only'
            msg = f"v{ver} unknown"
        statuses.append(VersionStatus(version=ver, status=status, local=loc, online=on, message=msg))
    return statuses


def find_parent_record_id(
    version: str,
    online: list[CanonVersionInfo],
    automation: ZenodoAutomation,
) -> str:
    """Latest published online record id before `version` to branch new version from."""
    candidates = [
        v for v in online
        if version_sort_key(v.version) < version_sort_key(version) and v.deposit_id
    ]
    published = [v for v in candidates if v.state == 'published']
    pool = published if published else candidates
    if pool:
        return pool[-1].deposit_id
    parent = automation.fetch_record_by_doi(PARENT_DOI)
    if parent:
        return str(parent.get('id', ''))
    return automation._record_id_from_doi(PARENT_DOI)


def find_existing_online_draft(version: str, online: list[CanonVersionInfo]) -> Optional[CanonVersionInfo]:
    for v in online:
        if v.version == version and v.state == 'draft':
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
            {"identifier": PARENT_DOI, "relation": "isVersionOf"},
        ],
    }
    cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return cfg


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
        online_versions = fetch_online_canon_versions(automation)
    existing_draft = find_existing_online_draft(version, online_versions)

    meta = extract_metadata_from_latex(tex)
    abstract = meta.get('description', '')
    base_desc = ""
    if automation:
        parent_record = automation.fetch_record_by_doi(PARENT_DOI)
        if parent_record:
            base_desc = parent_record.get('metadata', {}).get('description', '')
    description = build_description(version, abstract, base_desc)

    papers_dir = get_papers_dir()
    tex_rel = str(tex.relative_to(papers_dir))

    if dry_run:
        if automation:
            parent_id = find_parent_record_id(version, online_versions, automation)
        else:
            parent_id = PARENT_DOI.split('.')[-1]
        result.success = True
        result.message = "Dry run OK"
        result.actions = [
            f"Would create new version from record {parent_id}" if not existing_draft else f"Would reuse draft {existing_draft.deposit_id}",
            f"Would update DOI in {tex.name}",
            f"Would render PDF to $out/",
            f"Would upload PDF and metadata (draft={not publish})",
        ]
        log(f"[DRY RUN] v{version}: " + "; ".join(result.actions))
        return result

    deposit_id = ""
    doi = ""
    html_url = ""

    if existing_draft:
        deposit_id = existing_draft.deposit_id
        doi = existing_draft.doi or automation.get_prereserved_doi(deposit_id) or ""
        html_url = existing_draft.html_url
        log(f"Reusing existing draft for v{version}: {deposit_id}")
        result.actions.append('Reused existing Zenodo draft')
    else:
        parent_id = find_parent_record_id(version, online_versions, automation)
        log(f"Creating new Zenodo version from record {parent_id}...")
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

    log("Rendering PDF and uploading to Zenodo...")
    proc = process_config_file(cfg, automation, papers_dir)
    if proc['status'] != 'success':
        result.message = proc.get('message', 'Render/upload failed')
        result.actions.extend(proc.get('actions', []))
        return result
    result.actions.extend(proc.get('actions', []))

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
    args = parser.parse_args()

    token = read_token_from_zenodo_py()
    automation = ZenodoAutomation(token, sandbox=False) if token else None

    if args.list_local:
        for v in scan_local_canon_versions():
            print(f"v{v.version}: tex={v.has_tex} pdf={v.has_pdf} doi={v.doi or '-'}")
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
        online = fetch_online_canon_versions(automation) if automation else []
        for s in compare_versions(local, online):
            print(f"v{s.version}: {s.status} — {s.message}")
        return

    if args.version:
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
