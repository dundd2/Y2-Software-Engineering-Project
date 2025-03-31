Game Event Handler Module
=========================

This module contains the GameEventHandler class that processes and manages user input events, such as mouse clicks and keyboard inputs, in the Property Tycoon game.

Key Features
------------

* **Event Processing**: Management of user input events
* **Mouse Handling**: Processing of mouse clicks, movements, and drag operations
* **Keyboard Handling**: Processing of keyboard inputs for shortcuts and navigation
* **UI Event Delegation**: Routing events to appropriate UI components
* **Game State Event Handling**: Processing events based on current game state
* **Dialog Event Processing**: Handling events for dialog interactions
* **Development Mode Events**: Processing events specific to property development

GameEventHandler Class
----------------------

The GameEventHandler class encapsulates event processing functionality:

.. plantuml::

   @startuml
   
   class GameEventHandler {
     -game : Game
     -ui : UI
     -last_mouse_pos : Tuple
     -clicked_button : String
     -mouse_down : Boolean
     -keyboard_state : Dict
     
     +__init__(game, ui)
     +process_events()
     +handle_mouse_event(event)
     +handle_keyboard_event(event)
     +handle_click(position)
     +handle_game_state_event(event, position)
     +handle_menu_event(event, position)
     +handle_playing_event(event, position)
     +handle_development_event(event, position)
     +handle_dialog_event(event, position)
     +handle_auction_event(event, position)
     +is_button_clicked(button_name, position)
     +get_property_at_position(position)
     +get_ui_element_at_position(position)
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   @enduml

Event Processing Flow
---------------------

The module implements a structured event processing flow:

.. plantuml::

   @startuml
   
   title Event Processing Flow
   
   start
   
   :Receive User Input Event;
   
   if (Event Type?) then (Mouse)
     if (Mouse Event Type?) then (Click)
       :Process Mouse Click;
       if (Game State?) then (Menu)
         :Handle Menu Click;
       else if (Game State?) then (Playing)
         :Handle Game Click;
         if (Click Target?) then (UI Button)
           :Process Button Action;
         else if (Click Target?) then (Game Board)
           :Handle Board Interaction;
         else if (Click Target?) then (Player Info)
           :Show Player Details;
         else if (Click Target?) then (Property Card)
           :Process Property Card Action;
         endif
       else if (Game State?) then (Development)
         :Handle Development Click;
       else if (Game State?) then (Dialog)
         :Handle Dialog Interaction;
       endif
     else if (Mouse Event Type?) then (Movement)
       :Update Hover States;
       :Update Cursor;
     else if (Mouse Event Type?) then (Drag)
       :Process Drag Operation;
     endif
   else if (Event Type?) then (Keyboard)
     if (Game State?) then (Menu)
       :Handle Menu Navigation;
     else if (Game State?) then (Playing)
       :Process Game Keyboard Input;
       if (Key?) then (Escape)
         :Show Pause Menu;
       else if (Key?) then (Space)
         :Roll Dice / End Turn;
       else if (Key?) then (D)
         :Toggle Development Mode;
       else (Other Keys)
         :Process Other Shortcuts;
       endif
     else if (Game State?) then (Dialog)
       :Handle Dialog Keyboard Input;
     endif
   else if (Event Type?) then (Window)
     if (Window Event?) then (Resize)
       :Handle Window Resize;
     else if (Window Event?) then (Close)
       :Handle Game Exit;
     else if (Window Event?) then (Focus)
       :Handle Focus Change;
     endif
   endif
   
   :Return Event Handling Result;
   
   stop
   
   @enduml

Game State Event Handling
-------------------------

The module handles events differently based on the current game state:

.. plantuml::

   @startuml
   
   title Game State Event Handling
   
   state "MENU State" as MENU {
     [*] --> Process_Menu_Click
     Process_Menu_Click --> Handle_Button_Action
     Handle_Button_Action --> Change_Menu
     Handle_Button_Action --> Start_Game
     Handle_Button_Action --> Exit_Game
     Change_Menu --> [*]
     Start_Game --> [*]
     Exit_Game --> [*]
}}}}}}}}}}}}}}}}}
   
   state "PLAYING State" as PLAYING {
     [*] --> Process_Playing_Click
     Process_Playing_Click --> Handle_Action_Button
     Process_Playing_Click --> Handle_Board_Click
     Process_Playing_Click --> Handle_UI_Element
     
     Handle_Action_Button --> Roll_Dice
     Handle_Action_Button --> Buy_Property
     Handle_Action_Button --> End_Turn
     Handle_Action_Button --> Auction_Bid
     
     Handle_Board_Click --> Select_Property
     Handle_Board_Click --> Show_Property_Card
     
     Handle_UI_Element --> Show_Player_Info
     Handle_UI_Element --> Toggle_Development
     Handle_UI_Element --> Initiate_Trade
     
     Roll_Dice --> [*]
     Buy_Property --> [*]
     End_Turn --> [*]
     Auction_Bid --> [*]
     Select_Property --> [*]
     Show_Property_Card --> [*]
     Show_Player_Info --> [*]
     Toggle_Development --> [*]
     Initiate_Trade --> [*]
}}}}}}}}}}}}}}}}}}}}}}
   
   state "DEVELOPMENT State" as DEV {
     [*] --> Process_Development_Click
     Process_Development_Click --> Select_Development_Property
     Process_Development_Click --> Build_House
     Process_Development_Click --> Build_Hotel
     Process_Development_Click --> Sell_House
     Process_Development_Click --> Sell_Hotel
     Process_Development_Click --> Exit_Development_Mode
     
     Select_Development_Property --> [*]
     Build_House --> [*]
     Build_Hotel --> [*]
     Sell_House --> [*]
     Sell_Hotel --> [*]
     Exit_Development_Mode --> [*]
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   state "DIALOG State" as DIALOG {
     [*] --> Process_Dialog_Event
     Process_Dialog_Event --> Dialog_Button_Click
     Process_Dialog_Event --> Dialog_Close
     Dialog_Button_Click --> Dialog_Action
     Dialog_Action --> Dialog_Result
     Dialog_Close --> Dialog_Result
     Dialog_Result --> [*]
}}}}}}}}}}}}}}}}}}}}}
   
   @enduml

