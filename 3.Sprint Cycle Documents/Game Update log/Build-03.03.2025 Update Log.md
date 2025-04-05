# Property Tycoon - Build-03.03.2025 Update Log

## Changes

* **Improved AI Decision-Making:** AI players now have more sophisticated logic for:
  * Evaluating property value based on color groups, stations, and utilities.
  * Making more informed decisions on whether to buy, bid in auctions, build houses/hotels, mortgage, or unmortgage.
  * Strategic decision-making in jail based on there difficulty.

* **Auction System:** Players can now auction properties they land on but choose not to buy. A dedicated auction screen and bidding process have been implemented, including:
  * Minimum bid increments.
  * Timeout for bids.
  * Clear display of the current highest bidder and bid.
  * AI players participate in auctions with strategic bidding.

* **Development Mode:** Player can build house on a selected group of property
  * Button for build, sell,mortgage and auction.
  * UI for Player build, sell, mortgage and auction.

* **Animation For Player Movement:** Player will moving on the board when rolling the dice.

* **Special Card UI**: Add UI for drawing special card.

**Enhancements:**

* **Improved UI:**
  * Added enhanced visual effects for player tokens, including glowing effects for the current player and a winning animation.
  * Streamlined game messages and added a message log to display recent actions.
  * New auction UI, showing the property, current bid, and active bidders.
* UI for Game Over, with more detail information.

* **Game Logic Refinements:**
  * Refined player movement logic to handle edge cases and invalid positions more robustly.
  * Improved handling of player bankruptcy and voluntary exits.
  * Added Free Parking pot to collect fines and taxes, awarded to players landing on Free Parking.
  * Streamlined turn processing and state transitions.
  * Fixed inconsistencies in player position synchronization.
  * Auction will skipped if no player can bid.
  * Implemented a delay after an auction ends before proceeding to the next turn.

* **Code Structure:**
  * Refactored key game logic functions for better readability and maintainability.

**Bug Fixes:**

* Resolved an issue where the game state could become inconsistent after certain player actions.
* Addressed edge cases in player movement and property ownership.
* Ensured AI players properly handled various game states and events.
* Fixed errors related to missing or invalid property data.
* Fixed a bug preventing property purchases before completing a full round.
* Prevented players from controlling AI during auctions.
* Resolved a crash when a player was in jail.
* Prevented an infinite loop when all players were in an auction, and the current bidder was AI.
* Player Position Bug: Ensured AI positions remained within the valid board range (1-40).
* Auction System Inconsistency: Fixed incorrect property tracking in auctions.
* Duplicate Messages: Eliminated redundant prompts and log entries.
* Player/AI Purchase Confusion: Ensured AI decision-making applies only to AI players.
* Inconsistent Turn Flow: Improved turn management to prevent extra turns.

**Documentation:**  
Created comprehensive software documentation in HTML using Sphinx, including:  

* Detailed class and function descriptions  
* Flowchart diagrams of game logic, player interactions, and AI decisions  
