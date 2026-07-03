#!/usr/bin/env python3
"""
Paper-level Zenodo publishing workflow for GUI_zenodo.py.

Separate from publish_canon_zenodo.py (canon version family).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from create_zenodo_configs import add_doi_to_latex, extract_metadata_from_latex
from render_and_update_zenodo import (
    compile_latex,
    pdf_doi_matches,
    process_config_file,
    resolve_pdf_path,
    update_zenodo_metadata,
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


@dataclass
class PaperWorkflowStatus:
    config_file: Path
    tex_file: Optional[Path] = None
    deposit_id: str = ""
    doi: str = ""
    zenodo_state: str = "none"  # draft | published | unknown | none
    message: str = ""
    can_mint_doi: bool = False
    can_render: bool = False
    can_push: bool = False
    can_push_metadata: bool = False
    can_publish: bool = False
    errors: list[str] = field(default_factory=list)
    html_url: str = ""


@dataclass
class PaperResult:
    success: bool
    message: str = ""
    doi: str = ""
    deposit_id: str = ""
    html_url: str = ""
    actions: list[str] = field(default_factory=list)


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


def read_config_data(config_file: Path) -> dict:
    if not config_file.is_file():
        return {}
    try:
        return json.loads(config_file.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_tex_file(config_file: Path, papers_dir: Path) -> Optional[Path]:
    cfg = read_config_data(config_file)
    tex_rel = cfg.get('tex_file', '')
    if tex_rel:
        tex = papers_dir / tex_rel
        if tex.is_file():
            return tex
    tex = config_file.with_suffix('.tex')
    if tex.is_file():
        return tex
    parent_tex = config_file.parent / f"{config_file.parent.name}.tex"
    if parent_tex.is_file():
        return parent_tex
    stem_tex = config_file.parent / f"{config_file.stem.replace('.zenodo', '')}.tex"
    if stem_tex.is_file():
        return stem_tex
    return None


def fetch_deposit_state(
    automation: Optional[ZenodoAutomation],
    deposit_id: str,
    doi: str,
) -> str:
    if not automation:
        return "unknown"
    if doi:
        if automation.fetch_record_by_doi(doi):
            return "published"
    if not deposit_id:
        return "none"
    dep = automation.get_deposit_info(deposit_id)
    if not dep:
        if doi and automation.fetch_record_by_doi(doi):
            return "published"
        return "unknown"
    if dep.get('submitted', False):
        return "published"
    state = dep.get('state', '')
    if state in ('done', 'published'):
        return "published"
    return "draft"


def zenodo_html_url(deposit_id: str, state: str, automation: Optional[ZenodoAutomation]) -> str:
    if not deposit_id:
        return ""
    if state == "published":
        return f"{automation.base_url}/records/{deposit_id}" if automation else f"https://zenodo.org/records/{deposit_id}"
    return f"{automation.base_url}/deposit/{deposit_id}" if automation else f"https://zenodo.org/deposit/{deposit_id}"


def assess_paper(
    config_file: Path,
    papers_dir: Path,
    automation: Optional[ZenodoAutomation] = None,
) -> PaperWorkflowStatus:
    status = PaperWorkflowStatus(config_file=config_file.resolve())
    errors: list[str] = []

    if not config_file.is_file():
        status.message = "Config bestand niet gevonden"
        status.errors = ["Geen .zenodo.json"]
        return status

    cfg = read_config_data(config_file)
    tex = resolve_tex_file(config_file, papers_dir)
    status.tex_file = tex

    deposit_id = str(cfg.get('deposit_id', ''))
    config_doi = (cfg.get('doi') or '').strip()
    tex_doi = read_doi_from_tex(tex) if tex else ""
    doi = config_doi or tex_doi
    status.deposit_id = deposit_id
    status.doi = doi

    if not tex:
        errors.append("Geen .tex bestand gevonden")

    zenodo_state = fetch_deposit_state(automation, deposit_id, doi)
    status.zenodo_state = zenodo_state
    status.html_url = zenodo_html_url(deposit_id, zenodo_state, automation)

    if config_doi and tex_doi and config_doi != tex_doi:
        errors.append(f"DOI mismatch: config ({config_doi}) vs tex ({tex_doi})")

    if not deposit_id and not doi:
        status.can_mint_doi = bool(tex)
        status.message = "Mint DOI + config aanmaken" if tex else "Geen tex voor mint"
        status.errors = errors
        return status

    if not deposit_id:
        errors.append("Config mist deposit_id — mint DOI")
        status.can_mint_doi = True

    if zenodo_state == "published" and doi:
        status.can_push = False
        status.can_publish = False
        if not errors and deposit_id:
            status.can_push_metadata = True
            status.message = "Gepubliceerd — metadata kan worden bijgewerkt"
        else:
            status.message = "Gepubliceerd" + (f" — {errors[0]}" if errors else "")
    elif zenodo_state == "draft" and deposit_id and doi:
        status.can_push_metadata = False
        if not errors:
            cfg_for_pdf = cfg if cfg else {}
            if tex:
                pdf = resolve_pdf_path(tex, cfg_for_pdf)
                if not pdf.is_file():
                    errors.append("Geen PDF — render eerst")
                else:
                    matches, found = pdf_doi_matches(pdf, doi)
                    if not matches:
                        if found:
                            errors.append(f"PDF DOI ({found}) wijkt af van {doi}")
                        else:
                            errors.append(f"Geen DOI in PDF (verwacht {doi})")
            status.can_push = len(errors) == 0
            status.can_publish = len(errors) == 0
            status.message = "Draft — klaar om te pushen/publiceren" if status.can_push else errors[0] if errors else "Draft"
        else:
            status.message = errors[0]
    elif zenodo_state == "unknown" and deposit_id:
        status.message = "Zenodo status onbekend"
        if not errors and tex and doi:
            status.can_render = True
    else:
        status.message = "Lokaal aanwezig, nog niet op Zenodo" if not deposit_id else "Status onbekend"

    if tex and doi and zenodo_state != "published":
        cfg_for_pdf = cfg if cfg else {}
        pdf = resolve_pdf_path(tex, cfg_for_pdf)
        if not pdf.is_file():
            status.can_render = True
        else:
            matches, _ = pdf_doi_matches(pdf, doi)
            status.can_render = not matches

    if tex and not doi:
        status.can_mint_doi = True

    status.errors = errors
    return status


def _build_config_from_metadata(
    config_file: Path,
    papers_dir: Path,
    tex_file: Path,
    metadata: dict,
    deposit_id: str,
    doi: str,
) -> dict:
    existing = read_config_data(config_file)
    tex_rel = str(tex_file.relative_to(papers_dir)).replace('\\', '/')
    data = {
        "title": metadata.get('title') or existing.get('title', 'Untitled'),
        "creators": metadata.get('creators') or existing.get('creators', []),
        "description": metadata.get('description') or existing.get('description', ''),
        "keywords": metadata.get('keywords') or existing.get('keywords', []),
        "upload_type": existing.get('upload_type', 'publication'),
        "publication_type": existing.get('publication_type', 'preprint'),
        "publication_date": metadata.get('publication_date') or existing.get('publication_date') or datetime.now().strftime('%Y-%m-%d'),
        "language": existing.get('language', 'eng'),
        "access_right": existing.get('access_right', 'open'),
        "license": existing.get('license', 'cc-by-4.0'),
        "doi": doi,
        "deposit_id": deposit_id,
        "tex_file": tex_rel,
    }
    if existing.get('communities'):
        data['communities'] = existing['communities']
    if existing.get('related_identifiers'):
        data['related_identifiers'] = existing['related_identifiers']
    if existing.get('pdf_output_dir'):
        data['pdf_output_dir'] = existing['pdf_output_dir']
    if existing.get('compile_timeout'):
        data['compile_timeout'] = existing['compile_timeout']
    return data


def mint_paper_doi(
    config_file: Path,
    papers_dir: Path,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PaperResult:
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PaperResult(success=False)
    tex = resolve_tex_file(config_file, papers_dir)
    if not tex:
        result.message = "Geen .tex bestand gevonden"
        return result

    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)
    elif automation is None and dry_run:
        token = read_token_from_zenodo_py()
        if token:
            automation = ZenodoAutomation(token, sandbox=False)

    metadata = extract_metadata_from_latex(tex)
    if not metadata.get('title'):
        result.message = "Geen titel in LaTeX"
        return result

    existing = assess_paper(config_file, papers_dir, automation)
    if existing.deposit_id and existing.doi and not existing.errors:
        result.success = True
        result.message = f"Heeft al DOI en config ({existing.doi})"
        result.doi = existing.doi
        result.deposit_id = existing.deposit_id
        result.html_url = existing.html_url
        return result

    if dry_run:
        result.success = True
        result.message = "Dry run OK (mint DOI)"
        result.actions = [f"Would create draft for {tex.name}", f"Would write {config_file.name}"]
        log(f"[DRY RUN mint] {config_file.name}: " + "; ".join(result.actions))
        return result

    log(f"Creating Zenodo draft for {tex.name}...")
    deposit_id = automation.create_draft_deposit(metadata)
    if not deposit_id:
        result.message = "Failed to create Zenodo draft"
        return result
    result.actions.append('Created Zenodo draft')

    doi = automation.get_prereserved_doi(deposit_id) or automation.get_deposit_doi(deposit_id) or ""
    if not doi:
        result.message = "Draft created but no DOI returned"
        result.deposit_id = deposit_id
        return result

    log(f"DOI: {doi}")
    if add_doi_to_latex(tex, doi):
        result.actions.append('Updated DOI in LaTeX')

    cfg_data = _build_config_from_metadata(config_file, papers_dir, tex, metadata, deposit_id, doi)
    config_file.write_text(json.dumps(cfg_data, indent=2, ensure_ascii=False), encoding='utf-8')
    result.actions.append(f'Wrote {config_file.name}')

    dep = automation.get_deposit_info(deposit_id)
    html_url = dep.get('links', {}).get('html', '') if dep else ''
    result.success = True
    result.message = "DOI en config aangemaakt"
    result.doi = doi
    result.deposit_id = deposit_id
    result.html_url = html_url or f"https://zenodo.org/deposit/{deposit_id}"
    return result


def render_paper_pdf(
    config_file: Path,
    papers_dir: Path,
    dry_run: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PaperResult:
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PaperResult(success=False)
    tex = resolve_tex_file(config_file, papers_dir)
    if not tex:
        result.message = "Geen .tex bestand gevonden"
        return result

    cfg = read_config_data(config_file)
    expected_doi = (cfg.get('doi') or read_doi_from_tex(tex)).strip()
    if not expected_doi:
        result.message = "Geen DOI — mint eerst DOI"
        return result

    pdf_output_dir = cfg.get('pdf_output_dir', '')
    out_dir = tex.parent / pdf_output_dir if pdf_output_dir else None
    compile_timeout = int(cfg.get('compile_timeout', 120))

    if dry_run:
        result.success = True
        result.message = "Dry run OK (render PDF)"
        result.doi = expected_doi
        return result

    log(f"Rendering PDF for {tex.name}...")
    success, pdf_file = compile_latex(tex, num_passes=2, output_dir=out_dir, timeout=compile_timeout)
    if not success or not pdf_file:
        result.message = "LaTeX compile mislukt"
        return result

    matches, found_doi = pdf_doi_matches(pdf_file, expected_doi)
    if not matches:
        if found_doi:
            result.message = f"PDF bevat verkeerde DOI ({found_doi}); verwacht {expected_doi}"
        else:
            result.message = f"Geen DOI in PDF (verwacht {expected_doi})"
        return result

    result.success = True
    result.message = f"PDF gerenderd met DOI {expected_doi}"
    result.doi = expected_doi
    result.actions.append(f"Compiled {pdf_file.name}")
    return result


def push_paper_as_draft(
    config_file: Path,
    papers_dir: Path,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PaperResult:
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PaperResult(success=False)

    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)
    elif automation is None and dry_run:
        token = read_token_from_zenodo_py()
        if token:
            automation = ZenodoAutomation(token, sandbox=False)

    wf = assess_paper(config_file, papers_dir, automation)
    if wf.zenodo_state == "published":
        result.message = "Gepubliceerd — gebruik Push Metadata (geen PDF)"
        return result
    if not wf.can_push:
        result.message = "Push geblokkeerd"
        result.actions = wf.errors
        for err in wf.errors:
            log(f"✗ {err}")
        return result

    cfg = read_config_data(config_file)
    deposit_id = str(cfg.get('deposit_id', ''))
    doi = cfg.get('doi', '')

    if dry_run:
        result.success = True
        result.message = "Dry run OK (push draft)"
        result.doi = doi
        result.deposit_id = deposit_id
        result.actions = [f"Would render + upload PDF for {config_file.name}"]
        return result

    log("Rendering PDF and uploading to Zenodo...")
    proc = process_config_file(config_file, automation, papers_dir)
    if proc['status'] != 'success':
        result.message = proc.get('message', 'Render/upload failed')
        result.actions = proc.get('actions', [])
        return result

    result.success = True
    result.message = "Draft pushed successfully"
    result.doi = doi
    result.deposit_id = deposit_id
    result.html_url = f"https://zenodo.org/deposit/{deposit_id}"
    result.actions = proc.get('actions', [])
    return result


def push_published_metadata(
    config_file: Path,
    papers_dir: Path,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    publish: bool = True,
    on_log: Optional[Callable[[str], None]] = None,
) -> PaperResult:
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PaperResult(success=False)

    if automation is None:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)

    wf = assess_paper(config_file, papers_dir, automation)
    if wf.zenodo_state != "published":
        result.message = "Niet gepubliceerd — gebruik Push as Draft"
        return result
    if not wf.can_push_metadata:
        result.message = wf.errors[0] if wf.errors else "Metadata-push niet mogelijk"
        return result

    cfg = read_config_data(config_file)
    deposit_id = str(cfg.get('deposit_id', '') or wf.deposit_id)
    doi = cfg.get('doi', '') or wf.doi

    if dry_run:
        result.success = True
        result.message = "Dry run OK (metadata push)"
        result.doi = doi
        result.deposit_id = deposit_id
        result.actions = [
            f"Would edit deposit {deposit_id}",
            "Would update metadata (no PDF)",
            "Would publish" if publish else "Would leave draft after edit",
        ]
        return result

    with open(config_file, encoding='utf-8') as f:
        cfg_data = json.load(f)

    log(f"Opening deposit {deposit_id} for edit...")
    if not automation.edit_deposit(deposit_id):
        result.message = "Kon gepubliceerd record niet openen voor bewerking"
        return result
    result.actions.append('Opened deposit for edit')

    log("Updating Zenodo metadata (no PDF)...")
    if not update_zenodo_metadata(automation, deposit_id, cfg_data):
        result.message = "Metadata-update mislukt"
        return result
    result.actions.append('Updated metadata on Zenodo')

    if publish:
        log("Publishing metadata update...")
        if automation.publish_deposit(deposit_id):
            result.actions.append('Published metadata update')
        else:
            result.message = "Metadata bijgewerkt maar publiceren mislukt"
            result.deposit_id = deposit_id
            result.doi = doi
            result.html_url = wf.html_url
            return result

    result.success = True
    result.message = "Metadata gepubliceerd op Zenodo" if publish else "Metadata bijgewerkt"
    result.deposit_id = deposit_id
    result.doi = doi
    result.html_url = wf.html_url or f"https://zenodo.org/records/{deposit_id}"
    return result


def publish_paper_draft(
    config_file: Path,
    papers_dir: Path,
    automation: Optional[ZenodoAutomation] = None,
    dry_run: bool = False,
    on_log: Optional[Callable[[str], None]] = None,
) -> PaperResult:
    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    result = PaperResult(success=False)

    if automation is None and not dry_run:
        token = read_token_from_zenodo_py()
        if not token:
            result.message = "No Zenodo token found"
            return result
        automation = ZenodoAutomation(token, sandbox=False)
    elif automation is None and dry_run:
        token = read_token_from_zenodo_py()
        if token:
            automation = ZenodoAutomation(token, sandbox=False)

    wf = assess_paper(config_file, papers_dir, automation)
    if wf.zenodo_state == "published":
        result.message = "Al gepubliceerd"
        return result
    if not wf.can_publish:
        result.message = wf.errors[0] if wf.errors else "Publiceren niet mogelijk"
        return result

    deposit_id = wf.deposit_id
    doi = wf.doi

    if dry_run:
        result.success = True
        result.message = "Dry run OK (publish)"
        result.deposit_id = deposit_id
        result.doi = doi
        return result

    log(f"Publishing deposit {deposit_id}...")
    if automation.publish_deposit(deposit_id):
        result.success = True
        result.message = "Gepubliceerd op Zenodo"
        result.deposit_id = deposit_id
        result.doi = doi
        result.html_url = f"https://zenodo.org/records/{deposit_id}"
        result.actions.append('Published on Zenodo')
    else:
        result.message = "Publiceren mislukt"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description='Paper Zenodo workflow')
    parser.add_argument('--config', required=True, help='Path to .zenodo.json')
    parser.add_argument('--mint-doi', action='store_true')
    parser.add_argument('--render-only', action='store_true')
    parser.add_argument('--push-draft', action='store_true')
    parser.add_argument('--push-metadata', action='store_true')
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--no-publish', action='store_true', help='With --push-metadata: skip publish')
    args = parser.parse_args()

    papers_dir = get_papers_dir()
    config_file = Path(args.config)
    if not config_file.is_absolute():
        config_file = papers_dir / config_file

    if args.mint_doi:
        r = mint_paper_doi(config_file, papers_dir, dry_run=args.dry_run)
    elif args.render_only:
        r = render_paper_pdf(config_file, papers_dir, dry_run=args.dry_run)
    elif args.push_draft:
        r = push_paper_as_draft(config_file, papers_dir, dry_run=args.dry_run)
    elif args.push_metadata:
        r = push_published_metadata(
            config_file, papers_dir, dry_run=args.dry_run, publish=not args.no_publish,
        )
    elif args.publish:
        r = publish_paper_draft(config_file, papers_dir, dry_run=args.dry_run)
    else:
        wf = assess_paper(config_file, papers_dir, ZenodoAutomation(read_token_from_zenodo_py(), sandbox=False) if read_token_from_zenodo_py() else None)
        print(f"State: {wf.zenodo_state} — {wf.message}")
        for e in wf.errors:
            print(f"  ! {e}")
        return

    print(f"{'OK' if r.success else 'FAIL'}: {r.message}")
    for a in r.actions:
        print(f"  - {a}")


if __name__ == '__main__':
    main()
