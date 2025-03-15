Game Logic Module
===============

This module contains the game logic functions and classes that drive the game mechanics, including the core GameLogic class that manages the rules and flow of the Property Tycoon game.

Key Features
-----------

* **Game State Management**: Tracks players, properties, bank funds, and game progression
* **Turn Processing**: Handles player turns, dice rolls, and movement around the board
* **Property Transactions**: Manages buying, selling, mortgaging, and developing properties
* **Card Handling**: Implements Pot Luck and Opportunity Knocks card effects
* **Money Management**: Controls financial transactions between players and the bank
* **Auction System**: Provides a complete property auction mechanism
* **Bankruptcy Handling**: Manages player bankruptcy and asset liquidation
* **AI Player Logic**: Integrates with AI player decision-making systems
* **Game Rules Enforcement**: Ensures all game actions follow the established rules

Game Constants
------------

The GameLogic class defines several important constants:

* ``BANK_LIMIT``: The total amount of money in the bank (50,000)
* ``MAX_HOUSES_PER_PROPERTY``: Maximum number of houses per property (4)
* ``MAX_HOTELS_PER_PROPERTY``: Maximum number of hotels per property (1)
* ``GAME_TOKENS``: Available player tokens (boot, smartphone, ship, hatstand, cat, iron)

Game Initialization
-----------------

The GameLogic class initializes the game state with:

* Empty player list
* Bank money set to BANK_LIMIT
* Free parking fund set to 0
* Property data loaded from external source
* Shuffled card decks
* Game state tracking variables
* AI difficulty selection (easy or hard)

Card Systems
-----------

The module defines two types of card decks:

1. **Pot Luck Cards**: Cards that provide various effects like collecting money, paying fines, or moving to specific locations.

2. **Opportunity Knocks Cards**: Similar to Pot Luck cards but with different effects and probabilities.

Each card contains text to display to the player and an action function that implements its effect on the game state. Card effects include:

* Collecting or paying money
* Moving to specific board locations
* Getting out of jail
* Paying repair costs based on property development
* Collecting money from other players
* Making choices (like paying a fine or drawing another card)

Property Management
-----------------

The GameLogic class provides comprehensive property management:

* **Property Purchase**: Players can buy properties they land on
* **Property Auction**: When a player declines to buy a property, it goes to auction
* **Property Development**: Players can build houses and hotels on properties
* **Mortgaging**: Properties can be mortgaged for immediate cash
* **Rent Calculation**: Dynamic rent calculation based on property development


Class Documentation
-----------------

.. automodule:: src.game_logic
   :members:
   :undoc-members:
   :show-inheritance:

Turn Processing
-------------

The GameLogic class handles the complete turn sequence:

1. **Dice Rolling**: Generates random dice values
2. **Movement**: Updates player position based on dice roll
3. **Space Handling**: Processes the effect of the space the player lands on
4. **Property Actions**: Handles property purchases, rent payments, etc.
5. **Special Space Actions**: Manages effects of special spaces like Go, Jail, Free Parking, etc.
6. **Card Drawing**: Processes card effects when landing on card spaces

Jail System
-----------

The game implements a comprehensive jail system:

* **Going to Jail**: Players go to jail by landing on the "Go to Jail" space, drawing a card that sends them to jail, or rolling three consecutive doubles.
* **Jail Status Tracking**: The player's jail status is tracked via the 'in_jail' and 'jail_turns' properties.
* **Leaving Jail Options**:
  * Rolling doubles (automatic release)
  * Using a "Get Out of Jail Free" card
  * Paying a £50 fine
* **Forced Release**: After three turns in jail, players must pay the £50 fine or go bankrupt.
* **Jail Limitations**: Players in jail cannot collect rent or buy properties.
* **AI Jail Strategy**: AI players have specific strategies for handling jail based on their current financial situation and difficulty level.

Financial System
--------------

The game implements a comprehensive financial system:

* **Bank Transactions**: Methods for paying to and from the bank
* **Player Transactions**: Direct money transfers between players
* **Transaction Validation**: Ensures all transactions are valid
* **Bankruptcy Handling**: Manages player bankruptcy and asset liquidation
* **Payment Handling**: Special methods for handling various types of payments, including:
  * Regular payments to the bank
  * Payments to Free Parking
  * Birthday collections from all players
  * Property repair assessments

Auction System
------------

When a player declines to buy a property, it goes to auction:

1. All eligible players can participate in the auction
2. Players take turns bidding or passing
3. The highest bidder wins the property
4. The auction ends when all players except one have passed or time runs out
5. The auction system includes visual feedback and timers

AI Player Integration
------------------

The GameLogic class integrates with AI player logic:

* **AI Decision Making**: Handles AI player decisions during their turn
* **Property Purchase Decisions**: AI evaluates whether to buy properties
* **Auction Bidding**: AI determines appropriate bid amounts
* **Bankruptcy Prevention**: AI strategizes to avoid bankruptcy
* **AI Difficulty Levels**: Supports both easy and hard AI implementations with different strategies

Common Operations
---------------

The GameLogic module provides several key operations:

* **Player Management**: Adding, removing, and tracking players
* **Turn Processing**: Handling complete player turns
* **Property Transactions**: Buying, selling, and developing properties
* **Financial Transactions**: Managing money transfers
* **Game State Checking**: Determining game status and winner
* **Game Mode Support**: Supports both full game (last player standing) and abridged game (timed) modes