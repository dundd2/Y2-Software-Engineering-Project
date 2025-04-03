# Property Tycoon - Build-09.02.2025 Update Log

## Changes

1. **Dynamic Property Loading (from Excel):**

   * The game now loads property data (names, prices, rents, groups, etc.) from an external Excel file (`PropertyTycoonBoardData.xlsx`). This replaces the hardcoded property definitions in the Board class. The card (Pot Luck and Opportunity Knocks) data is read from `PropertyTycoonCardData.xlsx`.

2. **Refactored Game Board and UI:**

   * The board drawing and player representation have been significantly improved for visual appeal and clarity. Many UI elements that were previously in Game.py have been moved/integrated into Board.py and other sections for better organization. The window size is increased, and the overall visual style is modernized.

3. **Enhanced Game Logic:**

   Based on Eric's provided game flow flowchart image:

   * The game logic has been moved to a separate GameLogic class, and the turn-handling, property buying, and rent payment logic have been refined and expanded. The `Game` class now relies on `GameLogic`.

   * **Details:**
     * **`GameLogic` Class:** Handles all core game logic, including player turns, dice rolls, property management, rent calculations, card draws, jail mechanics, and determining the game winner.
     * **Turn-Based Logic:** The `play_turn()` method in `GameLogic` now manages the entire turn sequence, including handling jail, doubles, and moving the player.
     * **Rent Calculation:** Rent calculation is now dynamic and depends on the property type (regular, station, utility) and the number of properties owned by the same player. This logic is now in the `Property` class.
     * **Card Actions:** Pot Luck and Opportunity Knocks card actions are now handled by lambda functions within the card data (loaded from the Excel file). This makes it easy to define new card effects.
     * Jail mechanics are implemented, including the ability to get out of jail by rolling doubles or paying a fine.
     * A simple auction system added to the game.
     * A bankrupt system added.
     * **Message Queue:** `GameLogic` uses a message queue to store messages that need to be displayed to the player.
