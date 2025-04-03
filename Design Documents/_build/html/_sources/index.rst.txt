.. Software-Engineering-Project-Property Tycoon-2025 documentation master file, created by
   sphinx-quickstart on Mon Mar  3 07:23:54 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Property Tycoon Game Documentation
==================================

Welcome to the Property Tycoon game documentation! This is a digital implementation of a classic property trading board game developed by Group 5.

Quick Start
-----------

To get started with Property Tycoon:

1. Install the required dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

2. Run the game:

   .. code-block:: bash

      python Main.py

Game Overview
-------------

Property Tycoon is a property trading board game where players take turns rolling dice, moving around the board, and acquiring properties. Players can develop their properties with houses and hotels, charge rent to other players, and participate in auctions. The game includes various special squares like "Pot Luck" and "Opportunity Knocks" cards that add unpredictability to gameplay.

The game features:

* A virtual game board with properties organized into color groups
* Support for up to 6 players, including AI opponents
* Multiple AI difficulty levels with distinct behaviors and strategies
* Property development with houses and hotels
* Mortgage and auction systems
* Interactive UI with animations and sound effects
* Card events with various effects

Project Structure
-----------------

The project is organized into several key modules:

* **Main**: The entry point of the application, handling the main loop and page transitions.
* **Game**: The central controller that orchestrates the game flow.
* **Game Logic**: Implements the core game rules and mechanics.
* **Game Actions**: Encapsulates actions performed within the game loop.
* **Game Event Handler**: Manages user input and game events.
* **Game Renderer**: Handles drawing the game state to the screen.
* **Player**: Manages player attributes, movement, and interactions.
* **Property**: Handles property ownership, rent calculation, and development.
* **AI Player Logic**: Implements decision-making systems for AI players.
* **Board**: Manages the visual representation of the game board.
* **Cards**: Implements card effects and deck management.
* **UI**: Provides user interface components and visual feedback.
* **Development Mode**: Handles the property development interface.
* **Load Excel**: Loads game data from Excel spreadsheets.
* **Sound Manager**: Manages game audio effects and music.
* **Font Manager**: Manages font loading and scaling.

Module Documentation
--------------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/main
   modules/game
   modules/game_logic
   modules/game_actions
   modules/game_event_handler
   modules/game_renderer
   modules/player
   modules/board
   modules/property
   modules/ai_player_logic
   modules/cards
   modules/ui
   modules/development_mode
   modules/loadexcel
   modules/sound_manager
   modules/font_manager

Additional Documentation
------------------------

.. toctree::
   :maxdepth: 1
   :caption: Development:

   architecture
   development_guide
   testing

Team
----

* Eric Shi
* Stuart Baker
* Lin Moe Hein (kit)
* Duncan Law
* Owen Chen