UI Event Integration
--------------------

The GameEventHandler integrates with UI components for event processing:

.. plantuml::

   @startuml
   
   title UI Event Integration
   
   class GameEventHandler {
     +handle_click(position)
     +handle_keyboard_event(event)
     +process_events()
}}}}}}}}}}}}}}}}}
   
   class UI {
     -buttons : Dict
     -active_dialogs : List
     -hover_element : Any
     
     +handle_click(position)
     +is_point_in_button(position, button)
     +get_element_at_position(position)
     +handle_button_click(button_name)
     +update_hover_states(position)
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   class Game {
     -event_handler : GameEventHandler
     -ui : UI
     -state : String
     
     +handle_events()
     +handle_action(action_name)
     +set_state(new_state)
}}}}}}}}}}}}}}}}}}}}}
   
   class "UI Elements" as Elements {
     +Button
     +PropertyCard
     +PlayerInfoPanel
     +Dialog
}}}}}}}
   
   GameEventHandler --> UI : delegates UI events to
   Game *-- GameEventHandler
   UI *-- Elements
   GameEventHandler ..> Game : updates game state
   
   @enduml

Mouse Event Processing
----------------------

The module handles various types of mouse events:

.. plantuml::

   @startuml
   
   title Mouse Event Processing
   
   start
   
   :Receive Mouse Event;
   
   if (Event Type?) then (Mouse Down)
     :Record Button State;
     :Record Mouse Position;
     :Update UI Pressed States;
   else if (Event Type?) then (Mouse Up)
     if (Was Mouse Down?) then (Yes)
       :Calculate Click Position;
       :Determine Click Target;
       
       if (Click Target?) then (UI Button)
         :Handle Button Click;
         :Execute Button Action;
       else if (Click Target?) then (Game Board)
         :Get Property at Position;
         :Handle Property Interaction;
       else if (Click Target?) then (Dialog)
         :Process Dialog Interaction;
       else if (Click Target?) then (Player Info)
         :Show Player Details;
       endif
     endif
     
     :Reset Mouse States;
   else if (Event Type?) then (Mouse Motion)
     :Update UI Hover States;
     :Update Cursor Appearance;
     
     if (Dragging?) then (Yes)
       :Process Drag Operation;
     endif
   else if (Event Type?) then (Mouse Wheel)
     :Process Scroll Action;
     
     if (Scroll Target?) then (Property List)
       :Scroll Property List;
     else if (Scroll Target?) then (Card Deck)
       :Scroll Card Deck;
     else if (Scroll Target?) then (Dialog Content)
       :Scroll Dialog Content;
     endif
   endif
   
   :Return Event Processing Result;
   
   stop
   
   @enduml

