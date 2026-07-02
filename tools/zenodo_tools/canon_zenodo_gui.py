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
    from tkinter import messagebox, scrolledtext, ttk
except ImportError:
    print("tkinter is required for canon_zenodo_gui.py. Install Python with Tcl/Tk support.")
    sys.exit(1)

from publish_canon_zenodo import (
    CanonVersionInfo,
    VersionStatus,
    compare_versions,
    fetch_online_canon_versions,
    mint_version_doi,
    push_version_as_draft,
    render_version_pdf,
    scan_local_canon_versions,
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
    'ahead_local': '#e65100',
    'draft_online': '#1565c0',
    'online_only': '#6a1b9a',
    'local_only': '#757575',
    'duplicate_doi': '#c62828',
    'missing_config': '#c62828',
    'blocked': '#c62828',
    'stale_pdf': '#e65100',
}


class CanonZenodoGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SST Canon — Zenodo Version Manager")
        self.root.geometry("1200x750")

        self.automation: ZenodoAutomation | None = None
        self.local_versions: list[CanonVersionInfo] = []
        self.online_versions: list[CanonVersionInfo] = []
        self.statuses: list[VersionStatus] = []
        self.selected_version: str | None = None
        self._busy = False

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

        # Online panel
        online_frame = ttk.LabelFrame(paned, text="Online (Zenodo)")
        paned.add(online_frame, weight=1)

        online_cols = ('version', 'state', 'doi', 'date')
        self.online_tree = ttk.Treeview(online_frame, columns=online_cols, show='headings', height=14)
        for col, w in zip(online_cols, (70, 80, 200, 90)):
            self.online_tree.heading(col, text=col.capitalize())
            self.online_tree.column(col, width=w, minwidth=60)
        online_scroll = ttk.Scrollbar(online_frame, orient=tk.VERTICAL, command=self.online_tree.yview)
        self.online_tree.configure(yscrollcommand=online_scroll.set)
        self.online_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        online_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=4)

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

        self.push_btn = ttk.Button(action_frame, text="Push Selected as Draft", command=self.push_selected, state=tk.DISABLED)
        self.push_btn.pack(side=tk.RIGHT, padx=4)

        self.render_btn = ttk.Button(action_frame, text="Render PDF", command=self.render_selected, state=tk.DISABLED)
        self.render_btn.pack(side=tk.RIGHT, padx=4)

        self.mint_btn = ttk.Button(action_frame, text="Mint DOI + Config", command=self.mint_selected, state=tk.DISABLED)
        self.mint_btn.pack(side=tk.RIGHT, padx=4)

        self.open_btn = ttk.Button(action_frame, text="Open Zenodo Draft", command=self.open_draft, state=tk.DISABLED)
        self.open_btn.pack(side=tk.RIGHT, padx=4)

        # Log
        log_frame = ttk.LabelFrame(self.root, text="Action Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def log(self, msg: str) -> None:
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self.refresh_btn.config(state=state)
        if busy:
            self.push_btn.config(state=tk.DISABLED)
            self.mint_btn.config(state=tk.DISABLED)
            self.render_btn.config(state=tk.DISABLED)
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

        for tree in (self.online_tree, self.local_tree, self.compare_tree):
            for item in tree.get_children():
                tree.delete(item)

        for v in online:
            self.online_tree.insert('', tk.END, values=(
                f"v{v.version}",
                v.state,
                v.doi or '-',
                v.publication_date or '-',
            ))

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

        blocked = [s for s in statuses if s.errors and s.local]
        if blocked:
            summary = f"{len(blocked)} lokale versie(s) met fouten (DOI niet uniek of config ontbreekt)"
        else:
            ready = [s for s in statuses if s.can_push]
            summary = f"{len(ready)} versie(s) klaar om te pushen" if ready else "Geen versies klaar voor push"
        self.status_label.config(text=summary)
        self.log(f"Refresh: {len(local)} local, {len(online)} online, {error_count} met fouten")

    def _selected_status(self) -> VersionStatus | None:
        if not self.selected_version:
            return None
        return next((s for s in self.statuses if s.version == self.selected_version), None)

    def _update_action_buttons(self) -> None:
        status = self._selected_status()
        if not status or self._busy:
            self.push_btn.config(state=tk.DISABLED)
            self.mint_btn.config(state=tk.DISABLED)
            self.render_btn.config(state=tk.DISABLED)
            self.open_btn.config(state=tk.DISABLED)
            return
        self.push_btn.config(state=tk.NORMAL if status.can_push else tk.DISABLED)
        self.mint_btn.config(state=tk.NORMAL if status.can_mint_doi else tk.DISABLED)
        self.render_btn.config(state=tk.NORMAL if status.can_render else tk.DISABLED)
        has_url = bool(status.online and status.online.html_url)
        if not has_url and status.local and status.local.deposit_id:
            has_url = True
        self.open_btn.config(state=tk.NORMAL if has_url else tk.DISABLED)

    def _on_compare_select(self, _event=None) -> None:
        sel = self.compare_tree.selection()
        if not sel:
            self.selected_version = None
            self._update_action_buttons()
            return
        values = self.compare_tree.item(sel[0], 'values')
        version = values[0].lstrip('v')
        self.selected_version = version
        status = self._selected_status()
        if status and status.errors:
            self.log(f"--- v{version} validatie ---")
            for err in status.errors:
                self.log(f"  ! {err}")
        self._update_action_buttons()

    def _draft_url_for_version(self, version: str) -> str:
        status = next((s for s in self.statuses if s.version == version), None)
        if not status:
            return ""
        if status.online and status.online.html_url:
            return status.online.html_url
        if status.local and status.local.deposit_id:
            return f"https://zenodo.org/deposit/{status.local.deposit_id}"
        return ""

    def open_draft(self) -> None:
        if not self.selected_version:
            return
        url = self._draft_url_for_version(self.selected_version)
        if url:
            webbrowser.open(url)
            self.log(f"Opened: {url}")
        else:
            messagebox.showinfo("No URL", "No Zenodo URL available for this version")

    def _finish_worker(self, result_handler) -> None:
        """Clear busy flag before refresh (refresh_data skips while busy)."""
        def finish() -> None:
            result_handler()
            self._set_busy(False)
            self.refresh_data()

        self.root.after(0, finish)

    def mint_selected(self) -> None:
        if not self.selected_version or self._busy:
            return
        version = self.selected_version
        status = self._selected_status()
        preview = f"Mint unieke DOI + config voor v{version}?\n\n"
        if status and status.errors:
            preview += "Huidige problemen:\n" + "\n".join(f"• {e}" for e in status.errors) + "\n\n"
        preview += "Dit maakt een nieuwe Zenodo-versie (draft) en schrijft DOI + .zenodo.json.\nGeen PDF-upload."
        if not messagebox.askyesno("Confirm Mint DOI", preview):
            return

        def worker() -> None:
            self._set_busy(True)
            self.root.after(0, lambda: self.status_label.config(text=f"Minting DOI v{version}..."))
            try:
                automation = self._get_automation()
                if not automation:
                    return

                def on_log(msg: str) -> None:
                    self.root.after(0, lambda m=msg: self.log(m))

                result = mint_version_doi(version, automation=automation, on_log=on_log)

                def show_result() -> None:
                    if result.success:
                        messagebox.showinfo("Success", f"v{version}: {result.message}\nDOI: {result.doi}")
                        self.log(f"✓ v{version} DOI gemint — {result.doi}")
                    else:
                        messagebox.showerror("Failed", result.message)
                        self.log(f"✗ v{version} mint failed: {result.message}")

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

                result = render_version_pdf(version, on_log=on_log)

                def show_result() -> None:
                    if result.success:
                        messagebox.showinfo("Success", f"v{version}: {result.message}")
                        self.log(f"✓ v{version} PDF gerenderd — DOI {result.doi}")
                    else:
                        messagebox.showerror("Failed", result.message)
                        self.log(f"✗ v{version} render failed: {result.message}")

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
        if status and not status.can_push:
            messagebox.showerror(
                "Push geblokkeerd",
                "Deze versie mag nog niet naar Zenodo:\n\n"
                + "\n".join(f"• {e}" for e in (status.errors or ["Onbekende validatiefout"]))
                + "\n\nGebruik eerst 'Mint DOI + Config' of 'Render PDF' indien nodig.",
            )
            return
        preview = f"Push v{version} naar Zenodo als draft?\n\n"
        if status:
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
                        messagebox.showerror("Failed", result.message)
                        self.log(f"✗ v{version}: {result.message}")

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
