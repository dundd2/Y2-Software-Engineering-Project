Game Event Handler Module
=========================

This module defines the `GameEventHandler` class, responsible for capturing and processing all user inputs (keyboard, mouse clicks, mouse movement) during the main game loop. It acts as a central dispatcher, interpreting events based on the current game state and delegating actions to other game components like `GameActions`, `GameLogic`, `DevelopmentManager`, and the main `Game` object.

High-Level Design
-----------------

Dependency Diagram
~~~~~~~~~~~~~~~~~~

Visualizes the primary dependencies of the `GameEventHandler`.

.. uml::
   :caption: GameEventHandler Dependencies

   package "GameEventHandler Module" {
     (GameEventHandler)
   }

   package "Game Core" {
     (Game)
     (GameActions)
     (GameLogic) 
     (DevelopmentManager) 
     (Board) 
     (Renderer) 
     (Player) 
     (AIEmotionUI) 
   }

   package "Data Structures" {
      (Cards) # For CardType enum
   }

   package "Utilities" {
      (Sound_Manager)
   }

   package "External Libraries" {
     (pygame)
     (sys)
   }

   (GameEventHandler) ..> (Game) : uses
   (GameEventHandler) ..> (GameActions) : uses
   (GameEventHandler) ..> (Cards) : uses CardType
   (GameEventHandler) ..> (Sound_Manager) : uses
   (GameEventHandler) ..> (pygame) : uses
   (GameEventHandler) ..> (sys) : uses

   ' Indirect dependencies via Game object
   (GameEventHandler) ..> (GameLogic) : uses
   (GameEventHandler) ..> (DevelopmentManager) : uses
   (GameEventHandler) ..> (Board) : uses
   (GameEventHandler) ..> (Renderer) : uses
   (GameEventHandler) ..> (Player) : uses
   (GameEventHandler) ..> (AIEmotionUI) : uses

Simplified State Handling
~~~~~~~~~~~~~~~~~~~~~~~~~

Shows the main game states the `GameEventHandler` explicitly checks and how input handling differs.

.. uml::
   :caption: Simplified State Handling in GameEventHandler

   [*] --> IDLE : Game Start

   state "Input Handling" as Handling {
     IDLE : Awaiting Input
     ROLL : Handle Roll/Quit/Develop/Pause Click/Key
     BUY : Handle Yes/No Click/Key
     AUCTION : Handle Bid/Pass Click/Key, Numeric Input
     DEVELOPMENT : Handle DevManager Click/Key, Complete Button
     POPUP_SHOWN : Handle Click/Key to dismiss
     CARD_SHOWN : Handle Click/Key to dismiss
     GAME_OVER : Input Ignored
   }

   IDLE --> Handling : Event Occurs
   Handling --> Handling : Process Event (State may change via GameActions/GameLogic)
   Handling --> GAME_OVER : Game Over Condition Met

   note right of Handling
     The handler reacts differently
     based on `self.game.state`,
     `self.game.development_mode`,
     `self.game.show_popup`, etc.
     State transitions are often
     triggered by calls to
     `self.game_actions`.
   end note


Detailed Design
---------------

Class Diagram
~~~~~~~~~~~~~

.. uml::
   :caption: GameEventHandler Class Diagram

   class GameEventHandler {
     - game: Game
     - game_actions: GameActions
     + handle_input(): any
     + handle_click(pos: tuple): any
     + handle_motion(pos: tuple): bool
     + handle_key(event: pygame.Event): any
     # handle_auction_input(event: pygame.Event)
     # _process_auction_bid(current_bidder: dict)
     # handle_auction_click(pos: tuple): bool
   }

   GameEventHandler o--> Game
   GameEventHandler o--> GameActions

Activity Diagrams
~~~~~~~~~~~~~~~~~

**Overall Click Handling Flow (`handle_click`)**

Provides a high-level view of the decision-making process within `handle_click`.

