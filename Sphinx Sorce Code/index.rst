.. Software-Engineering-Project-Property Tycoon-2025 Game Design Documentation
   sphinx-quickstart on Mon Mar  3 07:23:54 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Software-Engineering-Project 2025 -Property Tycoon Game Design Documentation
===========================================================================

This documentation covers the digital implementation of Watson Games' Property Tycoon, developed by Group 5. The project represents Watson Games' first foray into digital gaming, transforming their classic property trading board game into an interactive computer game experience.

Key Project Requirements:
------------------------

* Development of a computer version of the classic Property Tycoon board game
* Implementation of AI players to enable single-player experiences
* Support for up to 6 players (human and/or AI)
* Creation of an engaging digital experience that maintains the social aspects of the original game
* Development using Agile methodologies with flexibility for evolving requirements
* Implementation of a comprehensive GUI component
* Thorough testing at both unit and system levels

Design Documentation
-------------------

This documentation includes design diagrams that illustrate the game's architecture and functionality:

* **UML Class Diagrams**
* **Entity Relationship Diagrams**


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

.. toctree::
   :maxdepth: 1
   :caption: Development:

   architecture
   development_guide
   testing

Group 5 Team members 
-------------------

* Eric Shi
* Stuart Baker
* Lin Moe Hein (kit)
* Duncan Law
* Owen Chen