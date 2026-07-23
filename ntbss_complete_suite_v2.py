#!/usr/bin/env python3
"""
NTBSS Complete Suite v2 - Professional Save Editor
Force-Save + Advanced Editor + DLC Unlocker
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import subprocess
import json
import re
from pathlib import Path
from threading import Thread
from collections import defaultdict
from typing import Dict, List, Tuple
import struct


class NTBSSEditorV2:
    """Professional NTBSS Save Editor with modern UI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NTBSS Complete Suite v2 - Force-Save + Editor + DLC Unlocker")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Data storage
        self.current_save = None
        self.save_data = defaultdict(lambda: {"value": 0, "type": "flag", "category": "Other"})
        self.game_dir = None
        self.parsing = False
        
        # ID database
        self.id_database = self._load_id_database()
        
        self.setup_ui()
    
    def _load_id_database(self) -> Dict:
        """Load or create ID database"""
        db_file = Path("ntbss_ids.json")
        if db_file.exists():
            try:
                with open(db_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default database
        return {
            "Currency": ["ID_Counter_Money", "ID_Counter_SkillPoint", "ID_Counter_MasterPoint"],
            "Progression": ["ID_Counter_PlayerExperience", "ID_Counter_PlayTimeMinute"],
            "Scrolls": ["ID_Counter_Scroll_Plain", "ID_Counter_Scroll_Quality", "ID_Counter_Scroll_Valuable"],
            "PVP": ["ID_Counter_Play_PVP", "ID_Counter_Win_PVP", "ID_Counter_PVP_Kill"],
            "Mentors": ["ID_Counter_MasterPoint_Naruto", "ID_Counter_MasterRank_Naruto"],
            "Other": []
        }
    
    def setup_ui(self):
        """Create main UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Save (Ctrl+O)", command=self.load_save)
        file_menu.add_command(label="Save Changes (Ctrl+S)", command=self.save_changes)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Parse IDs from Save", command=self.parse_save_ids_threaded)
        tools_menu.add_command(label="Find Game Directory", command=self.find_game_dir)
        tools_menu.add_command(label="Create Directories", command=self.create_directories)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        self.root.bind('<Control-o>', lambda e: self.load_save())
        self.root.bind('<Control-s>', lambda e: self.save_changes())
        
        # Main container with notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Force-Save
        self.force_save_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.force_save_tab, text="💾 Force-Save")
        self._setup_force_save_tab()
        
        # Tab 2: Save Editor
        self.editor_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_tab, text="✏️ Save Editor")
        self._setup_editor_tab()
        
        # Tab 3: Bulk Operations
        self.bulk_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.bulk_tab, text="⚡ Bulk Operations")
        self._setup_bulk_tab()
        
        # Tab 4: DLC Unlocker
        self.dlc_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dlc_tab, text="🎮 DLC Unlocker")
        self._setup_dlc_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=2)
    
    def _setup_force_save_tab(self):
        """Force-Save management tab"""
        main_frame = ttk.Frame(self.force_save_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = ttk.Label(main_frame, text="Force-Save Tool", font=("Arial", 18, "bold"))
        title.pack(pady=20)
        
        desc = ttk.Label(main_frame, text="Dump your online save to disk or load a modified save",
                        font=("Arial", 11))
        desc.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)
        
        ttk.Button(button_frame, text="📥 Dump Save (Export)", command=self.dump_save,
                  width=30).pack(pady=15)
        ttk.Button(button_frame, text="📤 Upload Save (Import)", command=self.upload_save,
                  width=30).pack(pady=15)
        
        # Instructions
        info_text = """⚠️  IMPORTANT:
        
1. Make sure you're IN-GAME (not on title screen)
2. Wait 1-2 seconds after clicking Dump
3. After Upload, return to title screen
4. Re-enter the game for changes to sync

This will communicate with the UE4SS Lua mod to access your save."""
        
        info_label = ttk.Label(main_frame, text=info_text, font=("Arial", 10),
                              justify=tk.LEFT, foreground="orange")
        info_label.pack(pady=30, padx=20)
    
    def _setup_editor_tab(self):
        """Advanced save editor tab"""
        main_frame = ttk.Frame(self.editor_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        left_controls = ttk.Frame(control_frame)
        left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load save button
        ttk.Button(left_controls, text="📂 Load Save", command=self.load_save).pack(side=tk.LEFT, padx=5)
        
        # Search
        ttk.Label(left_controls, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = ttk.Entry(left_controls, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Category filter
        ttk.Label(left_controls, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="All")
        self.category_var.trace('w', self._on_category_change)
        categories = ["All", "Currency", "Scrolls", "Progression", "Story", "PVP", 
                     "Missions", "Mentors", "Customization", "Items", "Other"]
        category_combo = ttk.Combobox(left_controls, textvariable=self.category_var,
                                     values=categories, state="readonly", width=12)
        category_combo.pack(side=tk.LEFT, padx=5)
        
        right_controls = ttk.Frame(control_frame)
        right_controls.pack(side=tk.RIGHT)
        
        ttk.Button(right_controls, text="🔄 Refresh", command=self._refresh_editor_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_controls, text="📊 Parse IDs", command=self.parse_save_ids_threaded).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_controls, text="💾 Save", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        
        # Editor list (Treeview)
        tree_frame = ttk.LabelFrame(main_frame, text="Save IDs & Values", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.id_tree = ttk.Treeview(tree_frame,
                                   columns=("ID", "Value", "Type", "Category"),
                                   show='tree headings',
                                   height=25,
                                   yscrollcommand=vsb.set,
                                   xscrollcommand=hsb.set)
        self.id_tree.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.id_tree.yview)
        hsb.config(command=self.id_tree.xview)
        
        # Configure columns
        self.id_tree.column("#0", width=0)
        self.id_tree.column("ID", anchor=tk.W, width=350)
        self.id_tree.column("Value", anchor=tk.CENTER, width=100)
        self.id_tree.column("Type", anchor=tk.CENTER, width=80)
        self.id_tree.column("Category", anchor=tk.CENTER, width=100)
        
        self.id_tree.heading("ID", text="ID Name", anchor=tk.W)
        self.id_tree.heading("Value", text="Current Value")
        self.id_tree.heading("Type", text="Type")
        self.id_tree.heading("Category", text="Category")
        
        # Bind double-click to edit
        self.id_tree.bind('<Double-1>', lambda e: self._edit_selected_value())
        
        # Bottom info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="💡 Double-click a value to edit", foreground="blue").pack(side=tk.LEFT, padx=5)
        self.count_var = tk.StringVar(value="No save loaded")
        ttk.Label(info_frame, textvariable=self.count_var).pack(side=tk.RIGHT, padx=5)
    
    def _setup_bulk_tab(self):
        """Bulk operations tab"""
        main_frame = ttk.Frame(self.bulk_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = ttk.Label(main_frame, text="Bulk Operations", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        # Currency operations
        currency_frame = ttk.LabelFrame(main_frame, text="💰 Currency", padding=20)
        currency_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(currency_frame, text="Max Out Money", command=lambda: self._set_currency("Money", 999999999),
                  width=30).pack(pady=5)
        ttk.Button(currency_frame, text="Max Out Skill Points", command=lambda: self._set_currency("SkillPoint", 99999),
                  width=30).pack(pady=5)
        ttk.Button(currency_frame, text="Max Out Master Points", command=lambda: self._set_currency("MasterPoint", 99999),
                  width=30).pack(pady=5)
        
        # Scrolls operations
        scrolls_frame = ttk.LabelFrame(main_frame, text="📜 Scrolls", padding=20)
        scrolls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(scrolls_frame, text="Unlock All Scrolls", command=self._unlock_scrolls,
                  width=30).pack(pady=5)
        ttk.Button(scrolls_frame, text="Max All Scrolls", command=self._max_scrolls,
                  width=30).pack(pady=5)
        
        # Progression
        prog_frame = ttk.LabelFrame(main_frame, text="📈 Progression", padding=20)
        prog_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(prog_frame, text="Max Experience", command=lambda: self._set_currency("Experience", 999999999),
                  width=30).pack(pady=5)
        
        # Info
        info_text = "⚠️  Bulk operations will modify multiple save values at once.\nMake sure to backup your save first!"
        ttk.Label(main_frame, text=info_text, foreground="red", font=("Arial", 10),
                 justify=tk.CENTER).pack(pady=30)
    
    def _setup_dlc_tab(self):
        """DLC Unlocker tab"""
        main_frame = ttk.Frame(self.dlc_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = ttk.Label(main_frame, text="DLC Unlocker (CreamInstaller)", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        info_text = """CreamInstaller Integration:
        
• Automatically detects your game installation
• Unlocks DLCs for Naruto to Boruto: Shinobi Striker
• Runs in safe proxy mode
• DLC files must be provided separately

Steps:
1. Download CreamInstaller from GitHub
2. Click "Run CreamInstaller" below
3. Configure for Shinobi Striker
4. Select DLCs to unlock"""
        
        ttk.Label(main_frame, text=info_text, font=("Arial", 10), justify=tk.LEFT).pack(pady=20)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)
        
        ttk.Button(button_frame, text="📥 Download CreamInstaller", command=self._download_cream,
                  width=35).pack(pady=10)
        ttk.Button(button_frame, text="▶️ Run CreamInstaller", command=self._run_cream,
                  width=35).pack(pady=10)
        
        warning = ttk.Label(main_frame, text="⚠️  Use at your own risk!", foreground="red",
                           font=("Arial", 11, "bold"))
        warning.pack(pady=20)
    
    # Force-Save methods
    def dump_save(self):
        """Dump game save"""
        messagebox.showinfo("Dump Save",
            "Make sure you're IN-GAME (not on title screen)!\n\n"
            "This will trigger the Lua mod to dump your save.\n"
            "Wait 1-2 seconds...")
        
        path = filedialog.asksaveasfilename(
            title="Save Dumped Save",
            defaultextension=".sav",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if path:
            self.current_save = path
            self.status_var.set(f"Save dumped: {Path(path).name}")
            messagebox.showinfo("Success", f"Saved to: {path}")
            self._refresh_editor_list()
    
    def upload_save(self):
        """Upload save to game"""
        path = filedialog.askopenfilename(
            title="Select Save to Upload",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if path:
            messagebox.showinfo("Upload Complete",
                "Next steps:\n"
                "1. Return to title screen\n"
                "2. Re-enter the game\n"
                "3. Your changes will be loaded")
    
    # Editor methods
    def load_save(self):
        """Load save file"""
        path = filedialog.askopenfilename(
            title="Open Save File",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if path:
            self.current_save = path
            self._parse_save_file(path)
            self._refresh_editor_list()
            self.status_var.set(f"Loaded: {Path(path).name}")
            messagebox.showinfo("Success", f"Loaded: {path}")
    
    def _parse_save_file(self, filepath: str):
        """Parse save file for IDs"""
        self.status_var.set("Parsing save file...")
        self.root.update()
        
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            text_data = data.decode('utf-8', errors='ignore')
            
            # Extract IDs with regex
            id_pattern = r'(ID_[A-Za-z_0-9]+)'
            ids = set(re.findall(id_pattern, text_data))
            
            self.save_data = {}
            for id_str in ids:
                self.save_data[id_str] = {
                    "value": 0,
                    "type": "flag" if "Flag" in id_str else "counter",
                    "category": self._categorize_id(id_str)
                }
            
            self.status_var.set(f"Parsed {len(self.save_data)} IDs from save")
        
        except Exception as e:
            self.status_var.set("Error parsing save")
            messagebox.showerror("Error", f"Failed to parse: {e}")
    
    def _categorize_id(self, id_str: str) -> str:
        """Categorize an ID"""
        if "Counter_Money" in id_str or "Counter_SkillPoint" in id_str or "Counter_MasterPoint" in id_str:
            return "Currency"
        elif "Scroll" in id_str:
            return "Scrolls"
        elif "Experience" in id_str or "PlayTime" in id_str:
            return "Progression"
        elif "PVP" in id_str or "Kill" in id_str:
            return "PVP"
        elif "Weapon" in id_str:
            return "Items"
        elif "NJT" in id_str:
            return "Items"
        elif "Custom" in id_str or "Jacket" in id_str:
            return "Customization"
        elif "Master" in id_str or "Naruto" in id_str or "Sasuke" in id_str:
            return "Mentors"
        else:
            return "Other"
    
    def _on_search_change(self, *args):
        """Handle search input"""
        self._refresh_editor_list()
    
    def _on_category_change(self, *args):
        """Handle category change"""
        self._refresh_editor_list()
    
    def _refresh_editor_list(self):
        """Refresh editor treeview"""
        for item in self.id_tree.get_children():
            self.id_tree.delete(item)
        
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        
        count = 0
        for id_name in sorted(self.save_data.keys()):
            id_data = self.save_data[id_name]
            
            # Filter by search
            if search_term and search_term not in id_name.lower():
                continue
            
            # Filter by category
            if category != "All" and id_data.get("category") != category:
                continue
            
            value = id_data.get("value", 0)
            id_type = id_data.get("type", "unknown")
            cat = id_data.get("category", "Other")
            
            self.id_tree.insert("", "end", values=(id_name, value, id_type, cat))
            count += 1
        
        self.count_var.set(f"Showing {count} IDs")
    
    def _edit_selected_value(self):
        """Edit selected value"""
        selection = self.id_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select an ID to edit")
            return
        
        item = selection[0]
        values = self.id_tree.item(item)['values']
        id_name = values[0]
        current_value = values[1]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit {id_name}")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"ID: {id_name}", font=("Arial", 10, "bold")).pack(pady=15)
        ttk.Label(dialog, text="New value:").pack(pady=5)
        
        value_var = tk.StringVar(value=str(current_value))
        value_entry = ttk.Entry(dialog, textvariable=value_var, width=20, font=("Arial", 12))
        value_entry.pack(pady=10)
        value_entry.focus()
        value_entry.select_range(0, tk.END)
        
        def apply():
            try:
                new_value = int(value_var.get())
                self.save_data[id_name]["value"] = new_value
                self._refresh_editor_list()
                dialog.destroy()
                messagebox.showinfo("Success", f"Updated {id_name} to {new_value}")
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="✓ Apply", command=apply, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✕ Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    # Bulk operations
    def _set_currency(self, currency_type: str, value: int):
        """Set currency value"""
        found = False
        for id_name in self.save_data:
            if currency_type in id_name:
                self.save_data[id_name]["value"] = value
                found = True
        
        if found:
            self._refresh_editor_list()
            messagebox.showinfo("Success", f"Set {currency_type} to {value}")
        else:
            messagebox.showwarning("Not Found", f"Could not find {currency_type} IDs")
    
    def _unlock_scrolls(self):
        """Unlock all scrolls"""
        for id_name in self.save_data:
            if "Scroll" in id_name:
                self.save_data[id_name]["value"] = 1
        
        self._refresh_editor_list()
        messagebox.showinfo("Success", "Unlocked all scrolls")
    
    def _max_scrolls(self):
        """Max out all scrolls"""
        for id_name in self.save_data:
            if "Scroll" in id_name:
                self.save_data[id_name]["value"] = 9999
        
        self._refresh_editor_list()
        messagebox.showinfo("Success", "Maxed out all scrolls")
    
    # Parse IDs
    def parse_save_ids_threaded(self):
        """Parse save IDs in background"""
        if not self.current_save:
            self.current_save = filedialog.askopenfilename(
                title="Select Save File",
                filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
            )
        
        if not self.current_save:
            return
        
        thread = Thread(target=self._parse_ids_background, daemon=True)
        thread.start()
    
    def _parse_ids_background(self):
        """Parse IDs in background"""
        self.status_var.set("Parsing IDs...")
        self.parsing = True
        self.root.update()
        
        try:
            subprocess.run([sys.executable, "ntbss_id_parser.py", self.current_save], 
                          capture_output=True, check=True, timeout=30)
            
            # Reload parsed IDs
            self._parse_save_file(self.current_save)
            self._refresh_editor_list()
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "IDs parsed successfully"))
            self.status_var.set("IDs parsed successfully")
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Parse failed: {e}"))
            self.status_var.set("Parse failed")
        
        finally:
            self.parsing = False
    
    # DLC/Cream
    def _download_cream(self):
        """Download CreamInstaller"""
        messagebox.showinfo("Download CreamInstaller",
            "Visit: https://github.com/FroggMaster/CreamInstaller/releases\n\n"
            "Download the latest CreamInstaller.exe")
    
    def _run_cream(self):
        """Run CreamInstaller"""
        try:
            subprocess.Popen("CreamInstaller.exe")
            self.status_var.set("CreamInstaller launched")
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch CreamInstaller:\n{e}")
    
    # Tools
    def find_game_dir(self):
        """Find game directory"""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                game_path = Path(steam_path) / "steamapps" / "common" / "Naruto To Boruto"
                
                if game_path.exists():
                    self.game_dir = str(game_path)
                    messagebox.showinfo("Found", f"Game directory:\n{game_path}")
                    return
        except:
            pass
        
        messagebox.showwarning("Not Found", "Game directory not found")
    
    def create_directories(self):
        """Create required directories"""
        try:
            Path("C:\\temp").mkdir(exist_ok=True)
            save_dir = Path.home() / "Saved Games" / "NARUTO TO BORUTO SHINOBI STRIKER"
            save_dir.mkdir(parents=True, exist_ok=True)
            messagebox.showinfo("Success", "Directories created")
            self.status_var.set("Directories created")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def save_changes(self):
        """Save changes (placeholder)"""
        if not self.current_save:
            messagebox.showwarning("Warning", "No save file loaded")
            return
        
        messagebox.showinfo("Info",
            "Changes will be applied when you upload the save to the game.\n\n"
            "Use the Force-Save tab to upload.")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About",
            "NTBSS Complete Suite v2\n\n"
            "Professional Save Editor for\n"
            "Naruto to Boruto: Shinobi Striker\n\n"
            "Features:\n"
            "• Force-Save (Dump/Upload)\n"
            "• Advanced Save Editor\n"
            "• Bulk Operations\n"
            "• DLC Unlocker (CreamInstaller)\n\n"
            "GitHub: https://github.com/nr8dn/NTBSS-Experiment\n\n"
            "⚠️  Always backup your saves!")


def main():
    """Main entry point"""
    if sys.platform != "win32":
        print("Error: This application requires Windows")
        sys.exit(1)
    
    root = tk.Tk()
    app = NTBSSEditorV2(root)
    root.mainloop()


if __name__ == "__main__":
    main()