.. uml::
    :caption: Activity Diagram: handle_click Logic Flow

    @startuml
    start
    if (game.game_over?) then (yes)
      stop
    endif

    if (DevManager active and Complete button clicked?) then (yes)
      :Deactivate DevManager;
      :Set state to ROLL;
      :Add message;
      stop
    endif

    if (DevManager active and state not AUCTION/BUY?) then (yes)
      :dev_result = DevManager.handle_click(pos);
      if (dev_result indicates game over?) then (yes)
        :return dev_result;
        stop
      else (no)
        note right: Continue (might fall through to state checks)
      endif
    endif

    if (AI Emotion UI clicked?) then (yes)
      :EmotionUI.handle_click(pos);
      stop
    endif

    if (Popup shown and clicked?) then (yes)
      :game.show_popup = False;
      stop
    endif

    if (Card shown and clicked?) then (yes)
      :game.show_card = False;
      stop
    endif

    if (Development Mode active?) then (yes)
      :dev_result = DevManager.handle_click(pos);
       if (dev_result is not None?) then (yes)
         :return dev_result;
         stop
       else (no)
         note right: Continue (might fall through to state checks)
       endif
    endif

    partition "State-Specific Handling" {
      if (game.state == ROLL?) then (yes)
        if (Human Player?) then (yes)
          if (Develop button clicked?) then (yes)
            :Activate DevManager;
            stop
          elseif (Roll button clicked?) then (yes)
            :game_actions.play_turn();
            stop
          elseif (Pause button clicked?) then (yes)
            :Toggle Pause;
            stop
          elseif (Quit button clicked?) then (yes)
            :Handle Voluntary Exit;
            ' May lead to game over or next turn
            stop
          else (no)
            note right: No relevant button clicked
          endif
        else (AI Player)
          note right: Click ignored for AI in ROLL state
        endif
      elseif (game.state == BUY?) then (yes)
        if (Yes button clicked?) then (yes)
          :game_actions.handle_buy_decision(True);
          stop
        elseif (No button clicked?) then (yes)
          :game_actions.handle_buy_decision(False);
          stop
        else (no)
          ' Click ignored
        endif
      elseif (game.state == AUCTION?) then (yes)
        :handle_auction_click(pos);
        ' May lead to state change after delay
        stop
      else (other state)
        ' Click ignored
      endif
    }
    stop
    @enduml

Sequence Diagrams
~~~~~~~~~~~~~~~~~

**Main Input Loop Dispatch**

.. uml::
   :caption: Sequence Diagram: Input Handling Dispatch

   @startuml
   participant "pygame_loop" as PyLoop
   participant "handler:GameEventHandler" as Handler
   participant "game:Game" as Game
   participant "game_actions:GameActions" as Actions

   PyLoop -> Handler : handle_input()
   activate Handler
   loop for event in pygame.event.get()
     alt event.type == QUIT
       Handler -> pygame : quit()
       Handler -> sys : exit()
     alt event.type == MOUSEBUTTONDOWN
       Handler -> Handler : handle_click(event.pos)
       activate Handler
       ' ... click handling logic (see Activity Diagram) ...
       Handler --> Handler : result
       deactivate Handler
       opt result indicates game over
         Handler --> PyLoop : "game_over" or winner dict
       end
     alt event.type == MOUSEMOTION
       Handler -> Handler : handle_motion(event.pos)
       activate Handler
       ' ... motion handling logic ...
       Handler --> Handler
       deactivate Handler
     alt event.type == KEYDOWN
       Handler -> Handler : handle_key(event)
       activate Handler
       ' ... key handling logic ...
       Handler --> Handler : result
       deactivate Handler
       opt result indicates game over
         Handler --> PyLoop : "game_over" or winner dict
       end
     end
   end loop
   Handler --> PyLoop : None (or game over result)
   deactivate Handler
   @enduml

**Click Handling (ROLL State)**

.. uml::
   :caption: Sequence Diagram - Handle Click (Normal Turn)

   actor Player
   participant "handler:GameEventHandler" as Handler
   participant "game:Game" as Game
   participant "development:DevelopmentMode" as DevMan
   participant "actions:GameActions" as Actions
   participant "logic:GameLogic" as Logic
   participant "player:Player" as PlayerUI
   participant "board:GameBoard" as Board

   Player -> Handler : handle_click(pos)
   activate Handler
   Handler -> Game : state == "ROLL"
   Handler -> Game : current_player (logic)
   Handler -> Game : player_obj (UI)
   opt player_obj is Human
     alt pos collides game.develop_button
       Handler -> Game : check owned_properties
       opt owned_properties exist
         Handler -> Game : development_mode = True
         Handler -> DevMan : activate(current_player)
         Handler -> Game : board.add_message(...)
         Handler --> Handler : return False
       end
     else pos collides game.roll_button
       Handler -> Game : check not player.is_moving
       opt not moving
         Handler -> Game : development_mode = False
         Handler -> DevMan : deactivate()
         Handler -> Actions : play_turn()
         Handler --> Handler : return False
       end
     end
   end
   Handler --> Player : return None
   deactivate Handler

