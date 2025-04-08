Development Mode Module
=======================

This module defines the `DevelopmentMode` class, responsible for handling the game state where a player can manage their owned properties. This includes building houses/hotels, selling buildings, mortgaging/unmortgaging properties, and selling properties back to the bank. It provides both visual feedback on the board (highlighting developable properties) and a dedicated UI panel when a specific property is selected.

High-Level Design
-----------------

Use Case Diagram
~~~~~~~~~~~~~~~~

Illustrates the primary actions a player can perform when development mode is active.

.. uml::

    @startuml
    left to right direction
    actor Player

    rectangle "Development Mode" {
      usecase "Activate Development Mode" as ADM
      usecase "Select Owned Property" as SOP
      usecase "View Property Details & Actions" as View
      usecase "Build House/Hotel" as Build
      usecase "Sell House/Hotel" as Sell
      usecase "Mortgage/Unmortgage Property" as Mortgage
      usecase "Sell Property to Bank" as SellBank
      usecase "Close Property View" as Close
      usecase "Deactivate Development Mode" as DDM
      
      Player -- ADM
      Player -- SOP
      SOP --> View
      View --> Build
      View --> Sell
      View --> Mortgage
      View --> SellBank
      View --> Close
      Player -- DDM

      note right of ADM
        Requires player to have
        completed at least one lap
        and own developable properties.
        Can be activated for Human or AI.
      end note

      note right of Build
        Requires owning full color set,
        sufficient funds, and adhering
        to building limits/rules.
      end note
    }
    @enduml

State Diagram
~~~~~~~~~~~~~

Shows the states related to the `DevelopmentMode` being active and whether a property UI is displayed. Note that this also influences the main `Game.state`.

.. uml::

    @startuml
    [*] --> Inactive : Initial State

    state Active {
      [*] --> BrowsingProperties : Mode Activated
      BrowsingProperties : Player can click owned properties\nDraws flashing stars
      BrowsingProperties --> PropertySelected : Player clicks own property
      PropertySelected : Displays Development UI Panel\nHandles UI button clicks/keys
      PropertySelected --> BrowsingProperties : Player clicks "Close" button or outside UI
      PropertySelected --> BrowsingProperties : Action performed (e.g., build, mortgage)
      PropertySelected --> Inactive : Player sells last property
      BrowsingProperties --> Inactive : Player ends turn / Mode deactivated externally
    }

    Active --> Inactive : Deactivate called / Player turn ends

    note right of Active
     When Active, the main Game state
     is typically "DEVELOPMENT".
    end note
    @enduml

Detailed Design
---------------

Class Diagram
~~~~~~~~~~~~~~

Details the `DevelopmentMode` class and its primary interactions.

