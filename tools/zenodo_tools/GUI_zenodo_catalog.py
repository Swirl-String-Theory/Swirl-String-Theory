#!/usr/bin/env python3
"""
GUI catalog of all Zenodo drafts and publications for the authenticated user.

Shows record titles with associated uploaded PDF filenames, views/downloads,
checkbox selection, sortable columns, and multi-delete for drafts.
"""

from __future__ import annotations

import sys
import threading
import tkinter as tk
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from tkinter import ttk, messagebox, scrolledtext

import requests

from zenodo_automation import ZenodoAutomation, read_token_from_zenodo_py

if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

CHECK_ON = '\u2611'
CHECK_OFF = '\u2610'


@dataclass
class ZenodoCatalogEntry:
    deposit_id: str
    record_id: str
    record_title: str
    state: str
    state_label: str
    doi: str
    pdf_names: list[str] = field(default_factory=list)
    other_files: list[str] = field(default_factory=list)
    url: str = ''
    publication_date: str = ''
    created: str = ''
    modified: str = ''
    views: int | None = None
    downloads: int | None = None

    @property
    def pdf_sort_key(self) -> str:
        if self.pdf_names:
            return self.pdf_names[0].casefold()
        return '\uffff'

    @property
    def pdf_display(self) -> str:
        if not self.pdf_names:
            return '(geen PDF)'
        return ', '.join(self.pdf_names)


def pdf_filenames(files: list[dict]) -> list[str]:
    names = [f.get('filename', '') for f in files if f.get('filename', '').lower().endswith('.pdf')]
    return sorted(names, key=str.casefold)


def other_filenames(files: list[dict]) -> list[str]:
    return sorted(
        (f.get('filename', '') for f in files if f.get('filename', '') and not f.get('filename', '').lower().endswith('.pdf')),
        key=str.casefold,
    )


def deposit_state(deposit: dict) -> str:
    raw = deposit.get('state', '') or ''
    submitted = bool(deposit.get('submitted'))
    url = (deposit.get('links', {}) or {}).get('html', '') or ''
    if raw == 'done':
        return 'published'
    if raw in ('unsubmitted', 'inprogress') or not submitted or '/deposit/' in url:
        return 'draft'
    return 'published' if submitted else 'draft'


def deposit_state_label(deposit: dict) -> str:
    raw = deposit.get('state', '') or ''
    labels = {
        'done': 'Published',
        'inprogress': 'Draft (in progress)',
        'unsubmitted': 'Draft (unsubmitted)',
    }
    return labels.get(raw, deposit_state(deposit).capitalize())


def deposit_doi(deposit: dict) -> str:
    metadata = deposit.get('metadata', {}) or {}
    doi = metadata.get('doi', '') or deposit.get('doi', '')
    if doi:
        return doi
    prereserve = metadata.get('prereserve_doi', {}) or {}
    return prereserve.get('doi', '') or ''


def deposit_to_entry(deposit: dict) -> ZenodoCatalogEntry:
    metadata = deposit.get('metadata', {}) or {}
    files = deposit.get('files', []) or []
    links = deposit.get('links', {}) or {}
    return ZenodoCatalogEntry(
        deposit_id=str(deposit.get('id', '')),
        record_id=str(deposit.get('record_id', '') or ''),
        record_title=metadata.get('title', deposit.get('title', 'Untitled')) or 'Untitled',
        state=deposit_state(deposit),
        state_label=deposit_state_label(deposit),
        doi=deposit_doi(deposit),
        pdf_names=pdf_filenames(files),
        other_files=other_filenames(files),
        url=links.get('html', '') or links.get('record_html', '') or '',
        publication_date=metadata.get('publication_date', '') or '',
        created=deposit.get('created', '') or '',
        modified=deposit.get('modified', '') or '',
    )


def fetch_all_deposits(automation: ZenodoAutomation) -> list[dict]:
    url = f"{automation.base_url}/api/deposit/depositions"
    all_deposits: list[dict] = []
    page = 1
    while True:
        params = {
            'size': 100,
            'page': page,
            'sort': 'mostrecent',
            'all_versions': 1,
        }
        response = requests.get(url, headers=automation.headers, params=params, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Zenodo API {response.status_code}: {response.text[:300]}")
        batch = response.json()
        if not batch:
            break
        all_deposits.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return all_deposits


def fetch_record_stats(automation: ZenodoAutomation, record_id: str) -> tuple[int | None, int | None]:
    if not record_id:
        return None, None
    url = f"{automation.base_url}/api/records/{record_id}"
    response = requests.get(url, headers=automation.headers, timeout=30)
    if response.status_code != 200:
        return None, None
    stats = response.json().get('stats') or {}
    views = stats.get('unique_views', stats.get('views'))
    downloads = stats.get('unique_downloads', stats.get('downloads'))
    return views, downloads


def enrich_stats(automation: ZenodoAutomation, entries: list[ZenodoCatalogEntry], max_workers: int = 12) -> None:
    published = [e for e in entries if e.state == 'published' and e.record_id]
    if not published:
        return

    def worker(entry: ZenodoCatalogEntry) -> tuple[str, int | None, int | None]:
        views, downloads = fetch_record_stats(automation, entry.record_id)
        return entry.deposit_id, views, downloads

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(worker, e): e for e in published}
        for future in as_completed(futures):
            deposit_id, views, downloads = future.result()
            for entry in entries:
                if entry.deposit_id == deposit_id:
                    entry.views = views
                    entry.downloads = downloads
                    break


def delete_deposit(automation: ZenodoAutomation, deposit_id: str) -> tuple[bool, str]:
    url = f"{automation.base_url}/api/deposit/depositions/{deposit_id}"
    response = requests.delete(url, headers=automation.headers, timeout=30)
    if response.status_code == 204:
        return True, ''
    return False, f"{response.status_code}: {response.text[:200]}"


def stat_display(value: int | None) -> str:
    return '—' if value is None else str(value)


def stat_sort_key(value: int | None) -> int:
    return -1 if value is None else value


