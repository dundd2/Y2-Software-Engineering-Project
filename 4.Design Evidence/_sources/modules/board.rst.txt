Board Module
============

This module defines the `Board` class, responsible for managing and drawing the visual representation of the Property Tycoon game board, including player tokens, property ownership indicators, and the message log. It also handles camera controls like zooming and panning.

.. automodule:: src.Board
   :members:
   :undoc-members:
   :show-inheritance:

Diagrams
--------

**Board Class Structure**

.. uml::

    class Board {
        + players : List
        + spaces : List
        + properties_data : Dict
        + camera : CameraControls
        + board_image : Surface
        + background_image : Surface
        + board_rects : List
        + messages : List
        + message_times : List
        + message_font : Font
        
        + __init__(players)
        + add_message(text)
        + _create_board_rects()
        + update_board_positions()
        + draw_player(screen, player, rect, index)
        + _get_player_position_on_rect(rect, player_number, is_corner, apply_bounds)
        + draw(screen)
        + get_space(position)
        + update_ownership(properties_data)
        + get_property_group(position)
        + get_property_position(position)
        + board_to_screen(x, y)
        + update_offset(dx, dy)
        + property_clicked(pos)
    }

    class CameraControls {
        + zoom_level : float
        + offset_x : int
        + offset_y : int
        + move_speed : int
        + zoom_speed : float
        + min_zoom : float
        + max_zoom : float
        
        + __init__()
        + handle_camera_controls(keys)
    }

    class Property {
    }

    class Player {
        + position : int
        + player_number : int
        + color
        + player_image
        + animation_offset
        + is_moving
    }

    class Font_Manager {
        + get_font(size)
    }

    class Loadexcel {
        + load_property_data()
    }

    Board o-- CameraControls : contains
    Board ..> Player : uses
    Board ..> Property : uses
    Board ..> Font_Manager : uses
    Board ..> Loadexcel : uses
    Board ..> pygame : uses

**Board State Flow**

.. uml::

    [*] --> Initialize
    Initialize --> DrawBoard : Board created
    
    state DrawBoard {
        [*] --> PrepareRendering
        PrepareRendering --> HandleCamera : Apply camera controls
        HandleCamera --> RenderBackground
        RenderBackground --> RenderBoardImage
        RenderBoardImage --> RenderPlayers : Loop through each player
        RenderPlayers --> RenderMessageLog
        RenderMessageLog --> [*]
    }
    
    DrawBoard --> UpdateOwnership : Properties change ownership
    UpdateOwnership --> DrawBoard : Board redrawn
    
    DrawBoard --> AddMessage : Game event occurs
    AddMessage --> DrawBoard : Message added to log
    
    DrawBoard --> UpdatePositions : Players move
    UpdatePositions --> DrawBoard : Board redrawn

**Board Drawing Process Flow Chart**

.. uml::

    @startuml
    start
    :Initialize Board;
    
    repeat
      :Handle Camera Controls;
      note right
        Process zoom and panning
        based on keyboard input
      end note
      
      :Update Board Positions;
      note right
        Recalculate board_rects
        Update player positions
      end note
      
      :Prepare Drawing Surface;
      
      if (Background Image Available?) then (yes)
        :Draw Scaled Background;
      else (no)
        :Fill with UI Background Color;
      endif
      
      :Draw Board Image;
      
      :Create Transparent Layer for Players;
      
      fork
        :Draw Player Tokens;
        note right
          For each player:
          - Calculate position
          - Handle movement animation
          - Draw player token
        end note
      fork again
        :Draw Property Ownership Indicators;
      end fork
      
      :Draw Message Log Panel;
      
      :Render Messages in Log;
      note right
        Display last N messages
        with timestamps
      end note
      
      :Blit All Layers to Screen;
      
      :Process User Input;
      if (Property Clicked?) then (yes)
        :Return Property Position;
      else (no)
        :Continue;
      endif
      
    repeat while (Game Running?) is (yes)
    
    stop
    @enduml

**Board Camera Control Flow**

.. uml::
    
    @startuml
    start
    
    :Get Keyboard State;
    
    if (+ or = Key Pressed?) then (yes)
      :Increase Zoom Level;
      note right: Limited by max_zoom
    endif
    
    if (- Key Pressed?) then (yes)
      :Decrease Zoom Level;
      note right: Limited by min_zoom
    endif
    
    :Calculate Movement Speed;
    note right: Adjusted by zoom level
    
    if (Arrow/WASD Keys Pressed?) then (yes)
      :Update Offset X/Y;
    endif
    
    :Constrain Offset to Bounds;
    
    :Return Updated Camera Parameters;
    
    stop
    @enduml
