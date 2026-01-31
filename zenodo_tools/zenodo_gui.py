#!/usr/bin/env python3
"""
GUI to display all SST-xx .tex, .pdf, and zenodo config files recursively.
"""

import json
import re
import sys
import subprocess
import threading
import tkinter as tk
import requests
from pathlib import Path
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from zenodo_automation import read_token_from_zenodo_py, ZenodoAutomation

# Handle encoding
if sys.platform == 'win32':
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

class ZenodoFileViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("SST Papers - Zenodo File Viewer")
        self.root.geometry("1600x900")
        
        self.base_dir = Path(__file__).parent.parent
        
        # Create main paned window
        main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Tree view
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Tree view
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars for tree
        tree_vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_hscroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set)
        tree_vscroll.config(command=self.tree.yview)
        tree_hscroll.config(command=self.tree.xview)
        
        tree_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tree columns
        self.tree['columns'] = ('Type', 'DOI', 'Status')
        self.tree.heading('#0', text='File/Folder', anchor=tk.W)
        self.tree.heading('Type', text='Type', anchor=tk.W)
        self.tree.heading('DOI', text='DOI', anchor=tk.W)
        self.tree.heading('Status', text='Status', anchor=tk.W)
        
        self.tree.column('#0', width=400, minwidth=200)
        self.tree.column('Type', width=100, minwidth=80)
        self.tree.column('DOI', width=200, minwidth=150)
        self.tree.column('Status', width=150, minwidth=100)
        
        # Configure tags for visual styling
        self.tree.tag_configure('missing_config', foreground='red')
        self.tree.tag_configure('missing_doi', foreground='orange')
        self.tree.tag_configure('has_doi', foreground='green')
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Bind expand event to load JSON data
        self.tree.bind('<<TreeviewOpen>>', self.on_expand)
        
        # Bind right-click context menu
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Create context menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Upload PDF", command=self.upload_pdf_selected)
        self.context_menu.add_command(label="Render & Upload", command=self.render_and_upload_selected)
        self.context_menu.add_command(label="Sync Publication Date", command=self.sync_date_selected)
        self.context_menu.add_command(label="Update Metadata", command=self.update_metadata_selected)
        self.context_menu.add_command(label="Create/Edit Config", command=self.edit_config_selected)
        self.context_menu.add_command(label="Edit JSON", command=self.edit_json_selected)
        self.context_menu.add_command(label="Fetch from Zenodo", command=self.fetch_from_zenodo_selected)
        self.context_menu.add_command(label="Merge Configs", command=self.merge_configs_selected)
        
        # Right panel: Details and Log
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        # Details text area
        details_label = ttk.Label(right_frame, text="File Details:", font=('Arial', 10, 'bold'))
        details_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.details_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=15)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.refresh_tree)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        expand_btn = ttk.Button(button_frame, text="Expand All", command=self.expand_all)
        expand_btn.pack(side=tk.LEFT, padx=5)
        
        collapse_btn = ttk.Button(button_frame, text="Collapse All", command=self.collapse_all)
        collapse_btn.pack(side=tk.LEFT, padx=5)
        
        # Sorting toggle
        self.sort_errors_first = tk.BooleanVar(value=True)  # Default: errors first
        sort_checkbox = ttk.Checkbutton(button_frame, text="Errors First", 
                                        variable=self.sort_errors_first,
                                        command=self.refresh_tree)
        sort_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Action buttons frame
        action_frame = ttk.LabelFrame(left_frame, text="Actions")
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Upload/Processing buttons
        self.upload_pdf_btn = ttk.Button(action_frame, text="Upload PDF", command=self.upload_pdf_selected, state=tk.DISABLED)
        self.upload_pdf_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.render_upload_btn = ttk.Button(action_frame, text="Render & Upload", command=self.render_and_upload_selected, state=tk.DISABLED)
        self.render_upload_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.sync_date_btn = ttk.Button(action_frame, text="Sync Publication Date", command=self.sync_date_selected, state=tk.DISABLED)
        self.sync_date_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.update_metadata_btn = ttk.Button(action_frame, text="Update Metadata", command=self.update_metadata_selected, state=tk.DISABLED)
        self.update_metadata_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.edit_config_btn = ttk.Button(action_frame, text="Create/Edit Config", command=self.edit_config_selected, state=tk.DISABLED)
        self.edit_config_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.edit_json_btn = ttk.Button(action_frame, text="Edit JSON", command=self.edit_json_selected, state=tk.DISABLED)
        self.edit_json_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.fetch_zenodo_btn = ttk.Button(action_frame, text="Fetch from Zenodo", command=self.fetch_from_zenodo_selected, state=tk.DISABLED)
        self.fetch_zenodo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Bulk actions frame
        bulk_frame = ttk.LabelFrame(left_frame, text="Bulk Actions")
        bulk_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(bulk_frame, text="Render All & Update", command=self.render_all_and_update).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(bulk_frame, text="Sync All Dates", command=self.sync_all_dates).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(bulk_frame, text="Update All Creators", command=self.update_all_creators).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Output log frame
        log_frame = ttk.LabelFrame(right_frame, text="Action Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Store selected file
        self.selected_file = None
        self.selected_file_type = None
        
        # Status bar
        self.status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load data
        self.refresh_tree()
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get information about a file."""
        info = {
            'type': 'unknown',
            'doi': '',
            'status': '',
            'details': {}
        }
        
        if file_path.suffix == '.tex':
            info['type'] = 'LaTeX'
            # Check for DOI in LaTeX
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                doi_match = re.search(r'10\.5281/zenodo\.(\d+)', content)
                if doi_match:
                    info['doi'] = doi_match.group(0)
                    info['status'] = 'Has DOI'
                else:
                    info['status'] = 'No DOI'
                
                # Extract title
                title_match = re.search(r'\\title\{([^}]+)\}', content, re.DOTALL)
                if not title_match:
                    title_match = re.search(r'\\newcommand\{\\papertitle\}\{([^}]+)\}', content, re.DOTALL)
                if title_match:
                    title = title_match.group(1).strip()
                    title = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', title)
                    info['details']['title'] = ' '.join(title.split())[:100]
            except:
                pass
        
        elif file_path.suffix == '.pdf':
            info['type'] = 'PDF'
            info['status'] = 'PDF file'
            # Check if corresponding .tex exists
            tex_file = file_path.with_suffix('.tex')
            if tex_file.exists():
                info['details']['tex_file'] = str(tex_file.name)
        
        elif file_path.suffix == '.zenodo.json':
            info['type'] = 'Config'
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                info['doi'] = config_data.get('doi', '')
                info['status'] = 'Has DOI' if info['doi'] else 'No DOI'
                info['details'] = config_data  # Store full config data
            except Exception as e:
                info['status'] = f'Error reading config: {e}'
                info['details'] = {}
        
        return info
    
    def refresh_tree(self):
        """Refresh the tree view with current files."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.status_bar.config(text="Loading files...")
        self.root.update()
        
        # Find all SST-xx folders
        sst_folders = []
        for folder in self.base_dir.iterdir():
            if folder.is_dir() and re.match(r'^SST-\d+', folder.name):
                sst_folders.append(folder)
        
        # Sort folders - errors first if enabled
        if self.sort_errors_first.get():
            def folder_sort_key(folder):
                # Check for errors
                main_config = folder / f"{folder.name}.zenodo.json"
                has_config = main_config.exists()
                has_doi = False
                if has_config:
                    try:
                        with open(main_config, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        has_doi = bool(config_data.get('doi', ''))
                    except:
                        pass
                
                # Error priority: no config = 0, no doi = 1, has both = 2
                if not has_config:
                    error_priority = 0
                elif not has_doi:
                    error_priority = 1
                else:
                    error_priority = 2
                
                return (error_priority, folder.name)
            
            sst_folders.sort(key=folder_sort_key)
        else:
            sst_folders.sort(key=lambda x: x.name)
        
        file_count = 0
        for folder in sst_folders:
            # Check folder status: look for main config file and DOI
            folder_doi = ''
            folder_status = ''
            has_config = False
            has_doi = False
            
            # Find main config file (SST-xx.zenodo.json)
            main_config = folder / f"{folder.name}.zenodo.json"
            if main_config.exists():
                has_config = True
                try:
                    with open(main_config, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    folder_doi = config_data.get('doi', '')
                    if folder_doi:
                        has_doi = True
                        folder_status = 'Has DOI'
                    else:
                        folder_status = 'No DOI'
                except:
                    folder_status = 'Config Error'
            else:
                folder_status = 'No Config'
            
            # Create folder node with status
            folder_text = folder.name
            if folder_doi:
                folder_text += f" [{folder_doi}]"
            
            # Determine tag for visual styling
            folder_tag = ''
            if not has_config:
                folder_status = '⚠ No Config'
                folder_tag = 'missing_config'
            elif not has_doi:
                folder_status = '⚠ No DOI'
                folder_tag = 'missing_doi'
            elif has_doi:
                folder_tag = 'has_doi'
            
            folder_node = self.tree.insert('', 'end', text=folder_text, 
                                          values=('Folder', folder_doi, folder_status),
                                          tags=(folder_tag,))
            
            # Find all .tex, .pdf, and .zenodo.json files - show each file separately
            all_files = []
            for ext in ['.tex', '.pdf', '.zenodo.json']:
                for file_path in folder.rglob(f'*{ext}'):
                    if file_path.is_file():
                        # Skip cover letters
                        if 'coverletter' in file_path.name.lower() or 'cover_letter' in file_path.name.lower():
                            continue
                        all_files.append(file_path)
            
            # Sort files - errors first if enabled, otherwise alphabetically
            def file_sort_key(fp):
                # Check for errors in config files
                error_priority = 2  # Default: no error
                if fp.suffix == '.zenodo.json':
                    try:
                        with open(fp, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        has_doi = bool(config_data.get('doi', ''))
                        if not has_doi:
                            error_priority = 1  # No DOI
                    except:
                        error_priority = 0  # Error reading config
                
                # Extract base name for grouping
                base_name = fp.stem
                # Remove .zenodo from config files for better grouping
                if fp.suffix == '.zenodo.json':
                    base_name = base_name.replace('.zenodo', '')
                
                # Extension priority
                ext_priority = {
                    '.zenodo.json': 0 if '.online.json' in fp.name else 1,
                    '.tex': 2,
                    '.pdf': 3
                }.get(fp.suffix, 4)
                
                if self.sort_errors_first.get():
                    # Sort by error priority first, then by name
                    return (error_priority, base_name, ext_priority, fp.name)
                else:
                    # Normal sorting: by name only
                    return (base_name, ext_priority, fp.name)
            
            all_files.sort(key=file_sort_key)
            
            # Add each file as a separate entry
            for file_path in all_files:
                info = self.get_file_info(file_path)
                
                # Determine file type display
                if file_path.suffix == '.zenodo.json':
                    if '.online.json' in file_path.name:
                        file_type = 'Config (Online)'
                    else:
                        file_type = 'Config'
                elif file_path.suffix == '.tex':
                    file_type = 'LaTeX'
                elif file_path.suffix == '.pdf':
                    file_type = 'PDF'
                else:
                    file_type = 'Unknown'
                
                # Create file node
                file_node = self.tree.insert(folder_node, 'end', text=file_path.name,
                                           values=(file_type, info['doi'], info['status']),
                                           tags=(str(file_path),))
                
                # If it's a config file, make it expandable
                if file_path.suffix == '.zenodo.json':
                    self.tree.insert(file_node, 'end', text="(Expand to view JSON data)",
                                   values=('', '', ''))
                
                file_count += 1
        
        self.status_bar.config(text=f"Loaded {len(sst_folders)} folders, {file_count} files")
    
    def expand_all(self):
        """Expand all tree nodes."""
        def expand_node(node):
            self.tree.item(node, open=True)
            for child in self.tree.get_children(node):
                expand_node(child)
        
        for item in self.tree.get_children():
            expand_node(item)
    
    def collapse_all(self):
        """Collapse all tree nodes."""
        def collapse_node(node):
            self.tree.item(node, open=False)
            for child in self.tree.get_children(node):
                collapse_node(child)
        
        for item in self.tree.get_children():
            collapse_node(item)
    
    def on_expand(self, event):
        """Handle tree node expansion - load JSON data for config files."""
        item = self.tree.focus()
        if not item:
            return
        
        tags = self.tree.item(item, 'tags')
        if not tags or not tags[0]:
            return
        
        file_path = Path(tags[0])
        if file_path.exists() and file_path.suffix == '.zenodo.json':
            # Check if we already loaded the JSON data
            children = self.tree.get_children(item)
            if children and self.tree.item(children[0], 'text') == "(Click to load JSON data)":
                # Remove placeholder
                self.tree.delete(children[0])
                
                # Load and display JSON data
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # Add JSON data as expandable children
                    for key, value in config_data.items():
                        if isinstance(value, dict):
                            # Nested dict - create parent node
                            parent_node = self.tree.insert(item, 'end', text=f"{key}:",
                                                          values=('', '', ''))
                            for sub_key, sub_value in value.items():
                                display_value = str(sub_value)
                                if len(display_value) > 100:
                                    display_value = display_value[:100] + "..."
                                self.tree.insert(parent_node, 'end', 
                                               text=f"  {sub_key}: {display_value}",
                                               values=('', '', ''))
                        elif isinstance(value, list):
                            # List - show items
                            if value:
                                parent_node = self.tree.insert(item, 'end', text=f"{key}: [{len(value)} items]",
                                                              values=('', '', ''))
                                for i, item_val in enumerate(value):
                                    if isinstance(item_val, dict):
                                        # List of dicts
                                        dict_node = self.tree.insert(parent_node, 'end', 
                                                                   text=f"  [{i+1}]",
                                                                   values=('', '', ''))
                                        for sub_key, sub_value in item_val.items():
                                            display_value = str(sub_value)
                                            if len(display_value) > 80:
                                                display_value = display_value[:80] + "..."
                                            self.tree.insert(dict_node, 'end',
                                                           text=f"    {sub_key}: {display_value}",
                                                           values=('', '', ''))
                                    else:
                                        display_value = str(item_val)
                                        if len(display_value) > 100:
                                            display_value = display_value[:100] + "..."
                                        self.tree.insert(parent_node, 'end',
                                                       text=f"  [{i+1}] {display_value}",
                                                       values=('', '', ''))
                            else:
                                self.tree.insert(item, 'end', text=f"{key}: []",
                                               values=('', '', ''))
                        else:
                            # Simple value
                            display_value = str(value)
                            if len(display_value) > 150:
                                display_value = display_value[:150] + "..."
                            self.tree.insert(item, 'end', text=f"{key}: {display_value}",
                                           values=('', '', ''))
                except Exception as e:
                    self.tree.insert(item, 'end', text=f"Error loading JSON: {e}",
                                   values=('', '', ''))
    
    def on_select(self, event):
        """Handle tree selection event."""
        selection = self.tree.selection()
        if not selection:
            self.selected_file = None
            self.selected_file_type = None
            self.update_button_states()
            return
        
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        values = self.tree.item(item, 'values')
        
        if tags and tags[0]:
            file_path = Path(tags[0])
            if file_path.exists():
                self.selected_file = file_path
                self.selected_file_type = values[0] if values else 'Unknown'
                self.show_file_details(file_path)
                self.update_button_states()
    
    def update_button_states(self):
        """Update button states based on selected file."""
        if not self.selected_file:
            self.upload_pdf_btn.config(state=tk.DISABLED)
            self.render_upload_btn.config(state=tk.DISABLED)
            self.sync_date_btn.config(state=tk.DISABLED)
            self.update_metadata_btn.config(state=tk.DISABLED)
            self.edit_config_btn.config(state=tk.DISABLED)
            self.edit_json_btn.config(state=tk.DISABLED)
            self.fetch_zenodo_btn.config(state=tk.DISABLED)
            return
        
        # Enable buttons based on file type
        if self.selected_file.suffix == '.zenodo.json':
            # Config file - can upload PDF, sync date, update metadata, edit config, edit JSON
            self.upload_pdf_btn.config(state=tk.NORMAL)
            self.render_upload_btn.config(state=tk.NORMAL)
            self.sync_date_btn.config(state=tk.NORMAL)
            self.update_metadata_btn.config(state=tk.NORMAL)
            self.edit_config_btn.config(state=tk.NORMAL)
            self.edit_json_btn.config(state=tk.NORMAL)
            self.fetch_zenodo_btn.config(state=tk.NORMAL)
        elif self.selected_file.suffix == '.tex':
            # LaTeX file - can render & upload, sync date, create/edit config
            # Check if config exists for edit JSON
            config_file = self.find_config_file(self.selected_file)
            self.upload_pdf_btn.config(state=tk.DISABLED)
            self.render_upload_btn.config(state=tk.NORMAL)
            self.sync_date_btn.config(state=tk.NORMAL)
            self.update_metadata_btn.config(state=tk.DISABLED)
            self.edit_config_btn.config(state=tk.NORMAL)
            self.edit_json_btn.config(state=tk.NORMAL if config_file else tk.DISABLED)
            self.fetch_zenodo_btn.config(state=tk.NORMAL)
        elif self.selected_file.suffix == '.pdf':
            # PDF file - can sync date, create/edit config
            # Check if config exists for edit JSON
            config_file = self.find_config_file(self.selected_file)
            self.upload_pdf_btn.config(state=tk.DISABLED)
            self.render_upload_btn.config(state=tk.DISABLED)
            self.sync_date_btn.config(state=tk.NORMAL)
            self.update_metadata_btn.config(state=tk.DISABLED)
            self.edit_config_btn.config(state=tk.NORMAL)
            self.edit_json_btn.config(state=tk.NORMAL if config_file else tk.DISABLED)
            self.fetch_zenodo_btn.config(state=tk.NORMAL)
        else:
            self.upload_pdf_btn.config(state=tk.DISABLED)
            self.render_upload_btn.config(state=tk.DISABLED)
            self.sync_date_btn.config(state=tk.DISABLED)
            self.update_metadata_btn.config(state=tk.DISABLED)
            self.edit_config_btn.config(state=tk.DISABLED)
            self.edit_json_btn.config(state=tk.DISABLED)
            self.fetch_zenodo_btn.config(state=tk.DISABLED)
    
    def show_context_menu(self, event):
        """Show context menu on right-click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.on_select(None)  # Update selection
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def log(self, message):
        """Add message to log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def find_config_file(self, file_path: Path) -> Path | None:
        """Find corresponding config file for a given file."""
        if file_path.suffix == '.zenodo.json':
            return file_path
        
        # Try to find config file
        base_name = file_path.stem
        config_file = file_path.parent / f"{base_name}.zenodo.json"
        if config_file.exists():
            return config_file
        
        # Try with parent directory name
        parent_name = file_path.parent.name
        config_file = file_path.parent / f"{parent_name}.zenodo.json"
        if config_file.exists():
            return config_file
        
        return None
    
    def upload_pdf_selected(self):
        """Upload PDF for selected config file."""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a config file")
            return
        
        config_file = self.find_config_file(self.selected_file)
        if not config_file or config_file.suffix != '.zenodo.json':
            messagebox.showwarning("Invalid Selection", "Please select a .zenodo.json config file")
            return
        
        self.log(f"Uploading PDF for: {config_file.name}")
        self.status_bar.config(text="Uploading PDF...")
        
        def upload_thread():
            try:
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / 'upload_single_pdf.py'), 
                     str(config_file.relative_to(self.base_dir))],
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode == 0:
                    self.log("✓ Upload successful!")
                    self.status_bar.config(text="Upload successful")
                    messagebox.showinfo("Success", "PDF uploaded successfully!")
                else:
                    self.log(f"✗ Upload failed: {result.stderr}")
                    self.status_bar.config(text="Upload failed")
                    messagebox.showerror("Error", f"Upload failed:\n{result.stderr}")
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def render_and_upload_selected(self):
        """Render PDF and upload for selected file."""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        
        # Find config file
        config_file = self.find_config_file(self.selected_file)
        if not config_file:
            messagebox.showwarning("No Config", "Could not find corresponding .zenodo.json config file")
            return
        
        self.log(f"Rendering and uploading: {config_file.name}")
        self.status_bar.config(text="Rendering PDF...")
        
        def render_thread():
            try:
                # Import and use the render function directly
                from render_and_update_zenodo import process_config_file
                from zenodo_automation import read_token_from_zenodo_py
                
                token = read_token_from_zenodo_py()
                if not token:
                    raise Exception("No Zenodo token found")
                
                automation = ZenodoAutomation(token, sandbox=False)
                
                result = process_config_file(config_file, automation, self.base_dir)
                
                if result['status'] == 'success':
                    self.log("✓ Render and upload successful!")
                    self.status_bar.config(text="Success")
                    messagebox.showinfo("Success", "PDF rendered and uploaded successfully!")
                else:
                    self.log(f"✗ Failed: {result['message']}")
                    self.status_bar.config(text="Failed")
                    messagebox.showerror("Error", result['message'])
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=render_thread, daemon=True).start()
    
    def sync_date_selected(self):
        """Sync publication date for selected file."""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        
        config_file = self.find_config_file(self.selected_file)
        if not config_file:
            messagebox.showwarning("No Config", "Could not find corresponding .zenodo.json config file")
            return
        
        self.log(f"Syncing publication date: {config_file.name}")
        self.status_bar.config(text="Syncing date...")
        
        def sync_thread():
            try:
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / 'sync_publication_date.py'),
                     '--config', str(config_file.relative_to(self.base_dir)), '--update-zenodo'],
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode == 0:
                    self.log("✓ Date synced successfully!")
                    self.status_bar.config(text="Date synced")
                    messagebox.showinfo("Success", "Publication date synced successfully!")
                    self.refresh_tree()
                else:
                    self.log(f"✗ Sync failed: {result.stderr}")
                    self.status_bar.config(text="Sync failed")
                    messagebox.showerror("Error", f"Sync failed:\n{result.stderr}")
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def update_metadata_selected(self):
        """Update Zenodo metadata for selected config file."""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a config file")
            return
        
        config_file = self.find_config_file(self.selected_file)
        if not config_file or config_file.suffix != '.zenodo.json':
            messagebox.showwarning("Invalid Selection", "Please select a .zenodo.json config file")
            return
        
        self.log(f"Updating metadata: {config_file.name}")
        self.status_bar.config(text="Updating metadata...")
        
        def update_thread():
            try:
                from render_and_update_zenodo import update_zenodo_metadata
                from zenodo_automation import read_token_from_zenodo_py, ZenodoAutomation
                import json
                
                token = read_token_from_zenodo_py()
                if not token:
                    raise Exception("No Zenodo token found")
                
                automation = ZenodoAutomation(token, sandbox=False)
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                deposit_id = config_data.get('deposit_id', '')
                if not deposit_id:
                    raise Exception("No deposit_id in config")
                
                if update_zenodo_metadata(automation, deposit_id, config_data):
                    self.log("✓ Metadata updated successfully!")
                    self.status_bar.config(text="Metadata updated")
                    messagebox.showinfo("Success", "Metadata updated successfully!")
                else:
                    self.log("✗ Metadata update failed")
                    self.status_bar.config(text="Update failed")
                    messagebox.showerror("Error", "Failed to update metadata")
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def edit_json_selected(self):
        """Open JSON editor for selected config file."""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        
        # Find config file
        if self.selected_file.suffix == '.zenodo.json':
            config_file = self.selected_file
        else:
            config_file = self.find_config_file(self.selected_file)
            if not config_file:
                messagebox.showwarning("No Config", "No config file found. Use 'Create/Edit Config' to create one.")
                return
        
        # Open JSON editor
        self.open_json_editor(config_file)
    
    def open_json_editor(self, config_file: Path):
        """Open a simple JSON editor dialog."""
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Edit JSON: {config_file.name}")
        editor_window.geometry("800x600")
        
        # Load existing JSON
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                json_content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read config file: {e}")
            editor_window.destroy()
            return
        
        # Create frame with text area
        main_frame = ttk.Frame(editor_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Label
        label = ttk.Label(main_frame, text="Edit JSON (be careful with syntax):", font=('Arial', 10, 'bold'))
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # Text area with scrollbars
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        json_text = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, font=('Consolas', 10))
        json_text.insert(1.0, json_content)
        json_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        def validate_and_save():
            try:
                # Get content
                content = json_text.get(1.0, tk.END).strip()
                
                # Validate JSON
                parsed = json.loads(content)
                
                # Save to file
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Config saved to {config_file.name}")
                editor_window.destroy()
                self.refresh_tree()
                self.log(f"Saved JSON config: {config_file.name}")
                
                # Refresh details if this file is selected
                if self.selected_file == config_file:
                    self.show_file_details(config_file)
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Invalid JSON syntax:\n{e}\n\nPlease fix the errors and try again.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {e}")
        
        def format_json():
            try:
                content = json_text.get(1.0, tk.END).strip()
                parsed = json.loads(content)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                json_text.delete(1.0, tk.END)
                json_text.insert(1.0, formatted)
                messagebox.showinfo("Success", "JSON formatted successfully")
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Cannot format invalid JSON:\n{e}")
        
        ttk.Button(button_frame, text="Format JSON", command=format_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=validate_and_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=editor_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def fetch_from_zenodo_selected(self):
        """Fetch config from Zenodo and save as .zenodo.online.json"""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        
        # Get DOI from selected file or its config
        doi = None
        config_file = None
        
        if self.selected_file.suffix == '.zenodo.json':
            config_file = self.selected_file
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                doi = config_data.get('doi', '')
            except:
                pass
        else:
            # Try to find config file
            config_file = self.find_config_file(self.selected_file)
            if config_file:
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    doi = config_data.get('doi', '')
                except:
                    pass
            
            # If no DOI in config, try to extract from LaTeX
            if not doi and self.selected_file.suffix == '.tex':
                try:
                    with open(self.selected_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    doi_match = re.search(r'10\.5281/zenodo\.(\d+)', content)
                    if doi_match:
                        doi = doi_match.group(0)
                except:
                    pass
        
        if not doi:
            # Ask user for DOI
            doi = simpledialog.askstring("Enter DOI", "Enter Zenodo DOI (e.g., 10.5281/zenodo.123456):")
            if not doi:
                return
        
        # Fetch from Zenodo
        self.fetch_from_zenodo(doi, config_file or self.selected_file, config_file)
    
    def fetch_from_zenodo(self, doi: str, target_file: Path, config_file: Path = None):
        """Fetch config from Zenodo API and save as .zenodo.online.json"""
        self.log(f"Fetching config from Zenodo for DOI: {doi}")
        self.status_bar.config(text="Fetching from Zenodo...")
        
        def fetch_thread():
            try:
                token = read_token_from_zenodo_py()
                if not token:
                    raise Exception("No Zenodo token found")
                
                automation = ZenodoAutomation(token, sandbox=False)
                
                # Extract record ID from DOI
                record_id = doi.split('.')[-1]
                
                # Try published record first
                url = f"{automation.base_url}/api/records/{record_id}"
                response = requests.get(url, headers=automation.headers)
                
                if response.status_code == 200:
                    record = response.json()
                else:
                    # Try draft deposit
                    url = f"{automation.base_url}/api/deposit/depositions/{record_id}"
                    response = requests.get(url, headers=automation.headers)
                    if response.status_code == 200:
                        deposit = response.json()
                        record = {
                            'id': deposit.get('id'),
                            'metadata': deposit.get('metadata', {})
                        }
                    else:
                        raise Exception(f"Failed to fetch from Zenodo: {response.status_code} - {response.text}")
                
                # Convert to config format
                metadata = record.get('metadata', {})
                record_id = record.get('id', '')
                
                # Get DOI
                fetched_doi = metadata.get('doi', '')
                if not fetched_doi:
                    prereserve = metadata.get('prereserve_doi', {})
                    fetched_doi = prereserve.get('doi', '') if prereserve else ''
                
                # Create config data
                online_config = {
                    "title": metadata.get('title', ''),
                    "creators": metadata.get('creators', []),
                    "description": metadata.get('description', ''),
                    "keywords": metadata.get('keywords', []),
                    "publication_date": metadata.get('publication_date', ''),
                    "doi": fetched_doi,
                    "tex_file": target_file.name if target_file.suffix == '.tex' else '',
                    "upload_type": metadata.get('upload_type', 'publication'),
                    "publication_type": metadata.get('publication_type', 'preprint'),
                    "access_right": metadata.get('access_right', 'open'),
                    "license": metadata.get('license', 'cc-by-4.0'),
                    "deposit_id": str(record_id),
                    "language": metadata.get('language', 'eng')
                }
                
                # Add communities if present
                if metadata.get('communities'):
                    online_config['communities'] = metadata['communities']
                
                # Find local config file if not provided
                local_config = config_file
                if not local_config:
                    if target_file.suffix == '.zenodo.json':
                        local_config = target_file
                    else:
                        # Try to find config file
                        base_name = target_file.stem
                        potential_config = target_file.parent / f"{base_name}.zenodo.json"
                        if not potential_config.exists() and re.match(r'^SST-\d+', target_file.parent.name):
                            potential_config = target_file.parent / f"{target_file.parent.name}.zenodo.json"
                        if potential_config.exists():
                            local_config = potential_config
                
                # Determine where to save
                if local_config and local_config.exists() and local_config.suffix == '.zenodo.json':
                    # Local config exists - save as .zenodo.online.json for comparison
                    online_file = local_config.parent / local_config.name.replace('.zenodo.json', '.zenodo.online.json')
                    with open(online_file, 'w', encoding='utf-8') as f:
                        json.dump(online_config, f, indent=2, ensure_ascii=False)
                    
                    self.log(f"✓ Fetched and saved to {online_file.name}")
                    self.status_bar.config(text="Fetched successfully")
                    
                    # Ask if user wants to merge
                    if messagebox.askyesno("Merge Configs?", 
                                         f"Online config saved to {online_file.name}\n\n"
                                         "Would you like to merge it with your local config?"):
                        self.merge_configs(local_config, online_file)
                    else:
                        self.refresh_tree()
                else:
                    # No local config exists - create one from Zenodo data
                    # Determine save location based on target file
                    if target_file.suffix == '.tex':
                        new_config_file = target_file.parent / (target_file.stem + '.zenodo.json')
                    elif re.match(r'^SST-\d+', target_file.parent.name):
                        # Use folder name for config
                        new_config_file = target_file.parent / (target_file.parent.name + '.zenodo.json')
                    else:
                        # Use target file name
                        new_config_file = target_file.parent / (target_file.stem + '.zenodo.json')
                    
                    # Update tex_file path in config
                    if target_file.suffix == '.tex':
                        online_config['tex_file'] = str(target_file.relative_to(self.base_dir))
                    elif local_config and local_config.exists() and local_config.suffix == '.zenodo.json':
                        # Keep existing tex_file if available
                        try:
                            with open(local_config, 'r', encoding='utf-8') as f:
                                old_config = json.load(f)
                            if old_config.get('tex_file'):
                                online_config['tex_file'] = old_config['tex_file']
                        except:
                            pass
                    
                    # Save as main config file
                    with open(new_config_file, 'w', encoding='utf-8') as f:
                        json.dump(online_config, f, indent=2, ensure_ascii=False)
                    
                    self.log(f"✓ Created config file: {new_config_file.name}")
                    self.status_bar.config(text="Config created successfully")
                    messagebox.showinfo("Success", f"Config file created from Zenodo:\n{new_config_file.name}")
                    self.refresh_tree()
                    
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", f"Failed to fetch from Zenodo:\n{e}")
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def merge_configs_selected(self):
        """Merge local and online config files."""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        
        # Find local config
        if self.selected_file.suffix == '.zenodo.json':
            local_config = self.selected_file
        else:
            local_config = self.find_config_file(self.selected_file)
            if not local_config:
                messagebox.showwarning("No Local Config", "No local config file found")
                return
        
        # Find online config
        if local_config.name.endswith('.zenodo.online.json'):
            online_config = local_config
            local_config = local_config.parent / local_config.name.replace('.zenodo.online.json', '.zenodo.json')
        else:
            online_config = local_config.parent / local_config.name.replace('.zenodo.json', '.zenodo.online.json')
        
        if not online_config.exists():
            messagebox.showwarning("No Online Config", f"Online config not found: {online_config.name}\n\nUse 'Fetch from Zenodo' first.")
            return
        
        self.merge_configs(local_config, online_config)
    
    def merge_configs(self, local_config: Path, online_config: Path):
        """Merge local and online config files with a dialog."""
        try:
            with open(local_config, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            with open(online_config, 'r', encoding='utf-8') as f:
                online_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read config files: {e}")
            return
        
        # Open merge dialog
        merge_window = tk.Toplevel(self.root)
        merge_window.title("Merge Config Files")
        merge_window.geometry("1000x700")
        
        # Create paned window
        paned = ttk.PanedWindow(merge_window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left: Local config
        local_frame = ttk.LabelFrame(paned, text=f"Local: {local_config.name}")
        paned.add(local_frame, weight=1)
        
        local_text = scrolledtext.ScrolledText(local_frame, wrap=tk.NONE, font=('Consolas', 9))
        local_text.insert(1.0, json.dumps(local_data, indent=2, ensure_ascii=False))
        local_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right: Online config
        online_frame = ttk.LabelFrame(paned, text=f"Online: {online_config.name}")
        paned.add(online_frame, weight=1)
        
        online_text = scrolledtext.ScrolledText(online_frame, wrap=tk.NONE, font=('Consolas', 9))
        online_text.insert(1.0, json.dumps(online_data, indent=2, ensure_ascii=False))
        online_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Merge strategy frame
        strategy_frame = ttk.LabelFrame(merge_window, text="Merge Strategy")
        strategy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        merge_strategy = tk.StringVar(value="online_prefer")
        ttk.Radiobutton(strategy_frame, text="Prefer Online (overwrite local)", 
                       variable=merge_strategy, value="online_prefer").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(strategy_frame, text="Prefer Local (keep local values)", 
                       variable=merge_strategy, value="local_prefer").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(strategy_frame, text="Smart Merge (combine both)", 
                       variable=merge_strategy, value="smart").pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(merge_window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def perform_merge():
            try:
                strategy = merge_strategy.get()
                merged = local_data.copy()
                
                if strategy == "online_prefer":
                    # Online values take precedence
                    merged.update(online_data)
                elif strategy == "local_prefer":
                    # Local values take precedence, but add missing keys from online
                    for key, value in online_data.items():
                        if key not in merged:
                            merged[key] = value
                else:  # smart
                    # Smart merge: combine arrays, prefer non-empty strings, merge dicts
                    for key, online_value in online_data.items():
                        if key not in merged:
                            merged[key] = online_value
                        elif isinstance(online_value, dict) and isinstance(merged.get(key), dict):
                            # Merge nested dicts
                            merged[key] = {**merged[key], **online_value}
                        elif isinstance(online_value, list) and isinstance(merged.get(key), list):
                            # Combine lists (remove duplicates)
                            combined = list(merged[key])
                            for item in online_value:
                                if item not in combined:
                                    combined.append(item)
                            merged[key] = combined
                        elif isinstance(online_value, str) and online_value.strip():
                            # Prefer non-empty strings
                            if not merged.get(key) or not merged[key].strip():
                                merged[key] = online_value
                        else:
                            # Keep local value
                            pass
                
                # Save merged config
                with open(local_config, 'w', encoding='utf-8') as f:
                    json.dump(merged, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Merged config saved to {local_config.name}")
                merge_window.destroy()
                self.refresh_tree()
                self.log(f"Merged configs: {local_config.name}")
                
                # Refresh details if this file is selected
                if self.selected_file == local_config:
                    self.show_file_details(local_config)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge: {e}")
        
        ttk.Button(button_frame, text="Merge and Save", command=perform_merge).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=merge_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def render_all_and_update(self):
        """Render all PDFs and update Zenodo entries."""
        if not messagebox.askyesno("Confirm", "This will render and upload all PDFs. Continue?"):
            return
        
        self.log("Starting bulk render and update...")
        self.status_bar.config(text="Rendering all PDFs...")
        
        def bulk_thread():
            try:
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / 'render_and_update_zenodo.py'), '--yes'],
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.log(result.stdout)
                if result.stderr:
                    self.log(result.stderr)
                
                if result.returncode == 0:
                    self.log("✓ Bulk render and update completed!")
                    self.status_bar.config(text="Bulk update completed")
                    messagebox.showinfo("Success", "Bulk render and update completed!")
                    self.refresh_tree()
                else:
                    self.log("✗ Bulk update had errors")
                    self.status_bar.config(text="Bulk update completed with errors")
                    messagebox.showwarning("Warning", "Bulk update completed with some errors. Check log.")
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=bulk_thread, daemon=True).start()
    
    def sync_all_dates(self):
        """Sync all publication dates."""
        if not messagebox.askyesno("Confirm", "This will sync publication dates for all config files. Continue?"):
            return
        
        self.log("Starting bulk date sync...")
        self.status_bar.config(text="Syncing all dates...")
        
        def bulk_thread():
            try:
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / 'sync_publication_date.py'), '--all', '--update-zenodo'],
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.log(result.stdout)
                if result.stderr:
                    self.log(result.stderr)
                
                if result.returncode == 0:
                    self.log("✓ Bulk date sync completed!")
                    self.status_bar.config(text="Date sync completed")
                    messagebox.showinfo("Success", "All publication dates synced!")
                    self.refresh_tree()
                else:
                    self.log("✗ Date sync had errors")
                    self.status_bar.config(text="Date sync completed with errors")
                    messagebox.showwarning("Warning", "Date sync completed with some errors. Check log.")
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=bulk_thread, daemon=True).start()
    
    def update_all_creators(self):
        """Update all creator information."""
        if not messagebox.askyesno("Confirm", "This will update creator information for all config files. Continue?"):
            return
        
        self.log("Starting bulk creator update...")
        self.status_bar.config(text="Updating creators...")
        
        def bulk_thread():
            try:
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / 'update_config_creators.py')],
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.log(result.stdout)
                if result.stderr:
                    self.log(result.stderr)
                
                if result.returncode == 0:
                    self.log("✓ Bulk creator update completed!")
                    self.status_bar.config(text="Creator update completed")
                    messagebox.showinfo("Success", "All creators updated!")
                    self.refresh_tree()
                else:
                    self.log("✗ Creator update had errors")
                    self.status_bar.config(text="Creator update completed with errors")
                    messagebox.showwarning("Warning", "Creator update completed with some errors. Check log.")
            except Exception as e:
                self.log(f"✗ Error: {e}")
                self.status_bar.config(text="Error")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=bulk_thread, daemon=True).start()
    
    def edit_config_selected(self):
        """Create or edit config file for selected file."""
        if not self.selected_file:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        
        # Determine target config file
        if self.selected_file.suffix == '.zenodo.json':
            config_file = self.selected_file
        else:
            # Find or create config file for this file
            base_name = self.selected_file.stem
            config_file = self.selected_file.parent / f"{base_name}.zenodo.json"
            
            # Try parent folder name if base name doesn't work
            if not config_file.exists() and re.match(r'^SST-\d+', self.selected_file.parent.name):
                config_file = self.selected_file.parent / f"{self.selected_file.parent.name}.zenodo.json"
        
        # Open config editor window
        self.open_config_editor(config_file, self.selected_file)
    
    def open_config_editor(self, config_file: Path, source_file: Path):
        """Open a window to edit/create config file."""
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Edit Config: {config_file.name}")
        editor_window.geometry("900x700")
        
        # Load existing config or create new
        config_data = {}
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except:
                pass
        
        # If new config, try to extract from source file
        if not config_data and source_file.suffix == '.tex':
            from check_and_validate_zenodo_configs import extract_metadata_from_latex
            metadata = extract_metadata_from_latex(source_file)
            config_data = {
                'title': metadata.get('title', ''),
                'creators': metadata.get('creators', [{'name': 'Omar Iskandarani', 'affiliation': 'Independent Researcher, Groningen, The Netherlands', 'orcid': '0009-0006-1686-3961'}]),
                'description': metadata.get('description', ''),
                'keywords': metadata.get('keywords', []),
                'publication_date': metadata.get('publication_date', ''),
                'doi': metadata.get('doi', ''),
                'tex_file': str(source_file.relative_to(self.base_dir)),
                'upload_type': 'publication',
                'publication_type': 'preprint',
                'access_right': 'open',
                'license': 'cc-by-4.0',
                'language': 'eng'
            }
        
        # Create notebook for tabs
        notebook = ttk.Notebook(editor_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Basic info tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        
        # Title
        ttk.Label(basic_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        title_entry = tk.Text(basic_frame, height=2, width=80)
        title_entry.insert(1.0, config_data.get('title', ''))
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Description
        ttk.Label(basic_frame, text="Description:").grid(row=1, column=0, sticky=tk.W+tk.N, padx=5, pady=5)
        desc_text = scrolledtext.ScrolledText(basic_frame, height=10, width=80)
        desc_text.insert(1.0, config_data.get('description', ''))
        desc_text.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # DOI
        ttk.Label(basic_frame, text="DOI:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        doi_entry = ttk.Entry(basic_frame, width=80)
        doi_entry.insert(0, config_data.get('doi', ''))
        doi_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Publication Date
        ttk.Label(basic_frame, text="Publication Date:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        date_entry = ttk.Entry(basic_frame, width=80)
        date_entry.insert(0, config_data.get('publication_date', ''))
        date_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Keywords
        ttk.Label(basic_frame, text="Keywords (comma-separated):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        keywords_entry = ttk.Entry(basic_frame, width=80)
        keywords_entry.insert(0, ', '.join(config_data.get('keywords', [])))
        keywords_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # JSON tab
        json_frame = ttk.Frame(notebook)
        notebook.add(json_frame, text="Raw JSON")
        
        json_text = scrolledtext.ScrolledText(json_frame, wrap=tk.NONE, font=('Consolas', 10))
        json_text.insert(1.0, json.dumps(config_data, indent=2, ensure_ascii=False))
        json_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(editor_window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def save_config():
            try:
                # Get data from basic tab
                new_config = {
                    'title': title_entry.get(1.0, tk.END).strip(),
                    'description': desc_text.get(1.0, tk.END).strip(),
                    'doi': doi_entry.get().strip(),
                    'publication_date': date_entry.get().strip(),
                    'keywords': [k.strip() for k in keywords_entry.get().split(',') if k.strip()],
                    'creators': config_data.get('creators', [{'name': 'Omar Iskandarani', 'affiliation': 'Independent Researcher, Groningen, The Netherlands', 'orcid': '0009-0006-1686-3961'}]),
                    'tex_file': config_data.get('tex_file', str(source_file.relative_to(self.base_dir))),
                    'upload_type': config_data.get('upload_type', 'publication'),
                    'publication_type': config_data.get('publication_type', 'preprint'),
                    'access_right': config_data.get('access_right', 'open'),
                    'license': config_data.get('license', 'cc-by-4.0'),
                    'language': config_data.get('language', 'eng')
                }
                
                # Add deposit_id if exists
                if config_data.get('deposit_id'):
                    new_config['deposit_id'] = config_data['deposit_id']
                
                # Save to file
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(new_config, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Config saved to {config_file.name}")
                editor_window.destroy()
                self.refresh_tree()
                self.log(f"Saved config: {config_file.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=editor_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        basic_frame.columnconfigure(1, weight=1)
        basic_frame.rowconfigure(1, weight=1)
    
    def show_file_details(self, file_path: Path):
        """Show details for selected file."""
        self.details_text.delete(1.0, tk.END)
        
        info = self.get_file_info(file_path)
        
        details = f"File: {file_path.name}\n"
        details += f"Path: {file_path}\n"
        # Ensure type is correctly displayed
        if file_path.suffix == '.zenodo.json':
            if '.online.json' in file_path.name:
                details += f"Type: Config (Online)\n"
            else:
                details += f"Type: Config\n"
        else:
            details += f"Type: {info['type']}\n"
        details += f"Status: {info['status']}\n"
        
        if info['doi']:
            details += f"DOI: {info['doi']}\n"
        
        # If this is a config file, show its JSON directly
        if file_path.suffix == '.zenodo.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                details += "\n=== Config File Contents ===\n\n"
                details += json.dumps(config_data, indent=2, ensure_ascii=False)
                
                details += "\n\n=== Key Fields ===\n"
                details += f"Title: {config_data.get('title', 'N/A')}\n"
                details += f"DOI: {config_data.get('doi', 'N/A')}\n"
                details += f"Deposit ID: {config_data.get('deposit_id', 'N/A')}\n"
                details += f"Publication Date: {config_data.get('publication_date', 'N/A')}\n"
                details += f"Publication Type: {config_data.get('publication_type', 'N/A')}\n"
                
                if config_data.get('creators'):
                    details += f"\nCreators ({len(config_data['creators'])}):\n"
                    for i, creator in enumerate(config_data['creators'], 1):
                        details += f"  {i}. {creator.get('name', 'N/A')}\n"
                        if creator.get('affiliation'):
                            details += f"     Affiliation: {creator['affiliation']}\n"
                        if creator.get('orcid'):
                            details += f"     ORCID: {creator['orcid']}\n"
                
                if config_data.get('keywords'):
                    details += f"\nKeywords: {', '.join(config_data['keywords'])}\n"
                
                if config_data.get('description'):
                    desc = config_data['description']
                    if len(desc) > 500:
                        desc = desc[:500] + "..."
                    details += f"\nDescription: {desc}\n"
            except Exception as e:
                details += f"\nError reading config: {e}\n"
        
        # For non-config files, try to find and show related config file
        elif file_path.suffix in ['.tex', '.pdf']:
            config_file = self.find_config_file(file_path)
            if config_file and config_file.exists() and config_file != file_path:
                details += f"\n=== Related Config File: {config_file.name} ===\n"
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    details += f"\nTitle: {config_data.get('title', 'N/A')}\n"
                    details += f"DOI: {config_data.get('doi', 'N/A')}\n"
                    details += f"Deposit ID: {config_data.get('deposit_id', 'N/A')}\n"
                    details += f"Publication Date: {config_data.get('publication_date', 'N/A')}\n"
                    details += f"Publication Type: {config_data.get('publication_type', 'N/A')}\n"
                    
                    if config_data.get('creators'):
                        details += f"\nCreators ({len(config_data['creators'])}):\n"
                        for i, creator in enumerate(config_data['creators'], 1):
                            details += f"  {i}. {creator.get('name', 'N/A')}\n"
                            if creator.get('affiliation'):
                                details += f"     Affiliation: {creator['affiliation']}\n"
                            if creator.get('orcid'):
                                details += f"     ORCID: {creator['orcid']}\n"
                    
                    if config_data.get('keywords'):
                        details += f"\nKeywords: {', '.join(config_data['keywords'])}\n"
                    
                    if config_data.get('description'):
                        desc = config_data['description']
                        if len(desc) > 1000:
                            desc = desc[:1000] + "..."
                        details += f"\nDescription:\n{desc}\n"
                    
                    details += "\n=== Full JSON ===\n"
                    details += json.dumps(config_data, indent=2, ensure_ascii=False)
                except Exception as e:
                    details += f"\nError reading config: {e}\n"
        
        if info['details'] and not isinstance(info['details'], dict):
            details += "\nDetails:\n"
            for key, value in info['details'].items():
                details += f"  {key}: {value}\n"
        
        # Additional info based on file type
        if file_path.suffix == '.tex':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for \begin{document}
                if '\\begin{document}' in content:
                    details += "\n✓ Has \\begin{document}\n"
                else:
                    details += "\n✗ Missing \\begin{document}\n"
                
                # Check for title
                if '\\title' in content or '\\papertitle' in content:
                    details += "✓ Has title\n"
                else:
                    details += "✗ Missing title\n"
                
                # Check for DOI
                if re.search(r'10\.5281/zenodo\.\d+', content):
                    details += "✓ Has DOI in LaTeX\n"
                else:
                    details += "✗ No DOI in LaTeX\n"
            except:
                pass
        
        elif file_path.suffix == '.pdf':
            try:
                size = file_path.stat().st_size
                size_mb = size / (1024 * 1024)
                details += f"\nSize: {size_mb:.2f} MB\n"
                
                # Check if corresponding .tex exists
                tex_file = file_path.with_suffix('.tex')
                if tex_file.exists():
                    tex_mtime = tex_file.stat().st_mtime
                    pdf_mtime = file_path.stat().st_mtime
                    if pdf_mtime < tex_mtime:
                        details += "⚠ PDF is older than LaTeX source\n"
                    else:
                        details += "✓ PDF is up to date\n"
            except:
                pass
        
        self.details_text.insert(1.0, details)

def main():
    root = tk.Tk()
    app = ZenodoFileViewer(root)
    root.mainloop()

if __name__ == '__main__':
    main()
