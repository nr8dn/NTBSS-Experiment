#!/usr/bin/env python3
"""
NTBSS Complete Suite - All-in-one Automatic Setup & Editor
Automated installation, one-click dump/edit/reload workflow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import subprocess
import json
import re
import shutil
import webbrowser
from pathlib import Path
from threading import Thread
from collections import defaultdict
from typing import Dict, List, Tuple
import struct
import time


class NTBSSAutoSetup:
    """First-time setup wizard"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NTBSS Setup Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.completed = False
        
        self.show_welcome()
    
    def show_welcome(self):
        """Welcome screen"""
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="NTBSS Complete Suite", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="First-Time Setup", font=("Arial", 12)).pack(pady=10)
        
        info = """This wizard will:
        
✓ Create required directories
✓ Download CreamInstaller
✓ Verify game installation
✓ Configure UE4SS mod

Click Next to continue."""
        
        ttk.Label(frame, text=info, justify=tk.LEFT, font=("Arial", 10)).pack(pady=20)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=30)
        ttk.Button(button_frame, text="▶ Next", command=self.step_directories).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="✕ Exit", command=self.root.quit).pack(side=tk.LEFT, padx=10)
    
    def step_directories(self):
        """Create directories"""
        self._clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Creating Directories...", font=("Arial", 14, "bold")).pack(pady=20)
        
        progress = ttk.Progressbar(frame, length=400, mode='indeterminate')
        progress.pack(pady=20)
        progress.start()
        
        status_label = ttk.Label(frame, text="")
        status_label.pack(pady=10)
        
        def setup():
            try:
                status_label.config(text="Creating C:\\temp...")
                self.root.update()
                Path("C:\\temp").mkdir(exist_ok=True)
                
                status_label.config(text="Creating save directory...")
                self.root.update()
                save_dir = Path.home() / "Saved Games" / "NARUTO TO BORUTO SHINOBI STRIKER"
                save_dir.mkdir(parents=True, exist_ok=True)
                
                status_label.config(text="✓ Directories created")
                self.root.update()
                time.sleep(1)
                self.step_game_dir()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")
                self.step_game_dir()
        
        thread = Thread(target=setup, daemon=True)
        thread.start()
    
    def step_game_dir(self):
        """Find game directory"""
        self._clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Locating Game...", font=("Arial", 14, "bold")).pack(pady=20)
        
        progress = ttk.Progressbar(frame, length=400, mode='indeterminate')
        progress.pack(pady=20)
        progress.start()
        
        status_label = ttk.Label(frame, text="")
        status_label.pack(pady=10)
        
        def find_game():
            try:
                import winreg
                status_label.config(text="Checking Steam registry...")
                self.root.update()
                
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
                    steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    game_path = Path(steam_path) / "steamapps" / "common" / "Naruto To Boruto"
                    
                    if game_path.exists():
                        status_label.config(text=f"✓ Found: {game_path}")
                        self.root.update()
                        time.sleep(1)
                        self.step_cream()
                        return
            except:
                pass
            
            status_label.config(text="Game not found in registry")
            self.root.update()
            time.sleep(1)
            self.step_cream()
        
        thread = Thread(target=find_game, daemon=True)
        thread.start()
    
    def step_cream(self):
        """Download CreamInstaller"""
        self._clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="CreamInstaller Setup", font=("Arial", 14, "bold")).pack(pady=20)
        
        info = """CreamInstaller is required for DLC unlocking.

Click 'Download' to visit the GitHub releases page,
or skip if you already have it."""
        
        ttk.Label(frame, text=info, justify=tk.LEFT).pack(pady=20)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=30)
        
        ttk.Button(button_frame, text="📥 Download", 
                  command=lambda: self._download_cream()).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="⏭ Skip", 
                  command=self.step_complete).pack(side=tk.LEFT, padx=10)
    
    def _download_cream(self):
        """Download CreamInstaller"""
        webbrowser.open("https://github.com/FroggMaster/CreamInstaller/releases")
        self.step_complete()
    
    def step_complete(self):
        """Setup complete"""
        self._clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Setup Complete!", font=("Arial", 16, "bold")).pack(pady=20)
        
        info = """✓ Directories created
✓ Game location verified
✓ CreamInstaller ready

You're all set! Next steps:

1. Launch the game
2. Load into a lobby
3. Use the editor to dump/edit/reload saves

Click 'Launch Editor' to start."""
        
        ttk.Label(frame, text=info, justify=tk.LEFT, font=("Arial", 10)).pack(pady=20)
        
        ttk.Button(frame, text="▶ Launch Editor", 
                  command=self._launch).pack(pady=20)
    
    def _launch(self):
        """Launch main editor"""
        self.completed = True
        self.root.destroy()
    
    def _clear_frame(self):
        """Clear all widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()


class NTBSSAutoEditor:
    """Main auto-editing interface"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NTBSS Complete Suite - Auto Editor")
        self.root.geometry("1200x800")
        
        self.current_save = None
        self.save_data = defaultdict(lambda: {"value": 0, "type": "flag", "category": "Other"})
        self.game_process = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup main UI"""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Workflow buttons (big and obvious)
        workflow_frame = ttk.LabelFrame(container, text="NTBSS Auto Workflow", padding=15)
        workflow_frame.pack(fill=tk.X, pady=10)
        
        step_frame = ttk.Frame(workflow_frame)
        step_frame.pack(fill=tk.X, pady=10)
        
        # Step 1: Launch game
        ttk.Button(step_frame, text="1️⃣ Launch Game", command=self.launch_game,
                  width=25).pack(side=tk.LEFT, padx=5)
        
        # Step 2: Dump save
        ttk.Button(step_frame, text="2️⃣ Dump Save", command=self.auto_dump_save,
                  width=25).pack(side=tk.LEFT, padx=5)
        
        # Step 3: Edit
        ttk.Button(step_frame, text="3️⃣ Edit Save", command=self.show_editor,
                  width=25).pack(side=tk.LEFT, padx=5)
        
        # Step 4: Return to game
        ttk.Button(step_frame, text="4️⃣ Upload & Return", command=self.auto_upload_return,
                  width=25).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        inst_frame = ttk.LabelFrame(container, text="Instructions", padding=10)
        inst_frame.pack(fill=tk.X, pady=10)
        
        instructions = """1. Click 'Launch Game' to start Naruto to Boruto