.. uml::

    @startuml
    class DevelopmentMode {
      - game: Game
      - game_actions: GameActions
      - screen: pygame.Surface
      - font: pygame.font.Font
      - small_font: pygame.font.Font
      - tiny_font: pygame.font.Font
      - is_active: bool
      - buttons: dict(str, pygame.Rect)
      - last_star_flash_time: int
      - show_property_stars: bool
      + activate(player: dict): bool
      + can_develop_ai(player: dict): bool
      + deactivate()
      + draw(mouse_pos: tuple)
      + handle_click(pos: tuple): any
      + handle_key(event: pygame.Event): any
      - _draw_property_stars()
      - _draw_star(x: int, y: int)
      - _draw_development_ui(property_data: dict, mouse_pos: tuple)
      - _draw_button(button_rect: pygame.Rect, text: str, mouse_pos: tuple, active: bool, color: tuple)
    }

    note right of DevelopmentMode::handle_key
      Keyboard shortcuts (1-4, ESC)
      only apply to human players
      when a property UI is open.
    end note

    DevelopmentMode ..> "1" Game : uses
    DevelopmentMode ..> "1" GameActions : uses
    DevelopmentMode ..> GameLogic : uses
    DevelopmentMode ..> GameBoard : uses
    DevelopmentMode ..> pygame : uses
    DevelopmentMode ..> math : uses

    note "Implied classes/data structures used" as N3
    class Game {
      + screen: pygame.Surface
      + font: pygame.font.Font
      + small_font: pygame.font.Font
      + tiny_font: pygame.font.Font
      + logic: GameLogic
      + board: GameBoard
      + selected_property: dict
      + state: str
      + lap_count: dict
    }
    class GameActions {
      + start_auction(property: dict)
    }
    class GameLogic {
      + properties: dict(str, dict)
      + players: list(dict)
      + current_player_index: int
      + can_build_house(prop: dict, player: dict): tuple(bool, str)
      + can_build_hotel(prop: dict, player: dict): tuple(bool, str)
      + build_house(prop: dict, player: dict): bool
      + build_hotel(prop: dict, player: dict): bool
      + sell_house(prop: dict, player: dict): bool
      + sell_hotel(prop: dict, player: dict): bool
      + mortgage_property(prop: dict, player: dict): bool
      + unmortgage_property(prop: dict, player: dict): bool
      + calculate_space_rent(prop: dict, player: dict): int
    }
    note "Property data stored as dict(str, dict)" as N1
    GameLogic::properties .. N1
    
    note "Player data stored as list(dict)" as N2
    GameLogic::players .. N2
    class GameBoard {
      + add_message(msg: str)
      + update_ownership(properties: dict)
      + property_clicked(pos: tuple): int
      + get_property_position(index: int): tuple(int, int)
    }
    @enduml

Activity Diagram: Handling Clicks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shows the logical flow within the `handle_click` method.

