Player Module
============

This module contains the Player class that represents a player in the game and manages player-specific actions and states. The Player class is responsible for tracking a player's assets, position, and status, as well as handling player-specific game mechanics.

Player Types
-----------

The game supports two types of players:

* **Human Players**: Controlled by user input, with decisions made by the human player
* **AI Players**: Controlled by computer AI (see :doc:`ai_player_logic`), with automated decision-making

Player Properties
---------------

Each player has the following key attributes:

* **Name and player number**: Identifies the player in the game
* **Token representation**: Visual representation on the game board
* **Current position**: Position on the board (1-40)
* **Money balance**: Current cash holdings
* **Owned properties**: List of properties owned by the player
* **Jail status**: Whether the player is in jail and for how many turns
* **Get out of jail cards**: Number of cards that can be used to exit jail
* **Bankruptcy status**: Whether the player has gone bankrupt
* **Visual attributes**: Color, animation state, and highlighting effects

Visual Representation
-------------------

Each player is visually represented on the board with:

* **Player token**: A unique image or colored circle with player number
* **Animation effects**: Movement animations, highlighting when active
* **Position indicators**: Shows the player's current position on the board
* **Status indicators**: Visual cues for jail status, bankruptcy, etc.

Movement and Animation
--------------------

The Player class handles movement around the board with:

* **Path generation**: Creates a path of positions for smooth movement
* **Animation**: Smooth transitions between board positions
* **Visual effects**: Bounce effects, glowing, and highlighting for the active player

Financial Management
------------------

Players manage their finances through:

* **Money tracking**: Keeping track of cash balance
* **Property ownership**: Managing owned properties and their development
* **Asset calculation**: Determining total assets including property value
* **Affordability checks**: Determining if a player can afford a purchase or payment

Class Documentation
-----------------

.. automodule:: src.Player
   :members:
   :undoc-members:
   :show-inheritance:

Player Initialization
-------------------

The Player class is initialized with:

* ``name``: The player's name
* ``player_number``: A unique number identifying the player (1-8)
* ``is_ai``: Boolean indicating if the player is AI-controlled

Player State
-----------

The Player class tracks various states:

* **Active state**: Whether it's currently the player's turn
* **Winner state**: Whether the player has won the game
* **Jail state**: Whether the player is in jail and for how many turns
* **Bankruptcy state**: Whether the player has gone bankrupt
* **Movement state**: Whether the player is currently moving and animation progress

Common Operations
---------------

Players can perform various actions during the game:

* ``move(steps)``: Move the player a specified number of steps
* ``pay(amount)``: Deduct money from the player's balance
* ``receive(amount)``: Add money to the player's balance
* ``buy_property(property)``: Purchase a property and add it to owned properties
* ``add_property(property)``: Add a property to the player's portfolio (for trades)
* ``remove_property(property)``: Remove a property from the player's portfolio
* ``can_afford(amount)``: Check if the player has enough money for a transaction
* ``get_total_assets()``: Calculate the player's total assets including property value
* ``handle_bankruptcy(creditor)``: Process the player's bankruptcy
* ``handle_voluntary_exit()``: Process the player voluntarily exiting the game

Jail Management
-------------

The Player class includes methods for jail management:

* ``add_jail_card(card_type)``: Add a Get Out of Jail Free card
* ``use_jail_card()``: Use a Get Out of Jail Free card
* ``handle_jail_turn()``: Process a turn while the player is in jail

Property Management
-----------------

Players can manage their properties with:

* ``get_mortgageable_properties()``: Get properties that can be mortgaged
* ``get_unmortgageable_properties()``: Get properties that can be unmortgaged
* ``get_properties_with_houses()``: Get properties with houses that can be sold
* ``get_properties_with_hotels()``: Get properties with hotels that can be sold
* ``can_build_houses()``: Check if the player can build houses on any properties
* ``can_build_hotels()``: Check if the player can build hotels on any properties

Trading
-------

Players can trade properties and money with other players. A trade can include:

* Properties
* Money
* Get out of jail cards
* Rent immunity agreements 