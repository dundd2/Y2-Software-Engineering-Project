# Property Tycoon - Beta Build-06.04.2025 Update Log

## Changes

### Bug Fixes


- Fixed Linux build error
- Fixed various Python syntax errors and undefined names 
- Fixed GitHub Actions workflow errors
- Fixed "deep blue" UI issue in bankruptcy screen
- Fixed unit tests after `game.py` was split
- Added bankrupt/exit check before checking for "Pass Go"
- Fixed bug related to development mode for human players (Redo)

---

### New Features

- Added sound and music
- Added keyboard support and Keyboard Shortcuts Page
- Added development mode property stars
- Added zoom in/out tips page
-  abridged mode UI improvements
- Improved AI difficulty for hard AImode
- Improved bankruptcy UI
- Improved general UI appearance
- Changed `GROUP_COLORS` for better distinction
- Improved flashing stars display timing
- Uploaded 3-hour gameplay test log
- Improved unit tests

---

### Structural

- Split `game.py` into multiple files
- Split `DevelopmentMode.py`
- Improved folder structure 
- Edited workflow files to align with new structure
- Moved `requirements.txt` 
- Improved test folder organization
- Improved GitHub Actions:
  - Added `.DEB` Linux release for Chromebook
  - Updated `Build,ReleaseGame(pyinstaller).yml`
  - Added `python-package.yml`
- Added code comments in some file
---

### Documentation

- Reworked and improved Design Documents
- Uploaded code scanning results
- Uploaded flake8 code scan log
- Updated `README.md`