.. uml::

    @startuml
    start
    if (is_active?) then (yes)
      if (game.selected_property is set?) then (yes)
        :Check if click hit any UI button;
        if (UI button clicked?) then (yes)
          :Get clicked_action;
          if (action == "close"?) then (yes)
            :game.selected_property = None;
            stop
          else (no)
            :Perform action (build, sell, mortgage);
            :Update GameLogic state;
            :Update GameBoard visuals/messages;
            if (Player sold last property?) then (yes)
              :deactivate();
            endif
            stop
          endif
        else (no)
          :Check if click is inside UI panel area;
          if (Click inside UI panel?) then (yes)
            :Ignore click (stay in UI);
            stop
          else (no)
            note right: Click outside UI, treat as property click below
          endif
        endif
      else (no)
        note right: No property selected, check board click
      endif
      :property_pos_index = board.property_clicked(pos);
      if (property_pos_index exists?) then (yes)
        :prop_data = logic.properties(index);
        if (prop_data.owner == current_player?) then (yes)
          :game.selected_property = prop_data;
          stop
        else (no)
          :Ignore click (not player's property);
          stop
        endif
      else (no)
        :Ignore click (not on property);
        stop
      endif
    else (no)
      :Ignore click (mode not active);
      stop
    endif
    @enduml

Sequence Diagrams
~~~~~~~~~~~~~~~~~

**Activating Development and Selecting a Property (Human Player)**

Shows how a human player enters development mode and selects a property.

.. uml::
   :caption: Sequence Diagram: Activate and Select Property

   actor Player
   participant "dev_mode:DevelopmentMode" as DevMode
   participant "game:Game" as Game
   participant "logic:GameLogic" as Logic
   participant "board:GameBoard" as Board

   activate DevMode
   note over DevMode: Assume activation check passed (lap count >= 1, owns properties)
   DevMode -> Game : selected_property = None
   Game --> DevMode
   DevMode -> Game : board.add_message("Click a property to develop")
   Game --> DevMode

   Player -> DevMode : handle_click(pos)
   DevMode -> Board : property_clicked(pos)
   Board --> DevMode : space_index or None
   opt space_index is not None
        DevMode -> Logic : properties(index)
        Logic --> DevMode : prop_data
        alt prop_data.owner == current_player
          DevMode -> Game : selected_property = prop_data
          Game --> DevMode
          DevMode -> Game : state = "DEVELOPMENT"
          Game --> DevMode
        else
          DevMode -> Board : add_message("Owned by {owner}")
          Board --> DevMode
        end
   end
   DevMode --> Player : return False
   deactivate DevMode

**Performing an Action (e.g., Build House via UI)**

Illustrates the process when a player clicks a button in the development UI.

.. uml::
   :caption: Sequence Diagram: Build House Action (UI Click)

   actor Player
   participant "dev_mode:DevelopmentMode" as DevMode
   participant "game:Game" as Game
   participant "logic:GameLogic" as Logic
   participant "board:GameBoard" as Board
   participant "sound_manager:Sound_Manager" as SM

   note over Player, SM: Precondition: Development mode active, property selected
   Player -> DevMode : handle_click(pos_on_build_house_button)
   activate DevMode
   DevMode -> Logic : can_build_house(selected_property, current_player)
   Logic --> DevMode : can_build, reason
   alt can_build
     DevMode -> Logic : build_house(selected_property, current_player)
     Logic --> DevMode : success
     opt success
       DevMode -> SM : play_sound("build")
       SM --> DevMode
       DevMode -> Board : add_message("Built house on {property}")
       Board --> DevMode
     end
   else cannot build
     DevMode -> Board : add_message(reason)
     Board --> DevMode
   end
   DevMode -> Board : update_ownership(logic.properties)
   Board --> DevMode
   DevMode --> Player : return False
   deactivate DevMode

**Checking if AI Can Develop**

Shows the sequence for the `can_develop_ai` check.

.. uml::
    :caption: Sequence Diagram: can_develop_ai Check

    participant "Caller" as Caller
    participant "DevMode" as DevMode
    participant "Game" as Game
    participant "Logic" as Logic

    Caller -> DevMode : can_develop_ai(player_dict)
    activate DevMode
    
    DevMode -> Game : get lap_count(player_name)
    Game --> DevMode : lap_count
    
    alt lap_count < 1
        DevMode --> Caller : return False
    else has completed lap
        DevMode -> Logic : get properties
        Logic --> DevMode : all_properties
        
        DevMode -> DevMode : Filter owned_properties
        
        alt no owned properties
            DevMode --> Caller : return False
        else has properties
            loop for each property
                DevMode -> Logic : can_build_house(prop, player)
                Logic --> DevMode : can_build_house result
                
                DevMode -> Logic : can_build_hotel(prop, player)
                Logic --> DevMode : can_build_hotel result
                
                DevMode -> DevMode : Check other conditions
                
                alt can perform any action
                    DevMode --> Caller : return True
                    break
                end
            end
            
            DevMode --> Caller : return False
        end
    end
    
    deactivate DevMode

**Mortgage/Unmortgage Action (UI Click)**

Illustrates handling the mortgage button click in the UI.

.. uml::
    :caption: Sequence Diagram: Mortgage/Unmortgage Action

    actor Player
    participant "DevMode" as DevMode
    participant "Game" as Game
    participant "Logic" as Logic
    participant "Board" as Board

    Player -> DevMode : handle_click(pos)
    activate DevMode
    
    DevMode -> DevMode : Check button collision
    
    alt mortgage button clicked
        DevMode -> Game : get is_mortgaged
        Game --> DevMode : mortgage status
        
        alt property is mortgaged
            DevMode -> Logic : unmortgage_property(prop, player)
            Logic --> DevMode : result
            
            alt successful
                DevMode -> Board : add_message("Unmortgaged")
            end
        else not mortgaged
            DevMode -> Logic : mortgage_property(prop, player)
            Logic --> DevMode : result
            
            alt successful
                DevMode -> Board : add_message("Mortgaged")
            end
        end
        
        alt action successful
            DevMode -> Board : update_ownership()
        end
    end
    
    DevMode --> Player : return False
    deactivate DevMode

Key Classes Overview
--------------------

 **DevelopmentMode**: Orchestrates the development phase. It activates/deactivates the mode, handles player input (clicks on board/UI, keyboard shortcuts for humans), draws visual cues (stars on properties) and the detailed property management UI panel. It relies heavily on `GameLogic` to validate actions and update game state, and on `GameBoard` for visual updates and user messages. It interacts with the main `Game` object to access shared resources and state like the selected property.