Board Module
===========

This module contains the Board class that represents the game board and manages the visual representation and interaction with the game board.

Key Features
-----------

* Board initialization and setup
* Visual rendering of the game board
* Camera controls for zooming and panning
* Player token positioning and movement
* Property positioning and visualization
* Message display system
* Space management (properties, special spaces, etc.)

Board Structure
--------------

The game board consists of 40 spaces arranged in a square layout:

* Corner spaces (GO, Jail, Free Parking, Go to Jail)
* Property spaces (color-coded by property groups)
* Utility spaces (Electric Company, Water Works)
* Station spaces (train stations)
* Special spaces (Pot Luck, Opportunity Knocks, Tax spaces)

Camera Controls
-------------

The board implements a camera system that allows players to:

* Zoom in/out using +/- keys
* Pan the board using WASD or arrow keys
* Automatically center on important game events

Class Documentation
-----------------

.. automodule:: src.Board
   :members:
   :undoc-members:
   :show-inheritance:

CameraControls Class
------------------

The Board module also includes a CameraControls class that manages the zooming and panning functionality:

* ``zoom_level``: Current zoom level (default: 1.0)
* ``offset_x``, ``offset_y``: Current camera offset
* ``handle_camera_controls(keys)``: Process keyboard input for camera movement

Board Visualization
-----------------

The board visualization includes:

* Property ownership indicators
* Player token positioning
* Houses and hotels display
* Message notifications
* Highlighting of active spaces
* Visual effects for game events

Common Operations
---------------

The Board class provides several key operations:

* ``draw(screen)``: Render the board on the screen
* ``update_board_positions()``: Update the positions of all elements on the board
* ``get_space(position)``: Get the space at a specific position
* ``update_ownership(properties_data)``: Update property ownership visualization
* ``property_clicked(pos)``: Handle mouse clicks on properties
* ``add_message(text)``: Add a message to the board's message display
* ``board_to_screen(x, y)``: Convert board coordinates to screen coordinates 