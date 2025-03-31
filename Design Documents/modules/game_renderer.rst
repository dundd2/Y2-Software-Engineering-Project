Game Renderer Module
====================

This module contains the GameRenderer class that handles all visual rendering of the game state, including the board, properties, players, UI elements, and animations.

Key Features
------------

* **Game State Rendering**: Visual representation of the complete game state
* **Layered Rendering**: Organization of visual elements in multiple layers
* **Animation Integration**: Coordination with the animation system
* **Board Rendering**: Drawing of the game board and its elements
* **Player Token Rendering**: Visual representation of players on the board
* **Property Development Visualization**: Display of houses and hotels
* **UI Element Integration**: Coordination with UI components
* **Performance Optimization**: Efficient rendering techniques

GameRenderer Class
------------------

The GameRenderer class encapsulates the game rendering functionality:

.. plantuml::

   @startuml
   
   class GameRenderer {
     -screen : Surface
     -game : Game
     -board : Board
     -ui : UI
     -font_manager : FontManager
     -animation_manager : AnimationManager
     -render_layers : Dict
     -fps_counter : FPSCounter
     -last_frame_time : float
     
     +__init__(screen, game, board, ui)
     +render_game_state()
     +render_board()
     +render_properties()
     +render_players()
     +render_ui()
     +render_animations()
     +render_development()
     +render_dice()
     +render_notifications()
     +render_player_info()
     +update_render_layers()
     +get_fps()
     +toggle_fps_display()
     +set_vsync(enabled)
     +optimize_rendering()
}
   
   @enduml

Rendering System
----------------

The module implements a multi-layered rendering system:

.. plantuml::

   @startuml
   
   title Rendering System Architecture
   
   package "Rendering Layers" {
     rectangle "Background Layer" as BG {
       rectangle "Board" as Board
       rectangle "Background Elements" as BGElements
}}}}}
     
     rectangle "Game Elements Layer" as Game {
       rectangle "Properties" as Properties
       rectangle "Development" as Development
       rectangle "Special Squares" as Special
}}}}}}}}}}}}}}}}}}
     
     rectangle "Player Layer" as Players {
       rectangle "Player Tokens" as Tokens
       rectangle "Player Animations" as PlayerAnim
}}}
     
     rectangle "UI Layer" as UI {
       rectangle "Buttons" as Buttons
       rectangle "Dialogs" as Dialogs
       rectangle "Property Cards" as Cards
       rectangle "Player Info Panel" as InfoPanel
}}
     
     rectangle "Effects Layer" as Effects {
       rectangle "Animations" as Animations
       rectangle "Notifications" as Notifications
       rectangle "Dice" as Dice
       rectangle "Highlights" as Highlights
}}}}}}}}}}}}}}}}
     
     rectangle "Debug Layer" as Debug {
       rectangle "FPS Counter" as FPS
       rectangle "Debug Info" as DebugInfo
}}}}}}}}}}}}}}}
   }
   
   BG -down-> Game : renders before
   Game -down-> Players : renders before
   Players -down-> UI : renders before
   UI -down-> Effects : renders before
   Effects -down-> Debug : renders before
   
   class GameRenderer {
     +render_game_state()

   
   GameRenderer --> BG : renders
   GameRenderer --> Game : renders
   GameRenderer --> Players : renders
   GameRenderer --> UI : renders
   GameRenderer --> Effects : renders
   GameRenderer --> Debug : renders
   
   @enduml

Rendering Flow
--------------

The module implements a structured rendering process:

.. plantuml::

   @startuml
   
   title Rendering Process Flow
   
   start
   
   :Begin Frame Rendering;
   
   :Calculate Frame Time;
   
   :Clear Screen;
   
   :Update Animation States;
   
   :Render Background Layer;
   note right
     Draw board and
     background elements
   end note
   
   :Render Game Elements Layer;
   note right
     Draw properties, houses,
     hotels, and special squares
   end note
   
   :Render Player Layer;
   note right
     Draw player tokens and
     player movement animations
   end note
   
   :Render UI Layer;
   note right
     Draw buttons, dialogs,
     property cards, and player info
   end note
   
   :Render Effects Layer;
   note right
     Draw animations, notifications,
     dice, and highlights
   end note
   
   if (Debug Mode?) then (Yes)
     :Render Debug Layer;
     note right
       Draw FPS counter and
       debug information
     end note
   endif
   
   :Update Display;
   
   :Calculate and Limit FPS;
   
   stop
   
   @enduml

Property Rendering
------------------

The module handles property visualization:

.. plantuml::

   @startuml
   
   title Property Rendering
   
   start
   
   :Get All Properties;
   
   repeat
     :Get Property Data;
     
     :Get Property Position;
     
     :Determine Ownership;
     
     if (Property Owned?) then (Yes)
       :Get Owner Color;
       
       :Draw Ownership Indicator;
       
       if (Is Mortgaged?) then (Yes)
         :Draw Mortgage Indicator;
       endif
       
       if (Has Development?) then (Yes)
         :Count Houses;
         
         if (Houses == 5?) then (Yes)
           :Draw Hotel;
         else (No)
           :Draw Houses;
         endif
       endif
     endif
     
     if (Property Highlighted?) then (Yes)
       :Draw Highlight Effect;
     endif
   repeat while (More Properties?) is (Yes)
   
   stop
   
   @enduml

Player Rendering
----------------

The module implements player token visualization:

.. plantuml::

   @startuml
   
   title Player Token Rendering
   
   start
   
   :Get All Players;
   
   repeat
     :Get Player Data;
     
     :Get Player Position;
     
     :Calculate Token Position;
     note right
       Account for multiple players
       on same square
     end note
     
     :Get Player Token Image;
     
     if (Player Moving?) then (Yes)
       :Apply Movement Animation;
       :Calculate Animated Position;
     endif
     
     if (Is Current Player?) then (Yes)
       :Add Current Player Indicator;
     endif
     
     :Draw Player Token;
     
     if (Debug Mode?) then (Yes)
       :Draw Player Stats;
     endif
   repeat while (More Players?) is (Yes)
   
   stop
   
   @enduml

Animation Integration
---------------------

The module integrates with the animation system:

.. plantuml::

   @startuml
   
   title Animation Integration
   
   class GameRenderer {
     +render_animations()
     +render_game_state()

   
   class AnimationManager {
     -active_animations : List
     +update(delta_time)
     +draw(screen)
     +is_animating()
     +create_animation(type, parameters)
}}}}}}}}}}}}}}}
   
   class DiceAnimation {
     +update(delta_time)
     +draw(screen)
     +is_complete()
}}}}}}}}}}}}}}
   
   class PlayerMovementAnimation {
     +update(delta_time)
     +draw(screen)
     +is_complete()
}}}}}}}}}}}}}}
   
   class CardAnimation {
     +update(delta_time)
     +draw(screen)
     +is_complete()
}}}}}}}}}}}}}}
   
   class NotificationAnimation {
     +update(delta_time)
     +draw(screen)
     +is_complete()
}}}}}}}}}}}}}}
   
   GameRenderer --> AnimationManager : uses
   AnimationManager *-- DiceAnimation
   AnimationManager *-- PlayerMovementAnimation
   AnimationManager *-- CardAnimation
   AnimationManager *-- NotificationAnimation
   
   @enduml