Keyboard Event Processing
-------------------------

The module processes keyboard inputs for game control:

.. plantuml::

   @startuml
   
   title Keyboard Event Processing
   
   start
   
   :Receive Keyboard Event;
   
   if (Event Type?) then (Key Down)
     :Record Key State;
     
     if (Game State?) then (Menu)
       if (Key?) then (Enter)
         :Activate Selected Item;
       else if (Key?) then (Arrow Keys)
         :Navigate Menu;
       else if (Key?) then (Escape)
         :Exit Current Menu;
       endif
     else if (Game State?) then (Playing)
       if (Key?) then (Space)
         :Roll Dice / End Turn;
       else if (Key?) then (B)
         :Buy Property;
       else if (Key?) then (P)
         :Pass / Auction;
       else if (Key?) then (D)
         :Toggle Development Mode;
       else if (Key?) then (T)
         :Initiate Trade;
       else if (Key?) then (Escape)
         :Show Pause Menu;
       endif
     else if (Game State?) then (Development)
       if (Key?) then (1-4)
         :Build House on Selected Property;
       else if (Key?) then (H)
         :Build Hotel on Selected Property;
       else if (Key?) then (S)
         :Sell House/Hotel;
       else if (Key?) then (Escape)
         :Exit Development Mode;
       endif
     else if (Game State?) then (Dialog)
       if (Key?) then (Enter)
         :Confirm Dialog Action;
       else if (Key?) then (Escape)
         :Cancel Dialog Action;
       endif
     endif
   else if (Event Type?) then (Key Up)
     :Update Key State;
   endif
   
   :Return Event Processing Result;
   
   stop
   
   @enduml

Integration with Game Module
----------------------------

The GameEventHandler module integrates with several other components:

.. plantuml::

   @startuml
   
   title GameEventHandler Integration
   
   class GameEventHandler {
     +process_events()
     +handle_mouse_event()
     +handle_keyboard_event()
}}}}}}}}}}}}}}}}}}}}}}}}
   
   class Game {
     -state : String
     -current_player : Player
     -board : Board
     -ui : UI
     +handle_events()
     +handle_action(action_name)
}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   class Board {
     +get_square_at_coordinates(x, y)
     +highlight_property(property_data)
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   class UI {
     +handle_click(position)
     +update_hover_states(position)
     +get_element_at_position(position)
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   class GameActions {
     +execute_action(action_name, parameters)
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   Game *-- GameEventHandler
   GameEventHandler --> UI : delegates to
   GameEventHandler --> Board : uses
   GameEventHandler --> GameActions : triggers
   
   @enduml

Class Documentation
-----------------

.. automodule:: src.GameEventHandler
   :members:
   :undoc-members:
   :show-inheritance: