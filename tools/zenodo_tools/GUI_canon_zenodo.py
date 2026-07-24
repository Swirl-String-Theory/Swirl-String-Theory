#!/usr/bin/env python3
"""
SST Canon — Zenodo Version Manager GUI.

Shows online vs local canon versions and pushes selected editions as Zenodo drafts.
"""

from __future__ import annotations

import sys
import threading
import webbrowser

try:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext, simpledialog, ttk
except ImportError:
    print("tkinter is required for GUI_canon_zenodo.py. Install Python with Tcl/Tk support.")
    sys.exit(1)

from publish_canon_zenodo import (
    CanonVersionInfo,
    VersionStatus,
    bind_draft_to_local_version,
    compare_versions,
    fetch_online_canon_versions,
    is_orphan_online_version,
    list_bindable_local_versions,
    list_online_drafts,
    list_online_published,
    local_deposit_is_stale,
    mint_version_doi,
    push_version_as_draft,
    read_config_data,
    render_version_pdf,
    scan_local_canon_versions,
    update_config_no_pdf,
)
from render_and_update_zenodo import (
    expected_canon_pdf_path,
    format_pdf_doi_diagnostics,
    resolve_pdf_path,
)
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

STATUS_COLORS = {
    'synced': '#2e7d32',
    'ready_to_push': '#2e7d32',
    'published': '#1565c0',
    'ahead_local': '#e65100',
    'draft_online': '#1565c0',
    'online_only': '#6a1b9a',
    'local_only': '#757575',
    'duplicate_doi': '#c62828',
    'missing_config': '#c62828',
    'blocked': '#c62828',
    'stale_pdf': '#e65100',
    'stale_deposit': '#c62828',
}


class CanonZenodoGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SST Canon — Zenodo Version Manager")
        self.root.geometry("1280x820")

        self.automation: ZenodoAutomation | None = None
        self.local_versions: list[CanonVersionInfo] = []
        self.online_versions: list[CanonVersionInfo] = []
        self.statuses: list[VersionStatus] = []
        self.selected_version: str | None = None
        self.selected_draft_deposit_id: str | None = None
        self._busy = False
        self._pending_remint_version: str | None = None
        self._syncing_selection = False
        self._last_logged_validation_version: str | None = None

        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=8, pady=6)

        ttk.Label(top, text="SST Canon — Zenodo Version Manager", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.refresh_btn = ttk.Button(top, text="Refresh", command=self.refresh_data)
        self.refresh_btn.pack(side=tk.RIGHT, padx=4)

        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        online_outer = ttk.PanedWindow(paned, orient=tk.VERTICAL)
        paned.add(online_outer, weight=1)

        # Published online
        published_frame = ttk.LabelFrame(online_outer, text="Online — Published")
        online_outer.add(published_frame, weight=2)
        published_cols = ('version', 'doi', 'date')
        self.published_tree = ttk.Treeview(published_frame, columns=published_cols, show='headings', height=8)
        for col, w in zip(published_cols, (80, 220, 90)):
            self.published_tree.heading(col, text=col.capitalize())
            self.published_tree.column(col, width=w, minwidth=50)
        published_scroll = ttk.Scrollbar(published_frame, orient=tk.VERTICAL, command=self.published_tree.yview)
        self.published_tree.configure(yscrollcommand=published_scroll.set)
        self.published_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        published_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=4)

        # Online drafts (separate)
        drafts_frame = ttk.LabelFrame(online_outer, text="Online — Drafts")
        online_outer.add(drafts_frame, weight=1)
        draft_cols = ('version', 'deposit', 'doi', 'title')
        self.drafts_tree = ttk.Treeview(drafts_frame, columns=draft_cols, show='headings', height=6)
        for col, w, label in zip(draft_cols, (90, 90, 180, 220), ('Version', 'Deposit', 'DOI', 'Title')):
            self.drafts_tree.heading(col, text=label)
            self.drafts_tree.column(col, width=w, minwidth=50)
        drafts_scroll = ttk.Scrollbar(drafts_frame, orient=tk.VERTICAL, command=self.drafts_tree.yview)
        self.drafts_tree.configure(yscrollcommand=drafts_scroll.set)
        self.drafts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        drafts_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=4)
        self.drafts_tree.bind('<<TreeviewSelect>>', self._on_draft_select)

        # Local panel
        local_frame = ttk.LabelFrame(paned, text="Lokaal (been_processed)")
        paned.add(local_frame, weight=1)

        local_cols = ('version', 'tex', 'pdf', 'doi', 'config', 'warn')
        self.local_tree = ttk.Treeview(local_frame, columns=local_cols, show='headings', height=14)
        for col, w in zip(local_cols, (70, 40, 40, 180, 50, 40)):
            self.local_tree.heading(col, text=col.capitalize() if col != 'warn' else '!')
            self.local_tree.column(col, width=w, minwidth=40)
        local_scroll = ttk.Scrollbar(local_frame, orient=tk.VERTICAL, command=self.local_tree.yview)
        self.local_tree.configure(yscrollcommand=local_scroll.set)
        self.local_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        local_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=4)

        # Comparison / status
        compare_frame = ttk.LabelFrame(self.root, text="Vergelijking")
        compare_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        compare_cols = ('version', 'status', 'message')
        self.compare_tree = ttk.Treeview(compare_frame, columns=compare_cols, show='headings', height=8)
        self.compare_tree.heading('version', text='Version')
        self.compare_tree.heading('status', text='Status')
        self.compare_tree.heading('message', text='Message')
        self.compare_tree.column('version', width=80)
        self.compare_tree.column('status', width=120)
        self.compare_tree.column('message', width=600)
        self.compare_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.compare_tree.bind('<<TreeviewSelect>>', self._on_compare_select)

        for tag, color in STATUS_COLORS.items():
            self.compare_tree.tag_configure(tag, foreground=color)

        # Actions
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=8, pady=4)

        self.status_label = ttk.Label(action_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=4)

        self.push_btn = ttk.Button(
            action_frame, text="Push Selected as Draft", command=self.push_selected, state=tk.DISABLED
        )
        self.push_btn.pack(side=tk.RIGHT, padx=4)

        self.render_btn = ttk.Button(action_frame, text="Render PDF", command=self.render_selected, state=tk.DISABLED)
        self.render_btn.pack(side=tk.RIGHT, padx=4)

        self.mint_btn = ttk.Button(
            action_frame, text="Mint DOI + Config", command=self.mint_selected, state=tk.DISABLED
        )
        self.mint_btn.pack(side=tk.RIGHT, padx=4)

        self.update_config_btn = ttk.Button(
            action_frame, text="Update Config", command=self.update_config_selected, state=tk.DISABLED
        )
        self.update_config_btn.pack(side=tk.RIGHT, padx=4)

        self.replace_draft_btn = ttk.Button(
            action_frame, text="Replace Draft…", command=self.replace_draft_selected, state=tk.DISABLED
        )
        self.replace_draft_btn.pack(side=tk.RIGHT, padx=4)

        self.open_btn = ttk.Button(action_frame, text="Open Zenodo", command=self.open_draft, state=tk.DISABLED)
        self.open_btn.pack(side=tk.RIGHT, padx=4)

        # Log
        log_frame = ttk.LabelFrame(self.root, text="Action Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        log_toolbar = ttk.Frame(log_frame)
        log_toolbar.pack(fill=tk.X, padx=4, pady=(4, 0))
        self.verbose_errors = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            log_toolbar,
            text="Verbose errors",
            variable=self.verbose_errors,
        ).pack(side=tk.LEFT)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def log(self, msg: str) -> None:
        # Cap log growth so a runaway loop cannot melt the UI/CPU
        try:
            line_count = int(self.log_text.index('end-1c').split('.')[0])
        except (tk.TclError, ValueError, AttributeError):
            line_count = 0
        if line_count > 2000:
            self.log_text.delete('1.0', '1000.0')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        # Do not call update_idletasks() here — it amplifies CPU during log storms.

    def _set_tree_selection(self, tree: ttk.Treeview, item_id: str) -> None:
        """Select a tree item without re-entering selection handlers."""
        if not item_id or not tree.exists(item_id):
            return
        current = tree.selection()
        if current and current[0] == item_id:
            return
        self._syncing_selection = True
        try:
            tree.selection_set(item_id)
            tree.see(item_id)
        finally:
            self._syncing_selection = False

    def _log_validation_once(self, version: str, status: VersionStatus) -> None:
        """Log validation errors at most once per selected version change."""
        if not status.errors:
            return
        if self._last_logged_validation_version == version:
            return
        self._last_logged_validation_version = version
        self.log(f"--- v{version} validatie ---")
        for err in status.errors:
            self.log(f"  ! {err}")
        if self.verbose_errors.get() and self._errors_need_pdf_diagnostics(status.errors):
            loc = next((v for v in self.local_versions if v.version == version), None)
            if loc:
                self._log_pdf_diagnostics(loc)

    @staticmethod
    def _errors_need_pdf_diagnostics(errors: list[str]) -> bool:
        keywords = ('PDF', 'DOI gevonden in PDF', 'verouderde DOI')
        return any(any(keyword in err for keyword in keywords) for err in errors)

    def _needs_pdf_diagnostics(self, loc: CanonVersionInfo, status: VersionStatus | None) -> bool:
        if loc.has_pdf and not loc.pdf_doi_ok:
            return True
        if status and status.status == 'stale_pdf':
            return True
        if status and status.errors and self._errors_need_pdf_diagnostics(status.errors):
            return True
        return False

    def _log_pdf_diagnostics(self, loc: CanonVersionInfo) -> None:
        if not self.verbose_errors.get():
            return
        tex = loc.tex_path
        if not tex or not tex.is_file():
            self.log(f"--- PDF-DOI diagnostiek v{loc.version} ---")
            self.log("  geen .tex bestand beschikbaar")
            return

        cfg_data = read_config_data(loc.version) if loc.has_config else {}
        expected_doi = (cfg_data.get('doi') or loc.doi or '').strip()
        pdf_cfg = cfg_data if cfg_data else {'pdf_output_dir': '$out'}

        pdf = loc.pdf_path
        if not pdf or not pdf.is_file():
            pdf = expected_canon_pdf_path(tex, pdf_cfg)
            if not pdf.is_file():
                pdf = resolve_pdf_path(tex, pdf_cfg)

        self.log(f"--- PDF-DOI diagnostiek v{loc.version} ---")
        for line in format_pdf_doi_diagnostics(
            pdf,
            expected_doi,
            tex_file=tex,
            config_data=pdf_cfg,
        ):
            self.log(f"  {line}")

    def _log_local_diagnostics_if_verbose(self, version: str) -> None:
        if not self.verbose_errors.get():
            return
        loc = next((v for v in self.local_versions if v.version == version), None)
        if loc:
            self._log_pdf_diagnostics(loc)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self.refresh_btn.config(state=state)
        if busy:
            self.push_btn.config(state=tk.DISABLED)
            self.mint_btn.config(state=tk.DISABLED)
            self.render_btn.config(state=tk.DISABLED)
            self.update_config_btn.config(state=tk.DISABLED)
            self.replace_draft_btn.config(state=tk.DISABLED)
            self.open_btn.config(state=tk.DISABLED)
        else:
            self._update_action_buttons()

    def _get_automation(self) -> ZenodoAutomation | None:
        if self.automation:
            return self.automation
        token = read_token_from_zenodo_py()
        if not token:
            messagebox.showerror("No Token", "Zenodo API token not found in zenodo.py")
            return None
        self.automation = ZenodoAutomation(token, sandbox=False)
        return self.automation

    def refresh_data(self) -> None:
        if self._busy:
            return

        def worker() -> None:
            self._set_busy(True)
            self.root.after(0, lambda: self.status_label.config(text="Refreshing..."))
            try:
                local = scan_local_canon_versions()
                automation = self._get_automation()
                online: list[CanonVersionInfo] = []
                if automation:
                    online = fetch_online_canon_versions(automation, local)
                statuses = compare_versions(local, online)
                self.root.after(0, lambda: self._apply_refresh(local, online, statuses))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Refresh Error", str(e)))
            finally:
                self.root.after(0, lambda: self._set_busy(False))
                self.root.after(0, lambda: self.status_label.config(text="Ready"))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_refresh(
        self,
        local: list[CanonVersionInfo],
        online: list[CanonVersionInfo],
        statuses: list[VersionStatus],
    ) -> None:
        self.local_versions = local
        self.online_versions = online
        self.statuses = statuses
        self._last_logged_validation_version = None

        for tree in (self.published_tree, self.drafts_tree, self.local_tree, self.compare_tree):
            for item in tree.get_children():
                tree.delete(item)

        for v in list_online_published(online):
            self.published_tree.insert('', tk.END, values=(
                f"v{v.version}",
                v.doi or '-',
                v.publication_date or '-',
            ))

        for v in list_online_drafts(online):
            version_label = v.version if is_orphan_online_version(v.version) else f"v{v.version}"
            title = (v.title or '')[:48]
            self.drafts_tree.insert(
                '',
                tk.END,
                iid=v.deposit_id or version_label,
                values=(
                    version_label,
                    v.deposit_id or '-',
                    v.doi or '-',
                    title,
                ),
            )

        for v in local:
            status = next((s for s in statuses if s.version == v.version), None)
            warn = '✗' if status and status.errors else ''
            doi_display = (v.doi or '-')[:24]
            if status and status.status == 'duplicate_doi':
                doi_display = f"⚠ {doi_display}"
            if v.has_pdf:
                pdf_display = '✓' if v.pdf_doi_ok else '⚠'
            else:
                pdf_display = '✗'
            self.local_tree.insert('', tk.END, values=(
                f"v{v.version}",
                '✓' if v.has_tex else '✗',
                pdf_display,
                doi_display,
                '✓' if v.has_config else '✗',
                warn,
            ))

        error_count = 0
        for s in statuses:
            self.compare_tree.insert('', tk.END, values=(
                f"v{s.version}",
                s.status,
                s.message,
            ), tags=(s.status,))
            if s.errors:
                error_count += 1

        drafts = list_online_drafts(online)
        blocked = [s for s in statuses if s.errors and s.local and s.status != 'published']
        if blocked:
            summary = f"{len(blocked)} lokale versie(s) met fouten (DOI niet uniek of config ontbreekt)"
        else:
            ready = [s for s in statuses if s.can_push]
            update_ready = [s for s in statuses if s.can_update_config]
            parts = []
            if drafts:
                parts.append(f"{len(drafts)} online draft(s)")
            if update_ready:
                parts.append(f"{len(update_ready)} Update Config klaar")
            if ready:
                parts.append(f"{len(ready)} klaar om te pushen")
            summary = ", ".join(parts) if parts else "Geen versies klaar voor push"
        self.status_label.config(text=summary)
        published_n = len(list_online_published(online))
        self.log(
            f"Refresh: {len(local)} local, {published_n} published, "
            f"{len(drafts)} drafts, {error_count} met fouten"
        )
        if self.verbose_errors.get():
            for v in local:
                status = next((s for s in statuses if s.version == v.version), None)
                if self._needs_pdf_diagnostics(v, status):
                    self._log_pdf_diagnostics(v)
        self._update_action_buttons()

    def _selected_status(self) -> VersionStatus | None:
        if not self.selected_version:
            return None
        return next((s for s in self.statuses if s.version == self.selected_version), None)

    def _selected_draft(self) -> CanonVersionInfo | None:
        if not self.selected_draft_deposit_id:
            return None
        return next(
            (
                v for v in self.online_versions
                if v.state == 'draft' and v.deposit_id == self.selected_draft_deposit_id
            ),
            None,
        )

    def _update_action_buttons(self) -> None:
        status = self._selected_status()
        draft = self._selected_draft()
        if self._busy:
            return

        if not status:
            self.push_btn.config(state=tk.DISABLED, text="Push Selected as Draft")
            self.mint_btn.config(state=tk.DISABLED)
            self.render_btn.config(state=tk.DISABLED)
            self.update_config_btn.config(state=tk.DISABLED)
            self.open_btn.config(state=tk.DISABLED)
        else:
            if status.can_push:
                self.push_btn.config(state=tk.NORMAL, text="Push Selected as Draft")
            else:
                self.push_btn.config(state=tk.DISABLED, text="Push Selected as Draft")
            if status.can_mint_doi:
                remint = (
                    status.status == 'stale_deposit'
                    or local_deposit_is_stale(
                        status.version, self.local_versions, self.online_versions
                    )
                )
                self.mint_btn.config(
                    state=tk.NORMAL,
                    text="Remint DOI + Config" if remint else "Mint DOI + Config",
                )
            else:
                self.mint_btn.config(state=tk.DISABLED, text="Mint DOI + Config")
            self.render_btn.config(state=tk.NORMAL if status.can_render else tk.DISABLED)
            self.update_config_btn.config(
                state=tk.NORMAL if status.can_update_config else tk.DISABLED
            )
            has_url = bool(status.online and status.online.html_url)
            if not has_url and status.local and status.local.deposit_id:
                has_url = True
            self.open_btn.config(state=tk.NORMAL if has_url else tk.DISABLED)

        can_replace = bool(draft and draft.deposit_id)
        self.replace_draft_btn.config(state=tk.NORMAL if can_replace else tk.DISABLED)
        if draft and draft.html_url and not status:
            self.open_btn.config(state=tk.NORMAL)

    def _on_compare_select(self, _event=None) -> None:
        if self._syncing_selection:
            return
        sel = self.compare_tree.selection()
        if not sel:
            self.selected_version = None
            self._update_action_buttons()
            return
        values = self.compare_tree.item(sel[0], 'values')
        version = values[0].lstrip('v')
        version_changed = version != self.selected_version
        self.selected_version = version
        status = self._selected_status()
        if status and status.online and status.online.state == 'draft' and status.online.deposit_id:
            self.selected_draft_deposit_id = status.online.deposit_id
            self._set_tree_selection(self.drafts_tree, status.online.deposit_id)
        if version_changed and status:
            self._log_validation_once(version, status)
        self._update_action_buttons()

    def _on_draft_select(self, _event=None) -> None:
        if self._syncing_selection:
            return
        sel = self.drafts_tree.selection()
        if not sel:
            self.selected_draft_deposit_id = None
            self._update_action_buttons()
            return
        deposit_id = str(sel[0])
        self.selected_draft_deposit_id = deposit_id
        draft = self._selected_draft()
        if draft and not is_orphan_online_version(draft.version):
            version_changed = draft.version != self.selected_version
            self.selected_version = draft.version
            # sync compare selection when possible (guarded against feedback loop)
            for item in self.compare_tree.get_children():
                values = self.compare_tree.item(item, 'values')
                if values and values[0].lstrip('v') == draft.version:
                    self._set_tree_selection(self.compare_tree, item)
                    break
            if version_changed:
                status = self._selected_status()
                if status:
                    self._log_validation_once(draft.version, status)
        self._update_action_buttons()

    def _draft_url_for_version(self, version: str) -> str:
        status = next((s for s in self.statuses if s.version == version), None)
        if status:
            if status.online and status.online.html_url:
                return status.online.html_url
            if status.local and status.local.deposit_id:
                return f"https://zenodo.org/deposit/{status.local.deposit_id}"
        draft = self._selected_draft()
        if draft and draft.html_url:
            return draft.html_url
        if draft and draft.deposit_id:
            return f"https://zenodo.org/deposit/{draft.deposit_id}"
        return ""

    def open_draft(self) -> None:
        url = ""
        if self.selected_version:
            url = self._draft_url_for_version(self.selected_version)
        if not url:
            draft = self._selected_draft()
            if draft:
                url = draft.html_url or f"https://zenodo.org/deposit/{draft.deposit_id}"
        if url:
            webbrowser.open(url)
            self.log(f"Opened: {url}")
        else:
            messagebox.showinfo("No URL", "No Zenodo URL available for this selection")

    def _finish_worker(self, result_handler) -> None:
        """Clear busy flag before refresh (refresh_data skips while busy)."""
        def finish() -> None:
            result_handler()
            self._set_busy(False)
            remint_ver = self._pending_remint_version
            self._pending_remint_version = None
            if remint_ver:
                self.selected_version = remint_ver
                # After busy clears, offer Remint flow
                self.root.after(50, self.mint_selected)
            else:
                self.refresh_data()

        self.root.after(0, finish)

    def _offer_api_failure_action(self, result) -> None:
        """Show API failure and optionally queue the suggested recovery action."""
        msg = result.message or "Zenodo-actie mislukt"
        self.log(f"✗ v{getattr(result, 'version', '?')}: {msg}")
        if getattr(result, "api_status", None) is not None:
            self.log(f"  API HTTP {result.api_status}")
        if getattr(result, "api_detail", None):
            self.log(f"  detail: {result.api_detail[:400]}")

        action = getattr(result, "suggested_action", "") or ""
        version = getattr(result, "version", None) or self.selected_version

        if action == "remint" and version:
            if messagebox.askyesno(
                "API-fout — Remint?",
                f"{msg}\n\nRemint DOI + Config voor v{version} nu uitvoeren?",
            ):
                self._pending_remint_version = version
            return
        if action == "retry":
            messagebox.showwarning(
                "API-fout — later opnieuw",
                f"{msg}\n\nTip: even wachten en Refresh, daarna opnieuw proberen.",
            )
            return
        if action == "check_token":
            messagebox.showerror(
                "API-fout — token/rechten",
                f"{msg}\n\nControleer je Zenodo API-token in zenodo.py.",
            )
            return
        if action == "reuse_draft":
            messagebox.showinfo(
                "API-fout — bestaande draft",
                f"{msg}\n\nRefresh de lijst. Gebruik Replace Draft… of bind de bestaande draft.",
            )
            return
        messagebox.showerror("Failed", msg)

    def mint_selected(self) -> None:
        if not self.selected_version or self._busy:
            return
        version = self.selected_version
        status = self._selected_status()
        remint = bool(
            status
            and (
                status.status == 'stale_deposit'
                or local_deposit_is_stale(version, self.local_versions, self.online_versions)
            )
        )
        if remint:
            preview = (
                f"Remint DOI + Config voor v{version}?\n\n"
                "De lokale deposit bestaat niet (meer) op Zenodo.\n"
                "Er wordt een NIEUWE Zenodo-versie (draft) aangemaakt met een nieuwe DOI.\n"
                "Lokale .tex DOI + .zenodo.json worden overschreven.\n\n"
                "Geen PDF-upload."
            )
            title = "Confirm Remint DOI"
        else:
            preview = f"Mint unieke DOI + config voor v{version}?\n\n"
            if status and status.errors:
                preview += "Huidige problemen:\n" + "\n".join(f"• {e}" for e in status.errors) + "\n\n"
            preview += (
                "Dit maakt een nieuwe Zenodo-versie (draft) en schrijft DOI + .zenodo.json.\n"
                "Geen PDF-upload."
            )
            title = "Confirm Mint DOI"
        if not messagebox.askyesno(title, preview):
            return

        def worker() -> None:
            self._set_busy(True)
            self.root.after(
                0,
                lambda: self.status_label.config(
                    text=f"{'Reminting' if remint else 'Minting'} DOI v{version}..."
                ),
            )
            try:
                automation = self._get_automation()
                if not automation:
                    self.root.after(0, lambda: self._set_busy(False))
                    return

                def on_log(msg: str) -> None:
                    self.root.after(0, lambda m=msg: self.log(m))

                result = mint_version_doi(
                    version,
                    automation=automation,
                    force=remint,
                    on_log=on_log,
                )

                def show_result() -> None:
                    if result.success:
                        messagebox.showinfo("Success", f"v{version}: {result.message}\nDOI: {result.doi}")
                        self.log(f"✓ v{version} DOI {'her' if remint else ''}gemint — {result.doi}")
                    else:
                        self._offer_api_failure_action(result)

                self._finish_worker(show_result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def render_selected(self) -> None:
        if not self.selected_version or self._busy:
            return
        version = self.selected_version
        status = self._selected_status()
        if status and not status.can_render:
            messagebox.showerror(
                "Render geblokkeerd",
                "Deze versie kan nu niet gerenderd worden.\n\n"
                + "\n".join(f"• {e}" for e in (status.errors or ["Geen tex/config/DOI"]))
            )
            return
        preview = f"Render PDF voor v{version}?\n\n"
        if status and status.local:
            preview += f"Verwachte DOI: {status.local.doi}\n"
        preview += "\nAlleen lokaal compileren (geen Zenodo-upload)."
        if not messagebox.askyesno("Confirm Render PDF", preview):
            return

        def worker() -> None:
            self._set_busy(True)
            self.root.after(0, lambda: self.status_label.config(text=f"Rendering v{version}..."))
            try:
                def on_log(msg: str) -> None:
                    self.root.after(0, lambda m=msg: self.log(m))

                result = render_version_pdf(
                    version,
                    verbose=self.verbose_errors.get(),
                    on_log=on_log,
                )

                def show_result() -> None:
                    if result.success:
                        messagebox.showinfo("Success", f"v{version}: {result.message}")
                        self.log(f"✓ v{version} PDF gerenderd — DOI {result.doi}")
                    else:
                        messagebox.showerror("Failed", result.message)
                        self.log(f"✗ v{version} render failed: {result.message}")
                        if not self.verbose_errors.get():
                            self._log_local_diagnostics_if_verbose(version)

                self._finish_worker(show_result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def update_config_selected(self) -> None:
        if not self.selected_version or self._busy:
            return
        version = self.selected_version
        status = self._selected_status()
        if not status or not status.can_update_config:
            messagebox.showerror(
                "Update Config geblokkeerd",
                "Geen online draft/published record gekoppeld aan deze lokale versie.",
            )
            return
        state = status.online.state if status.online else "?"
        preview = (
            f"Update Config voor v{version}?\n\n"
            f"Online state: {state}\n"
            f"{status.message}\n\n"
            "Vernieuwt lokale .zenodo.json description en pusht metadata naar Zenodo.\n"
            "Geen PDF. Geen file-upload."
        )
        if not messagebox.askyesno("Confirm Update Config", preview):
            return

        def worker() -> None:
            self._set_busy(True)
            self.root.after(0, lambda: self.status_label.config(text=f"Updating config v{version}..."))
            try:
                automation = self._get_automation()
                if not automation:
                    self.root.after(0, lambda: self._set_busy(False))
                    return

                def on_log(msg: str) -> None:
                    self.root.after(0, lambda m=msg: self.log(m))

                result = update_config_no_pdf(
                    version,
                    automation=automation,
                    dry_run=False,
                    publish_if_published=True,
                    on_log=on_log,
                )

                def show_result() -> None:
                    if result.success:
                        messagebox.showinfo("Success", f"v{version}: {result.message}\nDOI: {result.doi}")
                        self.log(f"✓ v{version} config/metadata updated — {result.doi}")
                    else:
                        self._offer_api_failure_action(result)

                self._finish_worker(show_result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def replace_draft_selected(self) -> None:
        if self._busy:
            return
        draft = self._selected_draft()
        if not draft or not draft.deposit_id:
            messagebox.showinfo("Geen draft", "Selecteer eerst een online draft.")
            return

        bindable = list_bindable_local_versions(
            self.local_versions,
            self.online_versions,
            draft_deposit_id=draft.deposit_id,
        )
        if not bindable:
            messagebox.showinfo(
                "Geen kandidaten",
                "Geen lokale canon-versie beschikbaar om deze draft te claimen "
                "(tex nodig; niet al published).",
            )
            return

        choices = [f"v{v.version}" for v in bindable]
        default = choices[0]
        if draft.version and not is_orphan_online_version(draft.version):
            preferred = f"v{draft.version}"
            if preferred in choices:
                default = preferred

        chosen = simpledialog.askstring(
            "Replace Draft",
            (
                f"Bind draft {draft.deposit_id} aan welke lokale versie?\n\n"
                f"Beschikbaar: {', '.join(choices)}\n\n"
                "Geen PDF-upload. Metadata + lokale .zenodo.json worden bijgewerkt."
            ),
            initialvalue=default,
            parent=self.root,
        )
        if not chosen:
            return
        version = chosen.strip().lstrip('v')
        if version not in {v.version for v in bindable}:
            messagebox.showerror("Ongeldige versie", f"'{chosen}' staat niet in de kandidatenlijst.")
            return

        if not messagebox.askyesno(
            "Confirm Replace Draft",
            f"Draft {draft.deposit_id} → lokale v{version}?\n\nGeen PDF.",
        ):
            return

        def worker() -> None:
            self._set_busy(True)
            self.root.after(
                0,
                lambda: self.status_label.config(text=f"Binding draft → v{version}..."),
            )
            try:
                automation = self._get_automation()
                if not automation:
                    self.root.after(0, lambda: self._set_busy(False))
                    return

                def on_log(msg: str) -> None:
                    self.root.after(0, lambda m=msg: self.log(m))

                result = bind_draft_to_local_version(
                    draft.deposit_id,
                    version,
                    automation=automation,
                    dry_run=False,
                    on_log=on_log,
                )

                def show_result() -> None:
                    if result.success:
                        messagebox.showinfo(
                            "Success",
                            f"{result.message}\nDOI: {result.doi}",
                        )
                        self.log(f"✓ draft {draft.deposit_id} → v{version} — {result.doi}")
                        self.selected_version = version
                    else:
                        self._offer_api_failure_action(result)

                self._finish_worker(show_result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()

    def push_selected(self) -> None:
        if not self.selected_version or self._busy:
            return
        version = self.selected_version
        status = self._selected_status()
        if not status:
            return

        if not status.can_push:
            messagebox.showerror(
                "Push geblokkeerd",
                "Deze versie mag nog niet naar Zenodo (PDF-upload):\n\n"
                + "\n".join(f"• {e}" for e in (status.errors or ["Onbekende validatiefout"]))
                + "\n\nGebruik 'Update Config' voor metadata-only, of eerst "
                "'Mint DOI + Config' / 'Replace Draft…' / 'Render PDF'.",
            )
            return
        preview = f"Push v{version} naar Zenodo als draft?\n\n"
        preview += f"Status: {status.message}\n"
        preview += "\nVereist: unieke DOI + .zenodo.json met deposit_id.\n"
        preview += "Actie: PDF renderen en uploaden (blijft draft)."
        if not messagebox.askyesno("Confirm Push", preview):
            return

        def worker() -> None:
            self._set_busy(True)
            self.root.after(0, lambda: self.status_label.config(text=f"Pushing v{version}..."))
            try:
                automation = self._get_automation()
                if not automation:
                    self.root.after(0, lambda: self._set_busy(False))
                    return

                def on_log(msg: str) -> None:
                    self.root.after(0, lambda m=msg: self.log(m))

                result = push_version_as_draft(
                    version,
                    automation=automation,
                    dry_run=False,
                    publish=False,
                    on_log=on_log,
                )

                def show_result() -> None:
                    if result.success:
                        messagebox.showinfo("Success", f"v{version}: {result.message}\nDOI: {result.doi}")
                        self.log(f"✓ v{version} pushed as draft — {result.doi}")
                    else:
                        self._offer_api_failure_action(result)
                        self._log_local_diagnostics_if_verbose(version)

                self._finish_worker(show_result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self._set_busy(False))

        threading.Thread(target=worker, daemon=True).start()


def main() -> None:
    root = tk.Tk()
    CanonZenodoGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