class ZenodoCatalogViewer:
    COLUMNS = ('sel', 'pdf_title', 'record_title', 'state', 'views', 'downloads', 'doi', 'deposit_id')
    SORTABLE = ('pdf_title', 'record_title', 'state', 'views', 'downloads', 'doi', 'deposit_id')

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Zenodo Catalog — Drafts & Publications")
        self.root.geometry("1650x900")

        self.automation: ZenodoAutomation | None = None
        self.entries: list[ZenodoCatalogEntry] = []
        self.filtered_entries: list[ZenodoCatalogEntry] = []
        self.selected_entry: ZenodoCatalogEntry | None = None
        self.checked_ids: set[str] = set()
        self._loading = False
        self._deleting = False
        self.sort_column = 'pdf_title'
        self.sort_reverse = False

        main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)

        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Refresh from Zenodo", command=self.refresh_async).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open in Browser", command=self.open_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Select All", command=self.select_all_visible).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear Checks", command=self.clear_checks).pack(side=tk.LEFT, padx=2)
        self.delete_btn = ttk.Button(toolbar, text="Delete Checked", command=self.delete_checked_async)
        self.delete_btn.pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="Filter:").pack(side=tk.LEFT, padx=(12, 4))
        self.filter_var = tk.StringVar(value='all')
        for label, value in [('Alles', 'all'), ('Draft', 'draft'), ('Published', 'published')]:
            ttk.Radiobutton(
                toolbar, text=label, value=value, variable=self.filter_var, command=self.apply_filter
            ).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="Zoek:").pack(side=tk.LEFT, padx=(12, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *_: self.apply_filter())
        ttk.Entry(toolbar, textvariable=self.search_var, width=24).pack(side=tk.LEFT, padx=2)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_hscroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.COLUMNS,
            show='headings',
            selectmode='extended',
            yscrollcommand=tree_vscroll.set,
            xscrollcommand=tree_hscroll.set,
        )
        tree_vscroll.config(command=self.tree.yview)
        tree_hscroll.config(command=self.tree.xview)
        tree_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        headings = {
            'sel': '',
            'pdf_title': 'PDF titel',
            'record_title': 'Zenodo titel',
            'state': 'Status',
            'views': 'Views',
            'downloads': 'Downloads',
            'doi': 'DOI',
            'deposit_id': 'Deposit ID',
        }
        widths = {
            'sel': 36,
            'pdf_title': 240,
            'record_title': 360,
            'state': 120,
            'views': 70,
            'downloads': 80,
            'doi': 180,
            'deposit_id': 90,
        }
        for col in self.COLUMNS:
            self.tree.heading(col, text=headings[col], anchor=tk.W, command=lambda c=col: self.sort_by(c))
            stretch = col in ('pdf_title', 'record_title')
            self.tree.column(col, width=widths[col], minwidth=40, stretch=stretch, anchor=tk.W)

        self.tree.tag_configure('draft', foreground='#b45309')
        self.tree.tag_configure('published', foreground='#15803d')
        self.tree.tag_configure('no_pdf', foreground='#6b7280')
        self.tree.tag_configure('checked', background='#eff6ff')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-1>', self.on_tree_click, add=True)
        self.tree.bind('<Button-3>', self.show_context_menu)

        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Toggle Check", command=self.toggle_checked_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Open in Browser", command=self.open_selected)
        self.context_menu.add_command(label="Copy DOI", command=self.copy_doi)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Checked", command=self.delete_checked_async)

        self.summary_label = ttk.Label(left_frame, text="")
        self.summary_label.pack(anchor=tk.W, padx=5, pady=(0, 5))

        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Details", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=5)
        self.details_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=20)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        log_frame = ttk.LabelFrame(right_frame, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.refresh_async()

    def log(self, message: str) -> None:
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def _get_automation(self) -> ZenodoAutomation:
        if self.automation:
            return self.automation
        token = read_token_from_zenodo_py()
        if not token:
            raise RuntimeError("Geen Zenodo token. Zet key in zenodo.py of geef --token.")
        self.automation = ZenodoAutomation(token, sandbox=False)
        return self.automation

    def _update_heading_indicators(self) -> None:
        labels = {
            'sel': '',
            'pdf_title': 'PDF titel',
            'record_title': 'Zenodo titel',
            'state': 'Status',
            'views': 'Views',
            'downloads': 'Downloads',
            'doi': 'DOI',
            'deposit_id': 'Deposit ID',
        }
        for col in self.SORTABLE:
            text = labels[col]
            if col == self.sort_column:
                text += ' \u25bc' if self.sort_reverse else ' \u25b2'
            self.tree.heading(col, text=text)

    def sort_by(self, column: str) -> None:
        if column not in self.SORTABLE:
            return
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.apply_filter()

    def _sort_entries(self, entries: list[ZenodoCatalogEntry]) -> list[ZenodoCatalogEntry]:
        reverse = self.sort_reverse

        def key(entry: ZenodoCatalogEntry):
            col = self.sort_column
            if col == 'pdf_title':
                return entry.pdf_sort_key
            if col == 'record_title':
                return entry.record_title.casefold()
            if col == 'state':
                return entry.state_label.casefold()
            if col == 'views':
                return stat_sort_key(entry.views)
            if col == 'downloads':
                return stat_sort_key(entry.downloads)
            if col == 'doi':
                return entry.doi.casefold()
            if col == 'deposit_id':
                try:
                    return int(entry.deposit_id)
                except ValueError:
                    return entry.deposit_id
            return entry.pdf_sort_key

        return sorted(entries, key=key, reverse=reverse)

    def refresh_async(self) -> None:
        if self._loading:
            return
        self._loading = True
        self.status_bar.config(text="Ophalen van Zenodo...")
        self.summary_label.config(text="Laden...")

        def worker() -> None:
            error: str | None = None
            entries: list[ZenodoCatalogEntry] = []
            try:
                automation = self._get_automation()
                deposits = fetch_all_deposits(automation)
                entries = [deposit_to_entry(d) for d in deposits]
                enrich_stats(automation, entries)
            except Exception as exc:
                error = str(exc)

            def finish() -> None:
                self._loading = False
                if error:
                    self.status_bar.config(text="Fout bij ophalen")
                    messagebox.showerror("Zenodo", error)
                    self.log(f"✗ {error}")
                    return
                self.entries = entries
                self.log(f"✓ {len(entries)} deposits opgehaald (stats voor published records)")
                self.apply_filter()
                self.status_bar.config(text=f"Klaar — {len(entries)} deposits")

            self.root.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def apply_filter(self) -> None:
        mode = self.filter_var.get()
        query = self.search_var.get().strip().casefold()

        filtered: list[ZenodoCatalogEntry] = []
        for entry in self.entries:
            if mode == 'draft' and entry.state != 'draft':
                continue
            if mode == 'published' and entry.state != 'published':
                continue
            if query:
                haystack = ' '.join([
                    entry.pdf_display,
                    entry.record_title,
                    entry.doi,
                    entry.deposit_id,
                    entry.state,
                    stat_display(entry.views),
                    stat_display(entry.downloads),
                ]).casefold()
                if query not in haystack:
                    continue
            filtered.append(entry)

        self.filtered_entries = self._sort_entries(filtered)
        self.populate_tree(self.filtered_entries)
        self._update_heading_indicators()

    def _check_char(self, deposit_id: str) -> str:
        return CHECK_ON if deposit_id in self.checked_ids else CHECK_OFF

    def populate_tree(self, entries: list[ZenodoCatalogEntry]) -> None:
        self.tree.delete(*self.tree.get_children())
        draft_count = sum(1 for e in entries if e.state == 'draft')
        pub_count = sum(1 for e in entries if e.state == 'published')
        pdf_count = sum(1 for e in entries if e.pdf_names)
        checked_visible = sum(1 for e in entries if e.deposit_id in self.checked_ids)

        for entry in entries:
            if entry.state == 'draft':
                tag = 'draft'
            elif entry.state == 'published':
                tag = 'published'
            else:
                tag = 'no_pdf' if not entry.pdf_names else ''

            if not entry.pdf_names:
                tag = 'no_pdf'

            tags = [tag]
            if entry.deposit_id in self.checked_ids:
                tags.append('checked')

            self.tree.insert(
                '',
                'end',
                iid=entry.deposit_id,
                values=(
                    self._check_char(entry.deposit_id),
                    entry.pdf_display,
                    entry.record_title,
                    entry.state_label,
                    stat_display(entry.views),
                    stat_display(entry.downloads),
                    entry.doi or '—',
                    entry.deposit_id,
                ),
                tags=tuple(tags),
            )

        self.summary_label.config(
            text=(
                f"{len(entries)} records — {pub_count} published, {draft_count} draft, "
                f"{pdf_count} met PDF — {checked_visible} aangevinkt"
            )
        )

    def _entry_by_id(self, deposit_id: str) -> ZenodoCatalogEntry | None:
        for entry in self.filtered_entries:
            if entry.deposit_id == deposit_id:
                return entry
        for entry in self.entries:
            if entry.deposit_id == deposit_id:
                return entry
        return None

    def _toggle_check(self, deposit_id: str) -> None:
        if deposit_id in self.checked_ids:
            self.checked_ids.discard(deposit_id)
        else:
            self.checked_ids.add(deposit_id)
        self.populate_tree(self.filtered_entries)
        self._update_heading_indicators()

    def on_tree_click(self, event) -> str | None:
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return None
        column = self.tree.identify_column(event.x)
        if column != '#1':
            return None
        row = self.tree.identify_row(event.y)
        if not row:
            return None
        self._toggle_check(row)
        return 'break'

    def on_double_click(self, event) -> None:
        column = self.tree.identify_column(event.x)
        if column == '#1':
            return
        self.open_selected()

    def select_all_visible(self) -> None:
        for entry in self.filtered_entries:
            self.checked_ids.add(entry.deposit_id)
        self.populate_tree(self.filtered_entries)

    def clear_checks(self) -> None:
        self.checked_ids.clear()
        self.populate_tree(self.filtered_entries)

    def toggle_checked_selected(self) -> None:
        for deposit_id in self.tree.selection():
            self._toggle_check(deposit_id)

    def on_select(self, _event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            self.selected_entry = None
            self.details_text.delete(1.0, tk.END)
            return
        entry = self._entry_by_id(sel[0])
        self.selected_entry = entry
        if entry:
            self.show_details(entry)

    def show_details(self, entry: ZenodoCatalogEntry) -> None:
        self.details_text.delete(1.0, tk.END)
        lines = [
            f"PDF bestand(en): {entry.pdf_display}",
            f"Zenodo titel: {entry.record_title}",
            f"Status: {entry.state_label} ({entry.state})",
            f"Views (unique): {stat_display(entry.views)}",
            f"Downloads (unique): {stat_display(entry.downloads)}",
            f"DOI: {entry.doi or '—'}",
            f"Deposit ID: {entry.deposit_id}",
            f"Record ID: {entry.record_id or '—'}",
            f"Publicatiedatum: {entry.publication_date or '—'}",
            f"Aangemaakt: {entry.created or '—'}",
            f"Gewijzigd: {entry.modified or '—'}",
            f"URL: {entry.url or '—'}",
        ]
        if entry.state == 'published':
            lines.append("")
            lines.append("Verwijderen: gepubliceerde records niet via API (alleen Zenodo UI/support).")
        else:
            lines.append("")
            lines.append("Verwijderen: draft kan via 'Delete Checked' worden verwijderd.")
        if entry.other_files:
            lines.append("")
            lines.append("Overige bestanden:")
            for name in entry.other_files:
                lines.append(f"  • {name}")
        self.details_text.insert(1.0, '\n'.join(lines))

    def open_selected(self) -> None:
        if not self.selected_entry:
            return
        url = self.selected_entry.url
        if not url and self.selected_entry.deposit_id:
            base = self.automation.base_url if self.automation else 'https://zenodo.org'
            if self.selected_entry.state == 'published':
                rid = self.selected_entry.record_id or self.selected_entry.deposit_id
                url = f"{base}/records/{rid}"
            else:
                url = f"{base}/deposit/{self.selected_entry.deposit_id}"
        if url:
            webbrowser.open(url)
            self.log(f"Opened: {url}")
        else:
            messagebox.showinfo("Geen URL", "Geen Zenodo-URL voor deze selectie")

    def copy_doi(self) -> None:
        if not self.selected_entry or not self.selected_entry.doi:
            messagebox.showinfo("Geen DOI", "Geen DOI voor deze selectie")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.selected_entry.doi)
        self.log(f"Copied DOI: {self.selected_entry.doi}")

    def _checked_entries(self) -> list[ZenodoCatalogEntry]:
        result: list[ZenodoCatalogEntry] = []
        for deposit_id in self.checked_ids:
            entry = self._entry_by_id(deposit_id)
            if entry:
                result.append(entry)
        return result

    def delete_checked_async(self) -> None:
        if self._deleting or self._loading:
            return
        targets = self._checked_entries()
        if not targets:
            messagebox.showwarning("Geen selectie", "Vink eerst één of meer rijen aan om te verwijderen.")
            return

        drafts = [e for e in targets if e.state == 'draft']
        published = [e for e in targets if e.state == 'published']

        msg = f"{len(targets)} record(s) aangevinkt.\n"
        msg += f"  • {len(drafts)} draft(s) kunnen via API worden verwijderd\n"
        if published:
            msg += f"  • {len(published)} published record(s) worden overgeslagen (niet via API)\n"
        msg += "\nDoorgaan met verwijderen van drafts?"
        if not drafts:
            messagebox.showinfo(
                "Geen drafts",
                "Alleen drafts kunnen via de API worden verwijderd.\n"
                "Gepubliceerde records: gebruik Zenodo UI of support.",
            )
            return
        if not messagebox.askyesno("Bevestig verwijderen", msg):
            return

        self._deleting = True
        self.delete_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Verwijderen...")

        def worker() -> None:
            automation = self._get_automation()
            deleted: list[str] = []
            failed: list[tuple[str, str]] = []
            for entry in drafts:
                ok, err = delete_deposit(automation, entry.deposit_id)
                if ok:
                    deleted.append(entry.deposit_id)
                else:
                    failed.append((entry.deposit_id, err))

            def finish() -> None:
                self._deleting = False
                self.delete_btn.config(state=tk.NORMAL)
                for deposit_id in deleted:
                    self.checked_ids.discard(deposit_id)
                self.entries = [e for e in self.entries if e.deposit_id not in deleted]
                self.apply_filter()
                self.log(f"✓ {len(deleted)} draft(s) verwijderd")
                for deposit_id, err in failed:
                    self.log(f"✗ {deposit_id}: {err}")
                if published:
                    self.log(f"⊘ {len(published)} published record(s) overgeslagen")
                summary = f"Verwijderd: {len(deleted)}"
                if failed:
                    summary += f", mislukt: {len(failed)}"
                self.status_bar.config(text=summary)
                if failed:
                    messagebox.showwarning("Gedeeltelijk gelukt", summary)
                else:
                    messagebox.showinfo("Klaar", summary)

            self.root.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def show_context_menu(self, event) -> None:
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.tree.focus(item)
            self.on_select()
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()


def main() -> None:
    root = tk.Tk()
    ZenodoCatalogViewer(root)
    root.mainloop()


if __name__ == '__main__':
    main()
