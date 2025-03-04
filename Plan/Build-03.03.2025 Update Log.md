## Property Tycoon - Build-03.03.2025 Update Log

**New Features:**

*   **Improved AI Decision-Making:** AI players now have more sophisticated logic for:
    *   Evaluating property value based on color groups, stations, and utilities.
    *   Making more informed decisions on whether to buy, bid in auctions, build houses/hotels, mortgage, or unmortgage.
    *   Strategic decision-making in jail based on there difficulty.

*   **Auction System:** Players can now auction properties they land on but choose not to buy. A dedicated auction screen and bidding process have been implemented, including:
    *   Minimum bid increments.
    *   Timeout for bids.
    *   Clear display of the current highest bidder and bid.
    *   AI players participate in auctions with strategic bidding.

*   **Development Mode:** Player can build house on a selected group of property
    *   Button for build, sell,mortgage and auction.
    *    UI for Player build, sell, mortgage and auction.
    
*  **Animation For Player Movement:** Player will moving on the board when rolling the dice.

*  **Special Card UI**: Add UI for drawing special card.

**Enhancements:**

*   **Improved UI:**
    *   Added enhanced visual effects for player tokens, including glowing effects for the current player and a winning animation.
    *   Streamlined game messages and added a message log to display recent actions.
    *   New auction UI, showing the property, current bid, and active bidders.
   *    UI for Game Over, with more detail information.
   

*   **Game Logic Refinements:**
    *   Refined player movement logic to handle edge cases and invalid positions more robustly.
    *   Improved handling of player bankruptcy and voluntary exits.
    *   Added Free Parking pot to collect fines and taxes, awarded to players landing on Free Parking.
    *   Streamlined turn processing and state transitions.
    *   Fixed inconsistencies in player position synchronization.
    *  Auction will skipped if no player can bid.
    *   Implemented a delay after an auction ends before proceeding to the next turn.

*   **Code Structure:**
    *   Refactored key game logic functions for better readability and maintainability.

**Bug Fixes:**

*   Fixed: Resolved an issue where the game state would become inconsistent after certain player actions.
*   Fixed: Addressed several edge cases in player movement and property ownership.
*   Fixed: Corrected issues with animation timing and display.
*   Fixed: Ensured that AI players handled various game states and events properly.
*   Fixed: Fixed a bug that a player could not buy properties if it didn't complete a round.
*   Fixed: Fixed an issue that will crash the game when a player is in jail
*   Fixed: Fixed a bug that a  player who was not in the game could still buy property
*   Fixed: Player Position Bug:** Resolved an issue where AI players could have positions outside the valid board range (1-40).  Positions are now validated and corrected if necessary.
*   Fixed: Auction System Inconsistency:** Corrected the auction system to accurately track and display the correct property being auctioned.
*   Fixed: Duplicate Messages:** Eliminated redundant message processing to prevent duplicate prompts and log entries.
*   Fixed: Player/AI Purchase Confusion:**  Fixed logic to ensure that AI decision-making functions are only called for AI players, preventing incorrect attribution of actions.
*   Fixed: Inconsistent Turn Flow: Improved the turn management logic to ensure players take turns in the correct sequence, preventing issues like players getting multiple consecutive turns.

  
  **Documentation**
  
   Created software documentation in HTML format using the Sphinx documentation generator. 
