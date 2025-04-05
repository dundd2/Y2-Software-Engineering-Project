# Property Tycoon - Alpha Build- 25.03.2025 Update Log

## Changes

### Bug Fixes

- Fixed Owen's test code path bug 
- Fixed issue where player tokens were not displayed correctly when moving to a space
- Fixed dice roll issue for switching to the next player
- Fixed Board.png pixelation issue 
- Fixed font bug and UI fade-in/out issues
- Fixed asset valuation display (including hotel values)

---

### Improvements

- Added new test code
- Added University of Sussex font: *Libre Baskerville Bold 700*
- Added bankruptcy handling to end the game
- Added Credits Page (based on Owen’s idea)
- Added Easter egg in UI
- Improved UI layout and animations
- Combined `FontManager` and `TextScaler` into a single file
- Font changes now apply to the full game, not just the start page
- Added ownership markers
- Added rent paid UI
- Added 6-player tokens
- Improved background, message box, and temporary pixel UI
- Improved command-line output display
- Added tax payment popup UI
- Updated board image for quality and size
- UI updates: font adjustments and general layout

---

### File Maintenance

- Deleted duplicated "game message "
- Reverted deletion of "game message" due to a new bug; also changed board size
- Formatting updates in README and source code using Black formatter
- Removed unnecessary console output
- Changed test code names
- Renamed multiple files for consistency:
  - `cards.py` → `Cards.py`
  - `ai_player_logic.py` → `Ai_Player_Logic.py`
  - `main.py` → `Main.py`
  - `game_logic.py` → `Game_Logic.py`
  - `ui.py` → `UI.py`
  - `loadexcel.py` → `Loadexcel.py`

---

### Documentation

- Updated system-level testing documents
- Added YouTube channel details
- Deleted PERT sheet with invalid filename (Windows does not allow colons)
- Added 2 more edge-case test scenarios

---

###  Known New Bugs

- Minor issues remain in the bidding logic
- Some rent board data updates still under testing