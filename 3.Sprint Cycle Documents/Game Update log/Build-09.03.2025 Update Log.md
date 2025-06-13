# Property Tycoon - Build-09.03.2025 Update Log

## Changes

- A notification will now appear when the time limit is reached.
-The game will continue running until all players have completed the same number of turns.  
-Added clear visual indicators to show when the game is in the "finishing round" state.  
-The game will only end once all players have had an equal number of turns.  

- The final assets of all players, including those who voluntarily exited the game, will now be correctly displayed.  

### **Bug Fixes**  

- The `handle_card_draw` method has been updated to correctly differentiate between position changes (values 1-40) and monetary updates (all other values).   Ensures that a player's position is not mistakenly set to a money value.  

- Resolved an issue where auctions could become stuck.  

  - If a human player voluntarily exits, the next player (if an AI) will now automatically take their turn without requiring user interaction.  

- **Exit/Give Up Button Visibility Fix:**  
  - The "Exit/Give Up" button will no longer be shown when:  
    - It is not the human player's turn.  
    - All human players have exited the game.  

#### Known new Bug

The game experiences significant lag when it reaches around 20 or more laps.
