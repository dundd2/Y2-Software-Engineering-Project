AI Player Logic Module
===================

This module contains the logic for AI players in the game, implementing different difficulty levels and strategic decision-making processes for computer-controlled players.

Key Features
-----------

* **Multiple Difficulty Levels**: Implements Easy and Hard AI player strategies
* **Property Valuation**: Sophisticated algorithms to evaluate property worth
* **Auction Bidding**: Strategic bidding in property auctions
* **Development Decisions**: Logic for when and where to build houses and hotels
* **Financial Management**: Handling money, including emergency cash strategies
* **Jail Strategies**: Decision-making for jail situations
* **Trade Evaluation**: Assessing and responding to trade offers

AI Player Types
-------------

The module implements two main types of AI players:

1. **EasyAIPlayer**: A more forgiving AI that makes suboptimal decisions, suitable for casual players
2. **HardAIPlayer**: A more challenging AI that makes strategically sound decisions

AI Strategy Components
--------------------

Each AI player type implements various strategic components:

* **Property Acquisition Strategy**: Determines which properties to buy and how much to bid
* **Development Strategy**: Decides when and where to build houses and hotels
* **Cash Management Strategy**: Handles money, including when to mortgage properties
* **Jail Strategy**: Decides whether to pay to get out of jail or wait
* **Emergency Strategy**: Handles situations where cash is urgently needed

Property Valuation System
-----------------------

The AI uses a sophisticated property valuation system that considers:

* **Base Property Value**: The listed price of the property
* **Color Group Completion**: Higher value for properties that complete a color group
* **Existing Ownership**: Value increases for properties in groups where the AI already owns properties
* **Station and Utility Synergy**: Value increases based on how many stations or utilities the AI already owns
* **Strategic Position**: Value adjustments based on board position and landing probability

Class Documentation
-----------------

.. automodule:: src.ai_player_logic
   :members:
   :undoc-members:
   :show-inheritance:

EasyAIPlayer Class
----------------

The ``EasyAIPlayer`` class implements a more forgiving AI strategy with the following key methods:

* ``get_property_value``: Calculates the perceived value of a property
* ``handle_turn``: Manages the AI's actions during its turn
* ``get_auction_bid``: Determines how much to bid in property auctions
* ``handle_jail_strategy``: Decides what to do when in jail
* ``handle_property_development``: Makes decisions about building houses and hotels
* ``handle_emergency_cash``: Generates cash when needed through mortgages or selling

HardAIPlayer Class
----------------

The ``HardAIPlayer`` class implements a more challenging AI strategy with enhanced decision-making:

* More aggressive property acquisition
* Smarter auction bidding
* Optimal development strategies
* Better cash management
* Strategic jail decisions

Decision-Making Process
--------------------

The AI's decision-making process involves several steps:

1. **Situation Assessment**: Analyzing the current game state
2. **Option Generation**: Identifying possible actions
3. **Option Evaluation**: Calculating the expected value of each action
4. **Action Selection**: Choosing the action with the highest expected value

For property purchases, the AI considers:
* Current cash reserves
* Property's intrinsic value
* Potential for completing color groups
* Expected return on investment

For development decisions, the AI evaluates:
* Cash availability
* Return on investment for houses/hotels
* Risk of landing on expensive properties
* Strategic value of blocking other players

Difficulty Adjustment
------------------

The AI's difficulty can be adjusted through several parameters:

* ``max_bid_multiplier``: Controls how aggressively the AI bids in auctions
* ``development_threshold``: Determines how readily the AI builds houses and hotels
* ``jail_stay_threshold``: Affects how likely the AI is to pay to leave jail
* ``mortgage_threshold``: Influences when the AI decides to mortgage properties

These parameters are set differently for Easy and Hard AI players, creating distinct playing experiences. 