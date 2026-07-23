# NTBSS Complete Suite - Auto Editor

Professional all-in-one save editor and DLC unlocker for **Naruto to Boruto: Shinobi Striker**

## 🎯 Features

✅ **Automatic Setup Wizard** - First-time installation handles everything
✅ **One-Click Save Dump/Edit/Reload** - Seamless in-game editing workflow  
✅ **Advanced Save Editor** - Edit currency, items, stats, mentors with live preview
✅ **Bulk Operations** - Max money, unlock scrolls, max experience in one click
✅ **DLC Unlocker** - Integrated CreamInstaller for DLC management
✅ **Auto Return to Title Screen** - No manual navigation needed

## 📋 Requirements

- **Windows 10/11** (64-bit)
- **Naruto to Boruto: Shinobi Striker** (Steam)
- **UE4SS Mod** (Lua scripting support)
- **Python 3.8+** (if running from source)

## 🚀 Quick Start

### First Time Setup

1. **Download** the latest EXE from [Releases](https://github.com/nr8dn/NTBSS-Experiment/releases)
2. **Run** `NTBSS-Complete-Suite.exe`
3. **Follow the setup wizard** - it will:
   - Create required directories
   - Verify your game installation
   - Download CreamInstaller
   - Configure UE4SS

### Using the Editor

Once setup is complete, the workflow is simple:

```
1️⃣  Launch Game
   ↓
2️⃣  Dump Save (exports your current save)
   ↓
3️⃣  Edit Save (double-click any value to modify)
   ↓
4️⃣  Upload & Return (auto-reloads save, returns to title screen)
```

## 🎮 How It Works

### Auto Workflow

1. **Launch Game** - Starts Naruto to Boruto via Steam
2. **Dump Save** - Communicates with UE4SS mod to export your save to disk
3. **Edit Save** - Open the built-in editor to modify IDs:
   - Currency (Money, Skill Points, Master Points)
   - Scrolls (unlock/max)
   - Progression (Experience, playtime)
   - Mentors (rankings)
   - Customization items
   - PVP stats
4. **Upload & Return** - Re-uploads modified save and returns you to title screen automatically

### Bulk Operations

From the "Bulk Operations" tab:
- **Max Money** - Set currency to maximum
- **Max All Scrolls** - Unlock and max all scroll types
- **Max Experience** - Set XP to maximum
- All changes apply instantly

## 📝 Editing Your Save

### Double-Click to Edit

1. Open the save editor after dumping
2. Search for any ID using the search box
3. Filter by category (Currency, Items, etc.)
4. **Double-click the value** to edit
5. Enter new value and click OK

### Categories

- **💰 Currency** - Money, Skill Points, Master Points
- **📜 Scrolls** - All scroll types
- **📈 Progression** - Experience, playtime stats
- **⚡ PVP** - Battle wins, kills, deaths
- **👥 Mentors** - Master point rankings
- **🎨 Customization** - Clothes, hairstyles, accessories
- **🗡️ Items** - Weapons, ninjutsu

## 🔧 Manual Installation (If Building from Source)

```bash
# Clone the repo
git clone https://github.com/nr8dn/NTBSS-Experiment.git
cd NTBSS-Experiment

# Install dependencies
pip install pyinstaller

# Build the EXE
pyinstaller ntbss_complete_suite.py --onefile --windowed --name "NTBSS-Complete-Suite"

# Run
dist/NTBSS-Complete-Suite.exe
```

## 🛠️ Technical Details

### File Structure

```
ntbss_complete_suite.py          # Main auto-setup & editor
ntbss_asset_id_extractor.py      # Extract IDs from game assets
ntbss_id_parser.py               # Parse IDs from save files
gui.py                           # Legacy GUI (deprecated)
setup.py                         # Legacy setup (deprecated)
.github/workflows/build_exe.yml  # GitHub Actions build
```

### UE4SS Integration

The suite communicates with UE4SS via command files:
- `C:\temp\ue_cmd.txt` - Command file (dump/upload)
- Save file location: `%USERPROFILE%\Saved Games\NARUTO TO BORUTO SHINOBI STRIKER\`

### Save Format

- **GVAS Format** - Unreal Engine save format
- IDs follow pattern: `ID_Category_Name`
- Examples: `ID_Counter_Money`, `ID_Counter_SkillPoint`, `ID_Flag_*`

## ⚠️ Important Notes

### Backup Your Saves!

Always backup your save file before editing:
```
%USERPROFILE%\Saved Games\NARUTO TO BORUTO SHINOBI STRIKER\
```

### Game State

- You **MUST** be IN-GAME (not on title screen) when dumping
- Solo lobby recommended for safety
- Changes sync automatically when re-entering the game

### Online Safety

- **Edits may be detected by anti-cheat in online matches**
- Use edited saves in **offline modes only**
- Restore original save for online play

## 🔗 Related Projects

- **UE4SS** - Unreal Engine 4 Scripting System
  https://github.com/UE4SS-RE/RE-UE4SS

- **CreamInstaller** - DLC unlocker
  https://github.com/FroggMaster/CreamInstaller

- **Original Force-Save** - Base tool this builds on
  https://github.com/alfizari/NTBSS-Force-Save

## 📄 License

Use at your own risk. This tool is for personal use only.

## 🐛 Troubleshooting

### "Could not find game executable"

Game not installed in standard locations. Manually navigate to Steam folder:
```
C:\Program Files (x86)\Steam\steamapps\common\Naruto To Boruto\
```

### "Could not dump save after 15 seconds"

- Make sure you're **IN-GAME** (not title screen)
- Verify UE4SS is properly installed
- Check `C:\temp\ue_cmd.txt` was created

### Save not loading after upload

- Manually press **ESC** to go to title screen
- Re-enter the game (this triggers sync)
- Changes should now be loaded

### Changes not appearing in-game

- Make sure the dump completed (step 2)
- Make sure edits were saved (you should see confirmation)
- Return to title screen and re-enter game

## 💬 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing issues first

## 🎮 Gameplay Tips

### Recommended Edits

1. **First Playthrough** - Max scrolls to learn all jutsu types
2. **Mentor Grinding** - Edit master points to skip grinding
3. **Item Collection** - Unlock all customization items
4. **Challenge Runs** - Edit stats for custom difficulty

### What NOT to Edit

- ⚠️ Online rank/wins (will be detected)
- ⚠️ Character base stats excessively
- ⚠️ Anything that breaks game logic

## Credits

Built on:
- Original Force-Save concept by Alfizari
- UE4SS for Lua modding
- CreamInstaller for DLC support
- Community ID databases

---

**Last Updated**: July 2026  
**Version**: 2.0  
**Status**: Active Development