Performance Optimization
------------------------

The module implements performance optimizations:

.. plantuml::

   @startuml
   
   title Rendering Performance Optimization
   
   start
   
   :Implement Surface Caching;
   note right
     Cache static elements like
     board and property graphics
   end note
   
   :Use Layered Rendering;
   note right
     Only redraw layers that
     have changed
   end note
   
   :Implement Dirty Rectangle System;
   note right
     Only update regions of
     screen that changed
   end note
   
   :Limit Frame Rate;
   note right
     Cap FPS to display
     refresh rate
   end note
   
   :Use Sprite Batching;
   note right
     Group similar sprites
     for efficient rendering
   end note
   
   :Optimize Asset Sizes;
   note right
     Use appropriate texture
     sizes and compression
   end note
   
   :Implement Viewport Culling;
   note right
     Only render elements
     visible on screen
   end note
   
   :Profile and Optimize Bottlenecks;
   
   stop
   
   @enduml

Integration with Game Module
----------------------------

The GameRenderer integrates with several other modules:

.. plantuml::

   @startuml
   
   title GameRenderer Integration
   
   class GameRenderer {
     +render_game_state()
     +render_board()
     +render_players()
     +render_ui()
}}}}}}}}}}}}
   
   class Game {
     -renderer : GameRenderer
     -board : Board
     -players : List<Player>
     -ui : UI
     +get_state()
     +update()
}}}}}}}}}
   
   class Board {
     +draw(screen)
     +get_property_position(property_data)
}}}}}}}}}}}}}}}}}
   
   class Player {
     +draw(screen, position)
     +get_token_image()
}}}}}}}}}}}}}}}}}}
   
   class UI {
     +draw_game_ui(game_state)
     +draw_menu(menu_name)
}
   
   class Property {
     +draw_houses(screen, count)
     +draw_hotel(screen)
     +draw_mortgage_indicator(screen)
}}}}}}}}}}}}
   
   Game *-- GameRenderer
   GameRenderer --> Board : renders
   GameRenderer --> Player : renders
   GameRenderer --> UI : collaborates with
   GameRenderer --> Property : renders
   
   @enduml

Render States
-------------

The module handles different rendering states:

.. plantuml::

   @startuml
   
   title Render States
   
   state "Menu Rendering" as MENU {
     [*] --> RenderBackground
     RenderBackground --> RenderMenuUI
     RenderMenuUI --> RenderMenuAnimations
     RenderMenuAnimations --> [*]
}}}}}}}}
   
   state "Game Rendering" as GAME {
     [*] --> RenderBoard
     RenderBoard --> RenderProperties
     RenderProperties --> RenderPlayers
     RenderPlayers --> RenderGameUI
     RenderGameUI --> RenderAnimations
     RenderAnimations --> RenderEffects
     RenderEffects --> [*]
}
   
   state "Dialog Rendering" as DIALOG {
     [*] --> RenderGameUnderlay
     RenderGameUnderlay --> RenderDialogOverlay
     RenderDialogOverlay --> RenderDialogContent
     RenderDialogContent --> RenderDialogAnimations
     RenderDialogAnimations --> [*]
}}}}}}}}}}
   
   state "End Game Rendering" as END_GAME {
     [*] --> RenderEndGameBackground
     RenderEndGameBackground --> RenderStatistics
     RenderStatistics --> RenderEndGameUI
     RenderEndGameUI --> RenderEndGameAnimations
     RenderEndGameAnimations --> [*]
}}}}}}}}}}}
   
   [*] --> MENU
   MENU --> GAME : Start Game
   GAME --> DIALOG : Show Dialog
   DIALOG --> GAME : Close Dialog
   GAME --> END_GAME : Game Over
   END_GAME --> MENU : Return to Menu
   
   @enduml

Class Documentation
-----------------

.. automodule:: src.GameRenderer
   :members:
   :undoc-members:
   :show-inheritance: