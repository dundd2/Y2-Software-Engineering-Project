Board Module
============

This module contains the Board class that represents the game board and manages the visual representation and interaction with the game board.

Key Features
------------

* **Visual Representation**: Rendering of the game board with all squares
* **Square Management**: Tracking and accessing different types of squares
* **Position Calculation**: Converting between board positions and screen coordinates
* **Player Token Placement**: Determining where to draw player tokens on the board
* **Property Highlighting**: Visual indication of selected properties
* **House and Hotel Visualization**: Showing property developments on the board
* **Card Space Representation**: Special visualization for card squares

Board Class
-----------

The Board class encapsulates the game board functionality:

.. plantuml::

   @startuml
   
   class Board {
     -image : Surface
     -width : int
     -height : int
     -position_data : Dict
     -property_render_data : Dict
     -special_squares : Dict
     -card_squares : Dict
     
     +__init__(board_image_path, width, height)
     +draw(screen)
     +get_square_position(position)
     +get_property_position(property_data)
     +get_square_at_coordinates(x, y)
     +highlight_property(property_data)
     +reset_highlights()
     +draw_houses(screen, property_data, houses)
     +draw_hotel(screen, property_data)
     +draw_mortgaged_indicator(screen, property_data)
     +draw_player(screen, player, offset_x, offset_y)
     +draw_development_options(screen, player)
     +draw_card_animation(screen, card_type)
}}}}}}}}}}}}}}}}}}}
   
   @enduml

Board Layout
------------

The board implements a standard property trading game layout:

.. plantuml::

   @startuml
   
   title Property Tycoon Board Layout
   
   rectangle "Property Tycoon Board" {
     rectangle "Go" as go #LightGreen
     rectangle "Old Kent Road" as old_kent #Brown
     rectangle "Community Chest" as cc1 #LightBlue
     rectangle "Whitechapel Road" as whitechapel #Brown
     rectangle "Income Tax" as income_tax #LightGray
     rectangle "Kings Cross Station" as kings_cross #White
     rectangle "The Angel Islington" as angel #LightCyan
     rectangle "Chance" as chance1 #Orange
     rectangle "Euston Road" as euston #LightCyan
     rectangle "Pentonville Road" as pentonville #LightCyan
     rectangle "Jail" as jail #LightGray
     
     rectangle "Pall Mall" as pall_mall #Pink
     rectangle "Electric Company" as electric #LightGray
     rectangle "Whitehall" as whitehall #Pink
     rectangle "Northumberland Avenue" as northumberland #Pink
     rectangle "Marylebone Station" as marylebone #White
     rectangle "Bow Street" as bow #Orange
     rectangle "Community Chest" as cc2 #LightBlue
     rectangle "Marlborough Street" as marlborough #Orange
     rectangle "Vine Street" as vine #Orange
     
     rectangle "Free Parking" as free_parking #LightGreen
     
     rectangle "Strand" as strand #Red
     rectangle "Chance" as chance2 #Orange
     rectangle "Fleet Street" as fleet #Red
     rectangle "Trafalgar Square" as trafalgar #Red
     rectangle "Fenchurch St. Station" as fenchurch #White
     rectangle "Leicester Square" as leicester #Yellow
     rectangle "Coventry Street" as coventry #Yellow
     rectangle "Water Works" as water #LightGray
     rectangle "Piccadilly" as piccadilly #Yellow
     
     rectangle "Go To Jail" as go_to_jail #LightGray
     
     rectangle "Regent Street" as regent #Green
     rectangle "Oxford Street" as oxford #Green
     rectangle "Community Chest" as cc3 #LightBlue
     rectangle "Bond Street" as bond #Green
     rectangle "Liverpool St. Station" as liverpool #White
     rectangle "Chance" as chance3 #Orange
     rectangle "Park Lane" as park #Blue
     rectangle "Super Tax" as super_tax #LightGray
     rectangle "Mayfair" as mayfair #Blue
}}}}}}}}}}}}}}}}
   
   @enduml

Board Coordinates System
------------------------

The Board module implements a coordinate system for positioning game elements:

