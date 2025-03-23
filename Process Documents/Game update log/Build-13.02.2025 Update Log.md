# Property Tycoon - Build-13.02.2025 Update Log

## Changes

- **Dynamic UI Scaling:**
  - user interface now dynamically adapts to different window sizes.

- **Complete UI Redesign:**
- Improved the ui ,but it is still a demo ,we will update and redo it onece the coder team get the ui design

- **New Game Menu System:**
    **Main Menu:** Provides options to Start Game, access How to Play instructions, and adjust Settings.

    **Start Page:** Allows the user to configure the number of human and AI players, and enter names for human players.  Includes validation to ensure valid player names are entered.

    **Game Mode Page:**

    **Settings Page:** Allows the user to change the screen resolution

     **How to Play Page:**

    **End Game Page:**

- **Game Mode Selection:**
  - Added the ability to choose between "Full Game" and "Abridged Game"

- **Time Limit (Abridged Mode):**
  - Implemented a configurable time limit for the Abridged Game mode, with options for 10, 20, and 30 minutes.  Includes a visual progress bar and warnings as the time limit approaches.

- **AI Players:**
  - Added support for AI players, configurable on the Start Page.The AI players' names are automatically generated (e.g., AI-1, AI-2).

- **Player Avatars/Tokens:**
  - Changed the Player Token form emoji to Playerlogo photos
  - Replaced emoji player tokens with custom images.  These are loaded from the assets/image directory and fallback to a numbered circle if the image file is missing.  The player images now animate (slight vertical movement).

- **Property Tooltips:**
  - Added tooltips that appear when hovering over a player's owned properties in the side panel, displaying the property name, price, and rent.

- **End Game Screen:**
  - Created an End Game page that displays the winner, final assets (for Abridged mode), bankrupted players, and players who voluntarily exited.  Includes options to play again or quit.

- **Voluntary Exit (Full Game Mode):**
  - Added the ability for players to voluntarily exit the game in Full Game mode (via the ESC key).  This removes the player and resets their owned properties.

- **Bankruptcy Handling:**
  - Improved bankruptcy handling.  When a player goes bankrupt, they are removed from the game, their properties are reset, and they are added to a list of bankrupted players.

- **Message System:**
  - Refactored the message display system to show messages in a dedicated panel.

- **Game Logic Updates:**
  - The `GameLogic` class now tracks bankrupted players and players who have voluntarily exited.

### Minor Changes and Bug Fixes

- **Code Refactoring:**
  - Moved UI-related code out of `Game.py` and `Board.py` into separate UI classes.
  - Created base classes for UI elements (e.g., `ModernButton`, `ModernInput`, `BasePage`) to promote code reuse and consistency.

- **Input Handling:**
  - Improved input handling in the menu screens, including keyboard navigation and text input validation.

- **Data Loading:**
  - Added more robust error handling to the property data loading (`loadexcel.py`).  Ensures that properties are only loaded if their position is a valid number.  Handles stations and utilities correctly.
  - Added descriptive print statements to `loadexcel.py` to show loading progress and any errors encountered.

- **GitHub Actions Workflow:**
  - Added a GitHub Actions workflow (`build.yml`) to automatically build executables for Windows and macOS when a new tag with the prefix `Build-` is pushed.

- **Version Information:**
  - Added a build version display to the main menu.

- **Playerlogo.png**:
  - fixed player token image bug, now can show the logo at board

### To Do

- **Property Management:**
  - Implementing buying and selling houses/hotels

- **AI Logic:**
  - The AI players currently do not have any decision-making logic