**Click Handling (BUY State)**

.. uml::
   :caption: Sequence Diagram: Click Handling (BUY State)

   participant "handler:GameEventHandler" as Handler
   participant "game:Game" as Game
   participant "game_actions:GameActions" as Actions
   participant "renderer:Renderer" as Renderer

   Handler -> Handler : handle_click(pos)
   activate Handler
   Handler -> Game : check game.state == "BUY"
   Handler -> Game : check game.current_property is not None
   Handler -> Game : get current_player (logic)
   opt player in jail
     Handler -> Game : board.add_message(...)
     Handler -> Game : state = "ROLL"
     Handler -> Renderer : draw()
     Handler -> pygame.display : flip()
     Handler --> Handler : return False
   end
   alt pos collides game.yes_button
     Handler -> Actions : handle_buy_decision(True)
     Handler -> Game : dev_manager.deactivate()
     Handler -> Renderer : draw()
     Handler -> pygame.display : flip()
     Handler --> Handler : return False
   else pos collides game.no_button
     Handler -> Actions : handle_buy_decision(False)
     Handler -> Game : dev_manager.deactivate()
     Handler -> Renderer : draw()
     Handler -> pygame.display : flip()
     Handler --> Handler : return False
   end
   Handler --> Handler : return False ' Default if no button hit
   deactivate Handler

**Auction Click Handling**

.. uml::
   :caption: Sequence Diagram: Auction Click Handling

   participant "handler:GameEventHandler" as Handler
   participant "game:Game" as Game
   participant "logic:GameLogic" as Logic
   participant "sound_manager:Sound_Manager" as SM

   Handler -> Handler : handle_auction_click(pos)
   activate Handler
   Handler -> Logic : get current_auction data
   opt auction invalid or completed or no active players
     Handler -> Game : state = "ROLL"
     Handler --> Handler : return True
   end
   Handler -> Logic : get current_bidder
   Handler -> Game : find current_bidder_obj (UI)
   opt bidder is AI or exited
     Handler -> Logic : add bidder to passed_players
     Handler -> Logic : move_to_next_bidder()
     Handler --> Handler : return False
   end

   alt pos collides game.auction_buttons('bid')
     Handler -> Handler : _process_auction_bid(current_bidder)
     activate Handler
     Handler -> Logic : process_auction_bid(bidder, amount)
     opt success
       Handler -> Game : auction_bid_amount = ""
       Handler -> SM : play_sound("auction_bid")
     end
     Handler -> Game : board.add_message(message)
     Handler --> Handler
     deactivate Handler
   else pos collides game.auction_buttons('pass')
     Handler -> Logic : process_auction_pass(current_bidder)
     Handler -> Game : board.add_message(message)
   end

   Handler -> Logic : check_auction_end()
   opt result_message == "auction_completed"
     Handler -> Logic : get auction winner/property/bid
     Handler -> Game : board.add_message(winner_message or no_bid_message)
     opt winner exists
        Handler -> SM : play_sound("auction_win")
     end
     Handler -> Logic : current_auction = None
     Handler -> Game : auction_end_time = ticks()
     Handler -> Game : auction_completed = True
     Handler -> Game : board.update_ownership(...)
     Handler --> Handler : return False ' Delay before state change
   else
     Handler --> Handler : return False ' Auction continues
   end
   deactivate Handler

**Key Handling (ROLL State)**

Illustrates the primary key presses handled when the game state is `ROLL`.

