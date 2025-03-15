Game Module
==========

This module contains the main Game class which orchestrates the game flow and manages the overall game state. It serves as the central controller for the Property Tycoon game, handling everything from game initialization to player turns, property management, and win conditions.

Key Features
-----------

* **Game initialization and setup**: Creates and configures the game environment, board, and players
* **Turn management**: Controls the flow of player turns and actions
* **Player actions handling**: Processes player decisions like buying properties, paying rent, and development
* **Game state management**: Tracks and updates the state of the game, including player positions and property ownership
* **Win condition checking**: Determines when the game ends and identifies the winner
* **Save/Load game functionality**: Allows games to be saved and resumed later
* **Multiple game modes**: Supports different game modes including full game and time-limited games
* **AI player support**: Includes AI players with different difficulty levels
* **Visual rendering**: Handles the graphical representation of the game state
* **User interface**: Manages buttons, notifications, and interactive elements

Game Modes
---------

The Game class supports multiple game modes:

1. **Full Game**: The traditional game that continues until only one player remains solvent
2. **Time-Limited Game**: A game that ends after a specified time limit, with the winner determined by total assets
3. **Abridged Game**: A shorter version of the game with modified rules for quicker play

User Interface Components
-----------------------

The Game class manages several UI components:

* **Board visualization**: Renders the game board with property ownership indicators
* **Player information**: Displays player stats including money, properties, and position
* **Action buttons**: Provides interactive buttons for player decisions
* **Dice animation**: Visualizes dice rolls with animated graphics
* **Property cards**: Shows detailed information about properties
* **Notifications**: Displays game events and important messages
* **Development UI**: Interface for building houses and hotels
* **Auction system**: UI for property auctions when players decline to purchase

Class Documentation
-----------------

.. automodule:: src.Game
   :members:
   :undoc-members:
   :show-inheritance:

Game Initialization
-----------------

The Game class is initialized with the following parameters:

* ``players``: List of Player objects representing the game participants
* ``game_mode``: String indicating the game mode ("full", "abridged", etc.)
* ``time_limit``: Optional time limit in milliseconds for time-limited games
* ``ai_difficulty``: String indicating AI difficulty level ("easy", "hard")

Turn Management
-------------

The game manages player turns through several key methods:

* ``play_turn()``: Processes a player's turn, including dice rolling, movement, and action handling
* ``handle_space(player)``: Determines the action to take based on the space a player lands on
* ``handle_ai_turn(player)``: Manages turns for AI players with automated decision-making
* ``handle_jail_turn(player)``: Special handling for players currently in jail

Property Management
-----------------

The Game class provides comprehensive property management:

* ``handle_buy_decision(wants_to_buy)``: Processes a player's decision to buy a property
* ``start_auction(property_data)``: Initiates an auction when a player declines to buy a property
* ``draw_development_ui(property_data)``: Displays the interface for property development
* ``handle_development_click(pos, property_data)``: Processes player interactions with the development UI

Common Operations
---------------

The Game class provides several key operations:

* ``start()``: Initialize and start a new game
* ``process_turn()``: Handle a player's turn
* ``move_player(player, steps)``: Move a player on the board
* ``handle_property_purchase(player, property)``: Process property purchases
* ``handle_rent_payment(player, property)``: Handle rent payments
* ``save_game(filename)``: Save the current game state
* ``load_game(filename)``: Load a previously saved game
* ``check_game_over()``: Determine if the game has ended
* ``handle_bankruptcy(player)``: Process a player's bankruptcy
* ``calculate_player_assets(player)``: Calculate a player's total assets
* ``show_notification(text, duration)``: Display a notification message
* ``handle_card_draw(player, card_type)``: Process drawing a card from a deck

Event Handling
------------

The Game class includes comprehensive event handling:

* ``handle_click(pos)``: Process mouse click events
* ``handle_motion(pos)``: Process mouse movement events
* ``handle_key(event)``: Process keyboard input events
* ``handle_auction_input(event)``: Process input during auctions
* ``handle_auction_click(pos)``: Process clicks during auctions 