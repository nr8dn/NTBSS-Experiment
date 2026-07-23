#!/usr/bin/env python3
"""
NTBSS Asset ID Extractor
Scans game assets and save files to extract all available IDs for the Save Editor
"""

import os
import sys
import re
import json
import struct
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class AssetIDExtractor:
    """Extract IDs from game assets and save files"""
    
    def __init__(self, game_path: str = None, save_path: str = None):
        self.game_path = Path(game_path) if game_path else None
        self.save_path = Path(save_path) if save_path else None
        self.found_ids = defaultdict(set)
        self.id_database = defaultdict(lambda: {"description": "", "max": 0, "type": "unknown"})
    
    def find_game_directory(self) -> Path:
        """Auto-detect game directory"""
        common_paths = [
            Path("D:/steam/steamapps/common/Naruto To Boruto"),
            Path("C:/Program Files (x86)/Steam/steamapps/common/Naruto To Boruto"),
            Path("C:/Program Files/Steam/steamapps/common/Naruto To Boruto"),
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        # Try registry
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                game_path = Path(steam_path) / "steamapps" / "common" / "Naruto To Boruto"
                if game_path.exists():
                    return game_path
        except:
            pass
        
        return None
    
    def scan_save_file(self, save_path: Path) -> None:
        """Extract all IDs from a save file"""
        print(f"[*] Scanning save file: {save_path}")
        
        try:
            with open(save_path, 'rb') as f:
                data = f.read()
            
            # Decode as text (ignoring errors)
            text_data = data.decode('utf-8', errors='ignore')
            
            # Extract all ID patterns
            patterns = {
                'Counter': r'ID_Counter_(\w+)',
                'Flag': r'ID_Flag_(\w+)',
                'Weapon': r'ID_Weapon_(\w+)',
                'Ninjutsu': r'ID_NJT_(\w+)',
                'Reward': r'ID_Reward_(\w+)',
                'Skill': r'ID_Skill_(\w+)',
                'Custom': r'ID_Custom(\w+)',
                'Parts': r'ID_Parts(\w+)',
                'Voice': r'ID_Voice_(\w+)',
                'Palette': r'ID_Pallete_(\w+)',
                'Other': r'ID_(\w+)',
            }
            
            for category, pattern in patterns.items():
                matches = re.findall(pattern, text_data)
                for match in matches:
                    if category == 'Counter':
                        full_id = f"ID_Counter_{match}"
                    elif category == 'Other':
                        full_id = f"ID_{match}"
                    else:
                        full_id = f"ID_{category}_{match}"
                    
                    self.found_ids[category].add(full_id)
            
            print(f"[+] Found {sum(len(v) for v in self.found_ids.values())} unique IDs")
        
        except Exception as e:
            print(f"[-] Error reading save: {e}")
    
    def scan_asset_files(self, game_path: Path) -> None:
        """Scan game asset files for ID references"""
        print(f"[*] Scanning game assets in: {game_path}")
        
        # Common asset file patterns
        asset_extensions = ['.uasset', '.umap', '.json', '.txt', '.csv', '.ini', '.cfg']
        
        # Directories to scan
        scan_dirs = [
            game_path / "NARUTO" / "Content",
            game_path / "Content",
            game_path / "NARUTO" / "Config",
            game_path / "Config",
        ]
        
        total_files = 0
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            
            print(f"[*] Scanning {scan_dir}...")
            
            for file_path in scan_dir.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Check extension
                if file_path.suffix.lower() not in asset_extensions:
                    continue
                
                total_files += 1
                
                try:
                    # Try to read as text
                    with open(file_path, 'rb') as f:
                        data = f.read(1000000)  # Read first 1MB
                    
                    text_data = data.decode('utf-8', errors='ignore')
                    
                    # Extract IDs
                    id_pattern = r'ID_[A-Za-z_]+_?[A-Za-z0-9_]*'
                    matches = re.findall(id_pattern, text_data)
                    
                    for id_str in set(matches):
                        # Categorize by prefix
                        if id_str.startswith('ID_Counter_'):
                            self.found_ids['Counter'].add(id_str)
                        elif id_str.startswith('ID_Flag_'):
                            self.found_ids['Flag'].add(id_str)
                        elif 'Weapon' in id_str:
                            self.found_ids['Weapon'].add(id_str)
                        elif 'NJT' in id_str:
                            self.found_ids['Ninjutsu'].add(id_str)
                        elif 'Custom' in id_str:
                            self.found_ids['Customization'].add(id_str)
                        else:
                            self.found_ids['Other'].add(id_str)
                
                except Exception as e:
                    pass
        
        print(f"[+] Scanned {total_files} asset files")
    
    def extract_from_strings(self) -> None:
        """Extract hardcoded ID strings from compiled binaries"""
        print("[*] Extracting IDs from common game files...")
        
        # Add known IDs from game data
        known_ids = {
            'Counter': [
                'ID_Counter_Money',
                'ID_Counter_TotalMoney',
                'ID_Counter_SkillPoint',
                'ID_Counter_MasterPoint',
                'ID_Counter_PlayerExperience',
                'ID_Counter_PlayTimeMinute',
                'ID_Counter_Scroll_Plain',
                'ID_Counter_Scroll_Quality',
                'ID_Counter_Scroll_Valuable',
                'ID_Counter_Scroll_Esoteric',
                'ID_Counter_Play_PVP',
                'ID_Counter_Win_PVP',
                'ID_Counter_PVP_Kill',
            ],
            'Flag': [
                'ID_Flag_Acquisition_CustomJacket_ATK_001',
                'ID_Flag_Open_CustomJacket_ATK_001',
                'ID_Flag_Check_CustomJacket_ATK_001',
                'ID_Flag_Check_NJT_D01_001',
            ],
            'Mentor': [
                'ID_Counter_MasterPoint_Naruto',
                'ID_Counter_MasterRank_Naruto',
            ]
        }
        
        for category, ids in known_ids.items():
            self.found_ids[category].update(ids)
    
    def categorize_ids(self) -> Dict[str, List[str]]:
        """Categorize IDs by function"""
        categorized = {
            'Currency': [],
            'Scrolls': [],
            'Progression': [],
            'Story': [],
            'PVP': [],
            'Missions': [],
            'Mentors': [],
            'Weapons': [],
            'Ninjutsu': [],
            'Customization': [],
            'Flags': [],
            'Other': []
        }
        
        # Combine all found IDs
        all_ids = set()
        for category_ids in self.found_ids.values():
            all_ids.update(category_ids)
        
        # Categorize
        for id_str in sorted(all_ids):
            categorized_flag = False
            
            # Currency
            if any(kw in id_str for kw in ['Money', 'SkillPoint', 'MasterPoint']):
                categorized['Currency'].append(id_str)
                categorized_flag = True
            
            # Scrolls
            elif any(kw in id_str for kw in ['Scroll', 'CheckScroll']):
                categorized['Scrolls'].append(id_str)
                categorized_flag = True
            
            # Progression
            elif any(kw in id_str for kw in ['Experience', 'PlayTime', 'ExpBase', 'ExpScale']):
                categorized['Progression'].append(id_str)
                categorized_flag = True
            
            # Story
            elif any(kw in id_str for kw in ['Scenario', 'Lee', 'Boruto', 'Sarada', 'Ino', 'Choji', 'Sai', 'Shino', 'Hinata', 'Gaara', 'Mitsuki']):
                categorized['Story'].append(id_str)
                categorized_flag = True
            
            # PVP
            elif any(kw in id_str for kw in ['PVP', '_Kill', '_Dead', '_Play_']):
                categorized['PVP'].append(id_str)
                categorized_flag = True
            
            # Missions
            elif any(kw in id_str for kw in ['Mission', 'VRMission', 'Clear', '_Rank']):
                categorized['Missions'].append(id_str)
                categorized_flag = True
            
            # Mentors
            elif any(kw in id_str for kw in ['MasterPoint', 'MasterRank', 'Naruto', 'Sasuke', 'Sakura', 'Kakashi', 'Tsunade', 'Jiraiya', 'Orochimaru', 'Madara', 'Minato']):
                categorized['Mentors'].append(id_str)
                categorized_flag = True
            
            # Weapons
            elif 'Weapon' in id_str:
                categorized['Weapons'].append(id_str)
                categorized_flag = True
            
            # Ninjutsu
            elif 'NJT' in id_str:
                categorized['Ninjutsu'].append(id_str)
                categorized_flag = True
            
            # Customization
            elif any(kw in id_str for kw in ['Custom', 'Jacket', 'Pants', 'Accessory', 'FacePaint', 'Hair', 'Forehead', 'Avatar', 'Nickname', 'Voice', 'Pallete']):
                categorized['Customization'].append(id_str)
                categorized_flag = True
            
            # Flags
            elif 'Flag' in id_str:
                categorized['Flags'].append(id_str)
                categorized_flag = True
            
            # Other
            else:
                categorized['Other'].append(id_str)
        
        return categorized
    
    def export_results(self, output_dir: Path = None) -> None:
        """Export results to JSON and text files"""
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_dir.mkdir(exist_ok=True)
        
        categorized = self.categorize_ids()
        
        # Export JSON
        json_file = output_dir / "ntbss_ids.json"
        with open(json_file, 'w') as f:
            json.dump(categorized, f, indent=2)
        print(f"[+] Exported JSON: {json_file}")
        
        # Export formatted text
        txt_file = output_dir / "ntbss_ids.txt"
        with open(txt_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("NTBSS EXTRACTED ASSET IDs\n")
            f.write("=" * 80 + "\n\n")
            
            total_ids = 0
            for category, ids in categorized.items():
                if ids:
                    f.write(f"\n{category.upper()} ({len(ids)} IDs)\n")
                    f.write("-" * 80 + "\n")
                    for id_str in ids[:50]:  # Show first 50
                        f.write(f"  {id_str}\n")
                    if len(ids) > 50:
                        f.write(f"  ... and {len(ids) - 50} more\n")
                    total_ids += len(ids)
            
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"TOTAL UNIQUE IDs: {total_ids}\n")
            f.write("=" * 80 + "\n")
        
        print(f"[+] Exported text: {txt_file}")
        
        # Export CSV for spreadsheet
        csv_file = output_dir / "ntbss_ids.csv"
        with open(csv_file, 'w') as f:
            f.write("Category,ID Name,Type\n")
            for category, ids in categorized.items():
                for id_str in ids:
                    # Determine if it's a flag (1-byte) or counter (4-byte)
                    id_type = "Flag (1-byte)" if "Flag" in id_str else "Counter (4-byte)" if "Counter" in id_str else "Unknown"
                    f.write(f'"{category}","{id_str}","{id_type}"\n')
        
        print(f"[+] Exported CSV: {csv_file}")
        
        return categorized
    
    def run(self) -> Dict:
        """Run the full extraction"""
        print("\n" + "=" * 80)
        print("NTBSS ASSET ID EXTRACTOR")
        print("=" * 80 + "\n")
        
        # Find game directory if not provided
        if not self.game_path:
            print("[*] Finding game directory...")
            self.game_path = self.find_game_directory()
            if self.game_path:
                print(f"[+] Found game at: {self.game_path}")
            else:
                print("[-] Could not find game directory")
        
        # Extract known IDs
        self.extract_from_strings()
        
        # Scan save file if provided
        if self.save_path and self.save_path.exists():
            self.scan_save_file(self.save_path)
        
        # Scan game assets if available
        if self.game_path and self.game_path.exists():
            self.scan_asset_files(self.game_path)
        
        # Export results
        categorized = self.export_results()
        
        # Summary
        total = sum(len(ids) for ids in categorized.values())
        print(f"\n[+] Total unique IDs extracted: {total}")
        for category, ids in categorized.items():
            if ids:
                print(f"    {category}: {len(ids)}")
        
        print("\n[+] Ready to use with Save Editor!")
        return categorized


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract all available IDs from NTBSS assets and saves"
    )
    parser.add_argument('--game', type=str, help='Path to game directory')
    parser.add_argument('--save', type=str, help='Path to save file')
    parser.add_argument('--output', type=str, default='.', help='Output directory')
    
    args = parser.parse_args()
    
    extractor = AssetIDExtractor(
        game_path=args.game,
        save_path=args.save
    )
    
    try:
        extractor.run()
    except KeyboardInterrupt:
        print("\n\n[!] Extraction cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