.. uml::
    :caption: Sequence Diagram: Key Handling (ROLL State)

    participant "handler:GameEventHandler" as Handler
    participant "game:Game" as Game
    participant "game_actions:GameActions" as Actions
    participant "board:Board" as Board

    Handler -> Handler : handle_key(event)
    activate Handler
    Handler -> Game : check game.state == "ROLL"
    opt Human Player
        alt event.key in KEY_ROLL
            opt Abridged Mode and Paused
                Handler -> Board : add_message("Game is paused...")
                Handler --> Handler : return False
            else
                Handler -> Actions : play_turn()
                Handler --> Handler : return result ' May be game over
            end
        else event.key == K_q
            Handler -> Actions : show_exit_confirmation()
            opt confirmed
                Handler -> Actions : handle_voluntary_exit(...)
                ' ... check game over, potentially trigger AI ...
                Handler --> Handler : return result ' May be game over
            else
                Handler --> Handler : return False
            end
        else event.key == K_p (Abridged Mode)
            Handler -> Game : toggle game_paused
            Handler -> Board : add_message(...)
            Handler --> Handler : return False
        else event.key == K_t (Abridged Mode)
            Handler -> Actions : show_time_stats()
            Handler --> Handler : return False
        else event.key in Arrow Keys
            Handler -> Board : update_offset(dx, dy)
            Handler -> Board : camera.handle_camera_controls(...)
            Handler --> Handler : return None
        end
    else AI Player
        ' Key ignored for AI in ROLL state (except maybe camera)
        opt event.key in Arrow Keys
            Handler -> Board : update_offset(dx, dy)
            Handler -> Board : camera.handle_camera_controls(...)
            Handler --> Handler : return None
        end
    end
    Handler --> Handler : return None ' Default if key not handled
    deactivate Handler

**Key Handling (AUCTION State)**

.. uml::
   :caption: Sequence Diagram - Handle Auction Input

   actor Player
   participant "handler:GameEventHandler" as Handler
   participant "game:Game" as Game
   participant "actions:GameActions" as Actions
   participant "logic:GameLogic" as Logic
   participant "board:GameBoard" as Board
   participant "sound:Sound_Manager" as SM

   Player -> Handler : handle_key(event)
   activate Handler
   Handler -> Game : state == "AUCTION"
   Handler -> Game : current_auction (via logic)
   opt auction exists
     alt event.key in (0-9)
       Handler -> Game : auction_bid_amount += key
       Handler -> Game : renderer.draw()
     else event.key == RETURN
       Handler -> Handler : _process_auction_bid()
       activate Handler
       Handler -> Logic : process_auction_bid(...)
       Logic --> Handler : success, message
       opt success
         Handler -> SM : play_sound("auction_bid")
       end
       Handler -> Board : add_message(message)
       Handler -> Game : renderer.draw()
       deactivate Handler
     else event.key == SPACE
       Handler -> Logic : process_auction_pass()
       Logic --> Handler : success, message
       Handler -> Board : add_message(message)
       Handler -> Game : renderer.draw()
     end
   end
   Handler --> Player : return None
   deactivate Handler


Key Methods Overview
--------------------

*   **handle_input()**: The main event loop processor. Iterates through Pygame events and calls specific handlers (`handle_click`, `handle_motion`, `handle_key`) or handles QUIT events directly. Returns game over status if detected.
*   **handle_click(pos)**: Processes left mouse clicks. Behavior depends heavily on `game.state` (ROLL, BUY, AUCTION), `game.development_mode`, `game.show_popup`, `game.show_card`, and which UI element (buttons, AI mood UI) is clicked. Delegates actions to `GameActions`, `DevelopmentManager`, or `handle_auction_click`.
*   **handle_motion(pos)**: Processes mouse movement, primarily to update hover states for buttons and AI mood UI elements.
*   **handle_key(event)**: Processes keyboard presses. Behavior depends on `game.state`, active popups/cards, and development mode. Handles rolling dice, buying/passing, auction input, quitting, pausing, camera movement, and development actions. Delegates actions to `GameActions`, `DevelopmentManager`, or `handle_auction_input`.
*   **handle_auction_input(event)**: Specifically handles keyboard input during an auction (numeric keys for bid amount, Enter to submit, Esc to pass, Backspace). Calls `_process_auction_bid`.
*   **_process_auction_bid(current_bidder)**: Validates and submits the entered bid amount to `GameLogic`.
*   **handle_auction_click(pos)**: Specifically handles mouse clicks during an auction (Bid button, Pass button). Calls `_process_auction_bid` or `GameLogic.process_auction_pass`. Checks for auction completion.

API Documentation
-----------------

.. automodule:: src.GameEventHandler
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members: _process_auction_bid