.. plantuml::

   @startuml
   
   title Board Coordinate System
   
   rectangle "Board" {
     rectangle "Position 1\n(Go)" as p1
     rectangle "Position 2" as p2
     rectangle "..." as p3
     rectangle "Position 10" as p10
     rectangle "Position 11\n(Jail)" as p11
     
     rectangle "Position 40" as p40
     rectangle "..." as p39
     rectangle "Position 31" as p31
     rectangle "Position 30" as p30
     rectangle "Position 21\n(Free Parking)" as p21
     
     rectangle "Position 20" as p20
     rectangle "..." as p19
     rectangle "Position 12" as p12
}}}}}}}}}}
   
   note right of p1
     Each board position has:
     - Center coordinates (x, y)
     - Property render data if applicable
     - Player token placement offsets
     - Special rendering instructions
   end note
   
   @enduml

Square Types
------------

The board contains different types of squares with unique behaviors:

* **Property Squares**: Can be purchased and developed (standard properties, stations, utilities)
* **Card Squares**: Draw a card from Opportunity Knocks or Pot Luck decks
* **Corner Squares**: Special effects (Go, Jail, Free Parking, Go to Jail)
* **Tax Squares**: Pay a fixed amount to the bank

Property Visualization
----------------------

The Board handles visual representation of property development:

.. plantuml::

   @startuml
   
   title Property Development Visualization
   
   start
   
   :Request to Draw Property Development;
   
   if (Property Type?) then (Standard)
     if (Development Level?) then (Houses)
       :Calculate House Positions;
       :Draw Houses Based on Count;
     else if (Development Level?) then (Hotel)
       :Calculate Hotel Position;
       :Draw Hotel;
     endif
   endif
   
   if (Is Mortgaged?) then (Yes)
     :Draw Mortgage Indicator;
   endif
   
   if (Is Highlighted?) then (Yes)
     :Draw Highlight Effect;
   endif
   
   stop
   
   @enduml

Player Token Placement
----------------------

The Board handles positioning multiple player tokens on the same space:

.. plantuml::

   @startuml
   
   title Player Token Placement System
   
   start
   
   :Get Base Position for Board Square;
   
   :Count Players on Same Square;
   
   if (Player Count?) then (1 Player)
     :Place Token at Center;
   else if (Player Count?) then (2 Players)
     :Apply 2-Player Offset Pattern;
   else if (Player Count?) then (3 Players)
     :Apply 3-Player Offset Pattern;
   else if (Player Count?) then (4 Players)
     :Apply 4-Player Offset Pattern;
   else if (Player Count?) then (5 Players)
     :Apply 5-Player Offset Pattern;
   else (6 Players)
     :Apply 6-Player Offset Pattern;
   endif
   
   :Apply Animation Offset;
   
   :Draw Player Token at Final Position;
   
   stop
   
   @enduml

Interaction with Other Modules
------------------------------

The Board module interacts with several other components:

.. plantuml::

   @startuml
   
   title Board Module Integration
   
   class Board {
     +draw()
     +get_square_position()
     +highlight_property()
}
   
   class Game {
     +render()
     +handle_events()
}}}}}}}}}}}}}}}}
   
   class GameRenderer {
     +render_board()
     +render_players()
}}}}}}}}}}}}}}}}}
   
   class Player {
     +position
     +draw_player()
}}}}}}}}}}}}}}
   
   class Property {
     +position
     +houses
     +is_mortgaged
}}}}}}}}}}}}}
   
   class UI {
     +draw_property_card()
     +draw_buttons()
}}}}}}}}}}}}}}}
   
   Game --> Board : uses
   GameRenderer --> Board : uses
   Board --> Player : positions
   Board --> Property : shows development
   Board <--> UI : coordinates with
   
   @enduml

Board Implementation Details
----------------------------

The Board module provides several key implementation features:

* **Efficient Rendering**: Only redraws changed elements for performance
* **Flexible Scaling**: Adapts to different screen resolutions
* **Interactive Areas**: Defines clickable regions for user interaction
* **Visual Effects**: Implements highlighting and animation effects
* **Development Visualization**: Shows houses, hotels, and mortgages
* **Property Grouping**: Visual representation of property groups through colors

Class Documentation
-----------------

.. automodule:: src.Board
   :members:
   :undoc-members:
   :show-inheritance:
