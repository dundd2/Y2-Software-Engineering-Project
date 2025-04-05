# Property Tycoon - Build-17.02.2025V2 Update Log

## Changes

* **Auction System Overhaul:**  
  * **New Bidding Logic:**  The way players (both human and AI) bid on properties during auctions is now more dynamic and strategic.
  * **Minimum Bid Increments:**   a new minimum amount by which bids must increase, preventing excessively small bids.
  * **Auction Timer:** A timer has been added to auctions, giving players a limited time to place their bids. (Based on Owen's idea)
  * **Clearer Auction UI:** The on-screen display during auctions has been improved to show the current highest bid, the current bidder, and the time remaining more clearly.
  * **Auction Resolution:** The logic for determining the auction winner and handling payments has been refined for greater accuracy.
  * **Bidding history:** Auction bidding history has been added.

* **Player Turn & State Management:**
  * **Refined Turn Logic:**  The code that manages player turns, including rolling dice, moving, and handling actions (buying properties, paying rent, etc.), has been cleaned up and made more robust.  This should lead to smoother gameplay.
  * **Better State Tracking:** The game now keeps track of the game state (e.g., "rolling," "auction," "jail") more accurately, reducing potential errors.
  * **Space-Specific Actions:**  The code for handling actions on different spaces (e.g., "Go," "Jail," "Chance") has been improved.
  * **Player skip:** Added the ability to skip players who are in jail.
  * **Game over handling:** Added handling of game over situation.

* **UI**
  * **Color and Layout Adjustments:** Minor tweaks to colors, text placement, and element sizes

* **Jail System improvements:**
  * **Refined jail logic**: Fixed issues in jail logic.
  * **New jail exit method**: Added a new method to exit jail.

* **Property Management:**
  * **House/Hotel Calculations:**  code that calculates rent based on houses and hotels has been improved.
  * **Property Group Handling:**  The logic for managing property groups is more robust.
  * **Property display**: Property cards are displayed on screen.
  * **Buy Property**: Added a way for players to buy property after landing on it.

* **Money and transaction updates:**
  * **Money display**: Improved Money display for players.

* **Game Initialization and Setup:**
  * **Board Creation:** The way the game board is created at the start of the game has been updated.
  * **Player Setup:** The process of setting up players (names, starting money, etc.) has been refined.

**Bug Fixes:**

* Fix the game crash when change name