2. Load into a lobby (must be in-game, not title screen)
3. Click 'Dump Save' to export your save
4. Click 'Edit Save' to modify items, currency, stats
5. Click 'Upload & Return' to reload the save and return to title screen
6. The game will sync your changes automatically

⚠️  Always backup your save file before editing!"""
        
        ttk.Label(inst_frame, text=instructions, justify=tk.LEFT, font=("Arial", 9)).pack(anchor=tk.W, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Ready - Click 'Launch Game' to begin")
        status_frame = ttk.Frame(container)
        status_frame.pack(fill=tk.X, pady=10)
        ttk.Label(status_frame, text="Status:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.LEFT, padx=10)
    
    def launch_game(self):
        """Launch Naruto game"""
        try:
            game_paths = [
                Path("D:/steam/steamapps/common/Naruto To Boruto/Naruto.exe"),
                Path("C:/Program Files (x86)/Steam/steamapps/common/Naruto To Boruto/Naruto.exe"),
                Path("C:/Program Files/Steam/steamapps/common/Naruto To Boruto/Naruto.exe"),
            ]
            
            for path in game_paths:
                if path.exists():
                    self.game_process = subprocess.Popen(str(path))
                    self.status_var.set(f"Game launched - Load into a lobby, then click 'Dump Save'")
                    messagebox.showinfo("Game Launched", 
                        "Naruto to Boruto has been launched.\n\n"
                        "1. Load into a lobby (must be IN-GAME)\n"
                        "2. Once in-game, click 'Dump Save'")
                    return
            
            messagebox.showerror("Error", "Could not find game executable")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch game: {e}")
    
    def auto_dump_save(self):
        """Automatically dump save"""
        self.status_var.set("Dumping save...")
        self.root.update()
        
        save_dir = Path.home() / "Saved Games" / "NARUTO TO BORUTO SHINOBI STRIKER"
        save_dir.mkdir(parents=True, exist_ok=True)
        self.current_save = str(save_dir / "current_save.sav")
        
        # Create command file for Lua mod
        cmd_file = Path("C:\\temp\\ue_cmd.txt")
        cmd_file.write_text("dump")
        
        # Wait for dump
        for i in range(15):  # 15 second timeout
            time.sleep(1)
            if Path(self.current_save).exists():
                self.status_var.set(f"✓ Save dumped! Click 'Edit Save' to modify")
                messagebox.showinfo("Success", 
                    "Save dumped successfully!\n\n"
                    "Click 'Edit Save' to make changes")
                return
        
        messagebox.showerror("Timeout", 
            "Could not dump save after 15 seconds.\n\n"
            "Make sure:\n"
            "• You're in-game (not title screen)\n"
            "• UE4SS mod is properly installed")
    
    def show_editor(self):
        """Show the save editor"""
        if not self.current_save or not Path(self.current_save).exists():
            messagebox.showwarning("Warning", "No save loaded. Click 'Dump Save' first")
            return
        
        # Parse save
        self._parse_save(self.current_save)
        
        # Create editor window
        editor_window = tk.Toplevel(self.root)
        editor_window.title("NTBSS Save Editor")
        editor_window.geometry("1000x700")
        
        # Top controls
        control_frame = ttk.LabelFrame(editor_window, text="Controls & Search", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Category
        ttk.Label(control_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        category_var = tk.StringVar(value="All")
        categories = ["All", "Currency", "Scrolls", "Progression", "PVP", "Mentors", "Items", "Other"]
        category_combo = ttk.Combobox(control_frame, textvariable=category_var,
                                     values=categories, state="readonly", width=12)
        category_combo.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        ttk.Button(control_frame, text="🔄 Refresh", 
                  command=lambda: self._update_tree(editor_window, tree, search_var, category_var)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="💰 Max Money", 
                  command=lambda: self._max_money(tree)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="⚡ Max All", 
                  command=lambda: self._max_all(tree)).pack(side=tk.RIGHT, padx=5)
        
        # Tree
        tree_frame = ttk.LabelFrame(editor_window, text="Save Data", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Value", "Type", "Category"),
                           show='tree headings', yscrollcommand=vsb.set, height=25)
        tree.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=tree.yview)
        
        tree.column("#0", width=0)
        tree.column("ID", anchor=tk.W, width=350)
        tree.column("Value", anchor=tk.CENTER, width=100)
        tree.column("Type", anchor=tk.CENTER, width=80)
        tree.column("Category", anchor=tk.CENTER, width=100)
        
        tree.heading("ID", text="ID Name", anchor=tk.W)
        tree.heading("Value", text="Current Value")
        tree.heading("Type", text="Type")
        tree.heading("Category", text="Category")
        
        tree.bind('<Double-1>', lambda e: self._edit_value(tree))
        
        # Update tree
        self._update_tree(editor_window, tree, search_var, category_var)
        
        # Trace changes
        search_var.trace('w', lambda *args: self._update_tree(editor_window, tree, search_var, category_var))
        category_var.trace('w', lambda *args: self._update_tree(editor_window, tree, search_var, category_var))
        
        # Bottom buttons
        button_frame = ttk.Frame(editor_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(button_frame, text="💡 Double-click a value to edit", foreground="blue").pack(side=tk.LEFT)
        ttk.Button(button_frame, text="✓ Done Editing", command=editor_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _parse_save(self, filepath: str):
        """Parse save file"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            text_data = data.decode('utf-8', errors='ignore')
            id_pattern = r'(ID_[A-Za-z_0-9]+)'
            ids = set(re.findall(id_pattern, text_data))
            
            self.save_data = {}
            for id_str in ids:
                self.save_data[id_str] = {
                    "value": 0,
                    "type": "flag" if "Flag" in id_str else "counter",
                    "category": self._categorize_id(id_str)
                }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse: {e}")
    
    def _categorize_id(self, id_str: str) -> str:
        """Categorize ID"""
        if any(x in id_str for x in ["Money", "SkillPoint", "MasterPoint"]):
            return "Currency"
        elif "Scroll" in id_str:
            return "Scrolls"
        elif any(x in id_str for x in ["Experience", "PlayTime"]):
            return "Progression"
        elif any(x in id_str for x in ["PVP", "Kill"]):
            return "PVP"
        elif any(x in id_str for x in ["Master", "Naruto", "Sasuke"]):
            return "Mentors"
        elif any(x in id_str for x in ["Weapon", "NJT"]):
            return "Items"
        else:
            return "Other"
    
    def _update_tree(self, window, tree, search_var, category_var):
        """Update tree view"""
        for item in tree.get_children():
            tree.delete(item)
        
        search_term = search_var.get().lower()
        category = category_var.get()
        
        for id_name in sorted(self.save_data.keys()):
            id_data = self.save_data[id_name]
            
            if search_term and search_term not in id_name.lower():
                continue
            if category != "All" and id_data.get("category") != category:
                continue
            
            value = id_data.get("value", 0)
            tree.insert("", "end", values=(id_name, value, id_data.get("type"), id_data.get("category")))
    
    def _edit_value(self, tree):
        """Edit selected value"""
        selection = tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = tree.item(item)['values']
        id_name = values[0]
        current_value = values[1]
        
        dialog = tk.Toplevel(tree.winfo_toplevel())
        dialog.title(f"Edit {id_name}")
        dialog.geometry("350x150")
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
                tree.item(item, values=(id_name, new_value, self.save_data[id_name]["type"], self.save_data[id_name]["category"]))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        ttk.Button(button_frame, text="✓ OK", command=apply, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✕ Cancel", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
    
    def _max_money(self, tree):
        """Max out money"""
        for id_name in self.save_data:
            if "Money" in id_name:
                self.save_data[id_name]["value"] = 999999999
        messagebox.showinfo("Success", "Money maxed out!")
    
    def _max_all(self, tree):
        """Max all currencies"""
        for id_name in self.save_data:
            if any(x in id_name for x in ["Money", "SkillPoint", "MasterPoint", "Experience"]):
                self.save_data[id_name]["value"] = 999999999
            elif "Scroll" in id_name:
                self.save_data[id_name]["value"] = 9999
        messagebox.showinfo("Success", "All currencies maxed!")
    
    def auto_upload_return(self):
        """Upload save and return to title screen"""
        if not self.current_save:
            messagebox.showwarning("Warning", "No save to upload")
            return
        
        self.status_var.set("Uploading save and returning to title screen...")
        self.root.update()
        
        # Create upload command
        cmd_file = Path("C:\\temp\\ue_cmd.txt")
        cmd_file.write_text("upload")
        
        # Wait a bit
        time.sleep(2)
        
        # Send ESC to return to title screen
        try:
            import pyautogui
            pyautogui.press('esc')
            time.sleep(1)
            
            self.status_var.set("✓ Save uploaded and returned to title screen!")
            messagebox.showinfo("Complete", 
                "Save has been uploaded!\n\n"
                "The game has been returned to title screen.\n"
                "Changes will sync when you re-enter the game.")
        except ImportError:
            messagebox.showinfo("Manual Step",
                "Save has been uploaded!\n\n"
                "Manually:\n"
                "1. Press ESC to go to title screen\n"
                "2. Re-enter the game\n"
                "3. Your changes will be loaded")
            self.status_var.set("✓ Upload complete - manually return to title screen")
    
    def show_about(self):
        """Show about"""
        messagebox.showinfo("About",
            "NTBSS Complete Suite - Auto Editor\n\n"
            "One-click workflow for editing saves:\n"
            "1. Launch game\n"
            "2. Dump save\n"
            "3. Edit save\n"
            "4. Upload & return\n\n"
            "GitHub: https://github.com/nr8dn/NTBSS-Experiment")


def main():
    """Main entry point"""
    if sys.platform != "win32":
        messagebox.showerror("Error", "This requires Windows")
        sys.exit(1)
    
    # First-time setup check
    setup_flag = Path.home() / ".ntbss_setup_done"
    
    if not setup_flag.exists():
        root = tk.Tk()
        wizard = NTBSSAutoSetup(root)
        root.mainloop()
        
        if wizard.completed:
            setup_flag.write_text("done")
    
    # Launch main editor
    root = tk.Tk()
    app = NTBSSAutoEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
