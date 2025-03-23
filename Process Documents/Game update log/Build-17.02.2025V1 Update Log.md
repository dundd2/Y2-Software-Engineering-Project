# Property Tycoon - Build-17.02.2025V1 Update Log

## Changes

* **UI Overhaul:**
  * Added enhanced visual feedback for button interactions, including hover effects and active states.
  * Implemented custom, modern-looking buttons and input fields.
  * Updated all fonts
  * Game logo now added
  * New Starter Background
  * Dice now displayed in a new UI
  * New Buttons design

* **Responsive Design:**
  * The UI now dynamically adjusts to window resizing.

* **Improved Text Handling:**
  * Implemented a `TextScaler` class to dynamically adjust font sizes based on screen resolution.

* **Enhanced Player Representation:**
  * Added customizable player tokens with fallback options, ensuring each player is visually distinct on the game board.
  * Players now feature a subtle animation, making the game board feel more alive.

* **Advanced Game Logic:**
  * New auction mechanics, adding a new layer of strategic depth to property acquisition.
  * Implemented a message queue system for displaying game events.

* **Camera:**
  * Add camera control, player could zoom in/out, and move the board on the screen.(Based on owen's idea)

### Bug Fixes

* Fixed an issue where player images were not correctly displayed on the game board.
* Fixed an issue where text overlap in the game UI

### Code Improvements

* **Refactoring and Modularization:**
  * Created separate classes for different UI elements (e.g., `ModernButton`, `ModernInput`, `BasePage`, and specialized page classes)
  * Moved game logic into its own class (`GameLogic`)
  * Removed redundant code from `Game.py` to the appropriate files.
  * Removed unused variables.

* **Error Handling:**
  * Added error handling for missing assets (images) to provide fallback options and prevent crashes.

* **Foundation for AI Players:** This is the last version of the game without AI player functionality.  The development team is actively working on implementing "Easy" difficulty AI players, based on the flowchart provided by Eric.
* `ai_player_logic.py` has been created as the starting point for the AI logic.
