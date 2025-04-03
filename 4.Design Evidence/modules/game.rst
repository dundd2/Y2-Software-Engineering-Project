Game Module
===========

.. automodule:: src.Game
   :members:
   :undoc-members:
   :show-inheritance:

The Game module serves as the central coordinator of the Property Tycoon game, managing the overall game flow, state transitions, and integration of various subsystems. It initializes all necessary components, processes player actions through the game logic system, and ensures proper synchronization between the user interface, board representation, and game rules.

**Core Responsibilities:**

*   **Initialization:** Sets up the Pygame screen, loads assets (backgrounds, board, dice images), initializes fonts, sound, players, board, game logic, card decks, and UI elements (buttons).
*   **State Management:** Controls the main game state (`ROLL`, `BUY`, `AUCTION`, `DEVELOPMENT`, `JAIL_CHOICE`, `CARD_DISPLAY`, `POPUP`, `GAME_OVER`, etc.) and transitions between them based on game events.
*   **Game Loop Coordination:** While the main loop resides in `Main.py`, the `Game` object holds the state and data used by `GameRenderer`, `GameEventHandler`, and `GameActions` within that loop.
*   **Player Management:** Holds the list of `Player` objects, tracks the current player, and synchronizes player data (position, money, status) between the UI representation (`Player` class) and the core logic (`GameLogic`).
*   **Rule Enforcement & Logic Delegation:** Delegates core game rule processing (rent calculation, property transactions, card effects, bankruptcy) to the `GameLogic` instance.
*   **Event Handling (Indirect):** Holds data necessary for `GameEventHandler` to process user input (clicks, keys) relevant to the current game state (e.g., clicking buy/pass buttons, handling auction input).
*   **Rendering Coordination (Indirect):** Holds data necessary for `GameRenderer` to draw the current game state (board, players, UI elements, popups, dice).
*   **Action Execution (Indirect):** Holds data and state for `GameActions` to execute complex game actions (rolling dice, handling turns, buying/auctioning properties, managing development).
*   **UI Display:** Manages the display of popups, card information, notifications, and AI emotion indicators.
*   **Game Mode & Timing:** Manages different game modes (Full, Abridged) and enforces time limits in Abridged mode, including checking for game end conditions.
*   **AI Integration:** Initializes AI controllers within `Player` objects (via `Player.__init__`) and coordinates AI turn execution via `check_and_trigger_ai_turn` and `GameActions`.

Detailed Design
---------------

 Game Class Diagram

Shows the structure of the `Game` class and its primary relationships with other core components.

.. uml::

    @startuml
    class Game {
        + screen : pygame.Surface
        + players : List<Player>
        + board : Board
        + logic : GameLogic
        + pot_luck_deck : CardDeck
        + opportunity_deck : CardDeck
        + state : str  ' e.g., "ROLL", "BUY", "AUCTION"
        + game_mode : str
        + time_limit : int
        + start_time : int
        + game_over : bool
        + current_player_is_ai : bool
        + free_parking_pot : int
        + dice_images : Dict<int, pygame.Surface>
        + last_roll : tuple
        + current_property : Property ' Property being considered/auctioned
        + show_popup : bool
        + popup_message : str
        + show_card : bool
        + current_card : dict
        + game_paused : bool
        + renderer : GameRenderer ' Injected dependency
        + game_actions : GameActions
        + dev_manager : DevelopmentMode
        + emotion_uis : Dict<str, AIEmotionUI>
        ' UI Rects (roll_button, etc.) omitted for brevity
        ' Animation/Timing attributes omitted for brevity

        + __init__(players, game_mode, time_limit, ai_difficulty)
        + add_message(text: str)
        + finish_dice_animation()
        + check_game_over() : dict or None
        + handle_space(current_player: dict) : tuple
        + handle_game_over(winner_name: str)
        + get_jail_choice(player: dict) : str
        + handle_card_action(card: Card, player: dict)
        + show_card_popup(card_type: str, message: str)
        + show_rent_popup(player, owner, property_name, rent_amount)
        + show_tax_popup(player, tax_name, tax_amount)
        + handle_card_draw(player: dict, card_type: str) : str
        + check_one_player_remains() : bool
        + check_time_limit() : bool or dict
        + end_full_game() : dict
        + end_abridged_game() : dict
        + move_player(player: Player, spaces: int) : int
        + wait_for_animations()
        + check_passing_go(player: Player, old_position: int)
        + synchronize_player_positions()
        + synchronize_player_money()
        + synchronize_free_parking_pot()
        + show_exit_confirmation() : bool
        + check_and_trigger_ai_turn(recursion_depth=0) : bool
        + update_ai_mood(ai_player_name: str, is_happy: bool) : bool
        + update_current_player()
        + can_develop(player: dict) : bool
        + handle_turn_end(force_end=False)
        + handle_key(event) ' Primarily delegates to dev_manager or handles popups
    }

    class Player
    class Board
    class GameLogic
    class CardDeck
    class Property
    class Card
    class GameRenderer
    class GameActions
    class DevelopmentMode
    class AIEmotionUI
    class Font_Manager
    class Sound_Manager

    Game "1" *-- "1..*" Player : has
    Game "1" *-- "1" Board : has
    Game "1" *-- "1" GameLogic : uses
    Game "1" *-- "2" CardDeck : has
    Game "1" *-- "1" GameActions : creates/uses
    Game "1" *-- "1" DevelopmentMode : creates/uses
    Game "1" *-- "0..*" AIEmotionUI : creates/uses
    Game "1" o-- GameRenderer : has reference
    note right on link: Dependency Injected
    Game ..> Property : uses (via logic)
    Game ..> Card : uses (via decks/logic)
    Game ..> Font_Manager : uses
    Game ..> Sound_Manager : uses
    Game ..> pygame : uses

    GameActions ..> Game : modifies state
    DevelopmentMode ..> Game : modifies state / reads data
    GameLogic ..> Game : reads state / calls methods (e.g., show_popup)
    Board ..> Player : reads data
    AIEmotionUI ..> Player : reads data
    @enduml

 Game State Diagram

Illustrates the primary states the `Game` object transitions between during gameplay.

.. uml::

    @startuml
    [*] --> Initializing : Game Start
    Initializing --> ROLL : Initialization Complete

    state ActiveGameplay {
        ROLL : Waiting for player to roll dice
        DICE_ANIMATION : Showing dice roll animation
        MOVING : Player token is moving (managed by Player, observed by Game)
        LANDED : Player movement finished, evaluating space
        BUY : Player landed on unowned property, deciding to buy/auction
        AUCTION : Property is being auctioned
        JAIL_CHOICE : Player in jail, choosing action (pay/card/roll)
        CARD_DRAW : Player landed on card space, drawing card
        CARD_DISPLAY : Showing drawn card information
        ACTION_PENDING : Waiting for player action after landing (e.g., pay rent)
        DEVELOPMENT : Player managing properties (building/mortgaging)
        POPUP_DISPLAY : Showing a general notification popup
    }

    ROLL --> DICE_ANIMATION : Player clicks Roll / AI triggers roll
    DICE_ANIMATION --> MOVING : finish_dice_animation() called
    MOVING --> LANDED : Player animation complete (is_animation_complete() is true)

    LANDED --> BUY : Landed on unowned, buyable property (and passed GO)
    LANDED --> AUCTION : Landed on unowned, but chooses not to buy / cannot afford / hasn't passed GO
    LANDED --> JAIL_CHOICE : Landed on "Go to Jail" / Sent by card/doubles
    LANDED --> CARD_DRAW : Landed on Card space
    LANDED --> ACTION_PENDING : Landed on owned property (rent) / Tax / etc.
    LANDED --> ROLL : Landed on neutral space (Free Parking, Just Visiting) / Action completed

    BUY --> AUCTION : Player chooses not to buy / Timeout
    BUY --> ACTION_PENDING : Player buys property (transaction)
    ACTION_PENDING --> ROLL : Action completed (e.g., rent paid)
    ACTION_PENDING --> Bankrupt : Cannot afford action

    AUCTION --> ACTION_PENDING : Auction completes with winner (transaction)
    AUCTION --> ROLL : Auction completes with no winner

    JAIL_CHOICE --> ROLL : Player chooses to roll / Pays fine / Uses card / Stays in jail
    JAIL_CHOICE --> Bankrupt : Cannot pay fine after 3 turns

    CARD_DRAW --> CARD_DISPLAY : Card drawn from deck (via handle_card_draw -> logic -> handle_card_action)
    CARD_DISPLAY --> ACTION_PENDING : Card requires payment/action
    CARD_DISPLAY --> MOVING : Card causes movement
    CARD_DISPLAY --> JAIL_CHOICE : Card sends to jail
    CARD_DISPLAY --> ROLL : Card action complete (simple message/money change)

    ROLL --> DEVELOPMENT : Player chooses to develop properties (if applicable)
    DEVELOPMENT --> ROLL : Player finishes development / AI finishes

    ActiveGameplay --> POPUP_DISPLAY : Notification needed (e.g., passed GO)
    POPUP_DISPLAY --> ActiveGameplay : Popup dismissed

    ActiveGameplay --> GAME_OVER : check_game_over() returns true
    GAME_OVER --> [*]

    note right of DEVELOPMENT : Player can often choose\nto enter DEVELOPMENT\nbefore rolling or after\ncompleting actions,\ndepending on exact rules\nimplemented in Actions/Events.
    @enduml

 Sequence Diagram: Game Initialization (`__init__`)

Shows the setup process when a `Game` object is created.

.. uml::

    @startuml
    participant "Caller" as MainFunc
    participant "Game.__init__" as Init
    participant "pygame" as Pygame
    participant "Font_Manager" as FM
    participant "os" as OS
    participant "GameLogic" as Logic
    participant "Board" as BoardClass
    participant "CardDeck" as DeckClass
    participant "GameActions" as ActionsClass
    participant "DevelopmentMode" as DevModeClass
    participant "AIEmotionUI" as EmotionUIClass
    participant "Player" as PlayerClass

    MainFunc -> Init : Game(players, mode, time_limit, ai_diff)
    activate Init
    Init -> Pygame : display.get_surface() / set_mode()
    Init -> FM : get_font(...)
    Init -> Init : Load background/board images (simplified)
    Init -> Init : Display startup animations (simplified)
    Init -> Init : Set game_mode, time_limit, start_time
    Init -> Init : Initialize lap_count, game_over, etc.
    Init -> Init : Load dice images
    Init -> Logic : GameLogic()
    Logic --> Init : logic instance
    Init -> logic : game = self
    Init -> logic : ai_difficulty = self.ai_difficulty
    Init -> logic : game_start()
    note right: Loads properties etc.
    logic --> Init : success
    Init -> Init : self.players = players
    Init -> BoardClass : Board(self.players)
    BoardClass --> Init : board instance
    Init -> DeckClass : CardDeck(POT_LUCK)
    DeckClass --> Init : pot_luck_deck instance
    Init -> DeckClass : CardDeck(OPPORTUNITY_KNOCKS)
    DeckClass --> Init : opportunity_deck instance
    Init -> board : update_board_positions()
    Init -> board : update_ownership(logic.properties)
    Init -> Init : state = "ROLL"
    Init -> Init : Initialize animation/timing vars
    loop player in players
        Init -> logic : add_player(player.name)
        logic --> Init : success
        Init -> Init : player_colors(player.name) = player.color
    end
    Init -> Init : Create UI button Rects (roll_button, etc.)
    Init -> ActionsClass : GameActions(self)
    ActionsClass --> Init : game_actions instance
    Init -> DevModeClass : DevelopmentMode(self, self.game_actions)
    DevModeClass --> Init : dev_manager instance
    loop player in players
        alt player.is_ai and ai_difficulty == "hard"
            Init -> EmotionUIClass : AIEmotionUI(screen, player, self)
            EmotionUIClass --> Init : emotion_ui instance
            Init -> Init : emotion_uis(player.name) = emotion_ui
        end
    end
    Init -> Init : update_current_player()
    Init --> MainFunc : Game instance
    deactivate Init
    @enduml

 Sequence Diagram: Dice Roll and Landing (`finish_dice_animation`)

Illustrates the core logic after the dice animation completes.

.. uml::

    @startuml
    participant "Game" as GameObj
    participant "GameLogic" as Logic
    participant "Player" as PlayerObj ' UI Player object
    participant "Board" as BoardObj
    participant "GameActions" as Actions
    participant "GameRenderer" as Renderer

    GameObj -> GameObj : finish_dice_animation()
    activate GameObj
    GameObj -> GameObj : dice_animation = False
    GameObj -> GameObj : last_roll = dice_values
    GameObj -> Logic : Get current_player dict
    Logic --> GameObj : current_player
    GameObj -> GameObj : Find corresponding PlayerObj
    GameObj --> GameObj : player_obj

    GameObj -> GameObj : wait_for_animations() ' Ensure previous moves complete
    note right: Ensure previous moves complete

    loop message in Logic.message_queue
        GameObj -> BoardObj : add_message(message)
    end

    alt current_player('in_jail')
        alt dice1 == dice2 ' Rolled doubles
            GameObj -> current_player : in_jail = False
            GameObj -> player_obj : in_jail = False
            GameObj -> BoardObj : add_message("Left jail!")
        else ' Failed doubles
            GameObj -> Actions : handle_jail_turn(current_player)
            GameObj -> GameObj : state = "ROLL"
            GameObj -> Renderer : draw()
            GameObj -> Pygame : display.flip()
            deactivate GameObj
            return
        end
    end

    ' Player moves (handled by Player.update_animation, triggered elsewhere)
    ' Assume player position is updated in PlayerObj and current_player dict
    GameObj -> GameObj : check_passing_go(player_obj, old_position) ' Updates money/message

    GameObj -> BoardObj : update_board_positions()
    GameObj -> BoardObj : update_ownership(Logic.properties)

    alt Landed on Card Space (e.g., pos 3, 18, 34)
        GameObj -> BoardObj : add_message("Landed on Pot Luck")
        GameObj -> GameObj : handle_card_draw(current_player, "POT_LUCK")
        activate GameObj #DarkCyan
            GameObj -> Logic : handle_card_draw(...)
            Logic --> GameObj : result, message
            ' ... Show card popup, execute action ...
            alt result == "moved"
                GameObj -> GameObj : wait_for_animations()
                GameObj -> BoardObj : update_board_positions()
                GameObj -> Renderer : draw()
                GameObj -> Pygame : display.flip()
            end
        deactivate GameObj #DarkCyan
    else Landed on Property Space
        GameObj -> Logic : Get property data for position
        Logic --> GameObj : space_data
        alt space_data('name') == "Go to Jail"
            GameObj -> BoardObj : add_message("Goes to Jail!")
            GameObj -> current_player : in_jail = True, position = 11
            GameObj -> player_obj : in_jail = True, position = 11
            GameObj -> Logic : is_going_to_jail = True
            GameObj -> GameObj : handle_turn_end()
            GameObj -> GameObj : state = "ROLL"
            GameObj -> Renderer : draw()
            GameObj -> Pygame : display.flip()
        else Unowned Property and Can Buy
            alt Logic.completed_circuits < 1
                 GameObj -> BoardObj : add_message("Must pass GO first")
                 GameObj -> GameObj : state = "ROLL"
                 GameObj -> Renderer : draw()
                 GameObj -> Pygame : display.flip()
            else ' Can potentially buy
                 GameObj -> BoardObj : add_message("Landed on...")
                 GameObj -> BoardObj : add_message("Buy for £X?")
                 GameObj -> GameObj : state = "BUY"
                 GameObj -> GameObj : current_property = space_data
                 GameObj -> Renderer : draw()
                 GameObj -> Pygame : display.flip()
                 alt player_obj.is_ai
                     GameObj -> Actions : handle_buy_decision(ai_choice)
                 end
            end
        else Owned Property / Other
            GameObj -> Logic : handle_space(current_player) ' Handles rent, tax etc.
            Logic --> GameObj : result, message
            GameObj -> BoardObj : add_message(message)
            GameObj -> GameObj : state = "ROLL" ' Or ACTION_PENDING if rent etc.
            GameObj -> Renderer : draw()
            GameObj -> Pygame : display.flip()
        end
    else Other Space (GO, Free Parking, Tax)
         GameObj -> Logic : handle_space(current_player)
         Logic --> GameObj : result, message
         GameObj -> BoardObj : add_message(message)
         GameObj -> GameObj : state = "ROLL" ' Or ACTION_PENDING
         GameObj -> Renderer : draw()
         GameObj -> Pygame : display.flip()
    end

    alt not player_obj.is_ai and Logic.completed_circuits >= 1
        GameObj -> GameObj : waiting_for_end_turn = True
        GameObj -> BoardObj : add_message("Click End Turn...")
        opt owned_properties exist
             GameObj -> dev_manager : is_active = True
             GameObj -> BoardObj : add_message("Use Development button...")
        end
    end

    alt player_obj.is_ai and state != "BUY"
        GameObj -> GameObj : update_current_player() ' May trigger next AI turn if state is ROLL
    end

    GameObj -> GameObj : wait_for_animations() ' Final check before returning

    loop message in Logic.message_queue ' Process any new messages
        GameObj -> BoardObj : add_message(message)
    end

    GameObj -> Renderer : draw()
    GameObj -> Pygame : display.flip()
    deactivate GameObj
    @enduml

 Sequence Diagram: Card Draw and Action

Illustrates the flow when a player lands on a card space.

.. uml::

    @startuml
    participant "Caller" as Caller
    participant "Game" as GameObj
    participant "GameLogic" as Logic
    participant "CardDeck" as Deck
    participant "Card" as CardObj
    participant "GameRenderer" as Renderer
    participant "pygame" as Pygame
    participant "Player" as PlayerObj
    participant "Board" as BoardObj

    Caller -> GameObj : handle_card_draw(player_dict, card_type_str)
    activate GameObj
    GameObj -> Logic : handle_card_draw(player_dict, card_type_str)
    activate Logic
    alt card_type_str == "POT_LUCK"
        Logic -> GameObj : pot_luck_deck
        GameObj --> Logic : deck
    else card_type_str == "OPPORTUNITY_KNOCKS"
        Logic -> GameObj : opportunity_deck
        GameObj --> Logic : deck
    end
    Logic -> Deck : draw_card()
    activate Deck
    Deck --> Logic : card_instance
    deactivate Deck
    Logic -> GameObj : handle_card_action(card_instance, player_dict)
    activate GameObj #DarkCyan
        GameObj -> GameObj : show_card = True
        GameObj -> GameObj : current_card = {type: card.type, message: card.text}
        GameObj -> GameObj : current_card_player = player_dict
        GameObj -> Pygame : time.get_ticks()
        Pygame --> GameObj : start_time
        loop Waiting for user input (or timeout)
            GameObj -> Renderer : draw()
            note right: Will show the card popup
            GameObj -> Pygame : display.flip()
            GameObj -> Pygame : event.get()
            alt event is MOUSEBUTTONDOWN or KEYDOWN
                GameObj -> GameObj : show_card = False
                GameObj -> GameObj : current_card = None
                break loop
            end
            GameObj -> Pygame : time.wait(30)
        end loop
        GameObj -> CardObj : action(player_dict, self)
        note right: Card executes its effect
        activate CardObj
            note right: Card logic modifies player_dict, game state (e.g., money, position, jail)
            note right: May call GameObj methods like move_player, add_message, etc.
            CardObj --> GameObj : result (e.g., "moved", "paid", None)
        deactivate CardObj
        GameObj --> Logic : result
    deactivate GameObj #DarkCyan
    Logic --> GameObj : result, message (from card action)
    deactivate Logic

    alt result == "moved"
        GameObj -> GameObj : Find PlayerObj for player_dict
        GameObj --> GameObj : player_obj
        GameObj -> player_obj : start_move((new_position))
        GameObj -> GameObj : wait_for_animations()
        GameObj -> BoardObj : update_board_positions()
        GameObj -> Renderer : draw()
        GameObj -> Pygame : display.flip()
    end
    GameObj --> Caller : result
    note right: Return value from handle_card_draw
    deactivate GameObj
    @enduml

 Sequence Diagram: Time Limit Check (`check_time_limit`)

Focuses on the logic for the Abridged game mode end condition.

.. uml::

    @startuml
    participant "run_game()" as Runner
    participant "Game" as GameObj
    participant "pygame" as Pygame
    participant "Sound_Manager" as SM
    participant "Board" as BoardObj

    Runner -> GameObj : check_time_limit()
    activate GameObj
    opt time_limit is None or start_time is None
        GameObj --> Runner : False
        deactivate GameObj
        return
    end

    GameObj -> Pygame : time.get_ticks()
    Pygame --> GameObj : current_time
    GameObj -> GameObj : Calculate elapsed_time_ms (accounting for pauses)
    GameObj -> GameObj : time_limit_ms = self.time_limit * 1000

    alt elapsed_time_ms < time_limit_ms
        note right: Time not up yet
        GameObj -> GameObj : Calculate remaining_seconds
        opt remaining_seconds <= 60
            opt remaining_seconds <= 10 and interval passed
                GameObj -> SM : play_sound("countdown")
                GameObj -> BoardObj : add_message("Time remaining...")
            else remaining_seconds <= 30 and interval passed
                GameObj -> SM : play_sound("countdown")
                GameObj -> BoardObj : add_message("Time remaining...")
            else remaining_seconds == 60 and not warned
                GameObj -> SM : play_sound("jail")
                note right: Warning sound
                GameObj -> BoardObj : add_message("WARNING: 1 minute remaining!")
                GameObj -> GameObj : _one_minute_warning_played = True
            end
        end
        GameObj --> Runner : False
    else
        note right: Time limit reached or exceeded
        opt not self.time_limit_reached
            GameObj -> BoardObj : add_message("TIME'S UP!")
            GameObj -> SM : play_sound("game_over")
            GameObj -> GameObj : time_limit_reached = True
            GameObj -> GameObj : final_lap = current lap counts for active players
            opt state == "AUCTION"
                 GameObj -> Logic : Cancel current auction
            end
            GameObj -> GameObj : state = "ROLL"
            note right: Ensure game continues for final lap
        end

        GameObj -> GameObj : Check if all active players completed final lap
        alt All players completed lap
            GameObj -> GameObj : game_over = True
            GameObj --> Runner : True ' Signal to end game via end_abridged_game()
        else Not all completed
            GameObj --> Runner : False ' Continue playing final lap
        end
    end
    deactivate GameObj
    @enduml

 Sequence Diagram: Turn End and AI Trigger (`handle_turn_end`, `check_and_trigger_ai_turn`)

Shows how the turn ends and potentially triggers the next AI player's turn.

.. uml::

    @startuml
    participant "Caller" as Caller <<e.g., Action, Event Handler>>
    participant "Game" as GameObj
    participant "GameLogic" as Logic
    participant "Player" as PlayerObj
    participant "GameActions" as Actions

    Caller -> GameObj : handle_turn_end()
    activate GameObj
    GameObj -> Logic : Get current_player dict
    Logic --> GameObj : current_player
    opt development_mode == True
        GameObj -> GameObj : development_mode = False
    end
    GameObj -> GameObj : state = "ROLL"
    GameObj -> Logic : current_player_index = (index + 1) % num_players
    GameObj -> GameObj : update_current_player()
    activate GameObj #DarkGreen
        note over GameObj: Sets current_player_is_ai, updates board message
        GameObj -> GameObj : check_and_trigger_ai_turn(0)
        activate GameObj #DarkBlue
            opt state != "ROLL" and state != "DEVELOPMENT"
                 GameObj --> GameObj : False
                 deactivate GameObj #DarkBlue
                 return
            end
            GameObj -> Logic : Get current_player dict
            Logic --> GameObj : current_player
            opt player exited or bankrupt
                 GameObj -> Logic : Advance player index
                 GameObj -> GameObj : check_and_trigger_ai_turn(depth + 1)
                 note right: Recursive call
                 GameObj --> GameObj : result
                 deactivate GameObj #DarkBlue
                 return result
            end
            GameObj -> GameObj : Find PlayerObj for current_player
            GameObj --> GameObj : player_obj
            opt player_obj.is_ai
                 GameObj -> GameObj : current_player_is_ai = True
                 GameObj -> Pygame : time.delay(500)
                 opt player_obj.in_jail
                     GameObj -> Actions : handle_jail_turn(current_player)
                     Actions --> GameObj : jail_result
                     opt not jail_result
                         note right: Stays in jail
                         GameObj -> GameObj : handle_turn_end()
                         note right: End turn again
                         GameObj --> GameObj : result
                         deactivate GameObj #DarkBlue
                         return result
                     end
                 end
                 opt state == "ROLL"
                     GameObj -> Actions : play_turn() ' This handles AI roll/actions
                     Actions --> GameObj : turn_result
                     GameObj --> GameObj : turn_result
                 else
                     GameObj --> GameObj : True ' AI handled (e.g., development)
                 end
                 deactivate GameObj #DarkBlue
                 return result
            else ' Human player
                 GameObj -> GameObj : current_player_is_ai = False
                 GameObj --> GameObj : False ' Waiting for human input
                 deactivate GameObj #DarkBlue
                 return False
            end
        deactivate GameObj #DarkBlue
    deactivate GameObj #DarkGreen
    GameObj --> Caller
    deactivate GameObj
    @enduml

 Sequence Diagram: Exit Confirmation

Illustrates the user interaction flow for the exit confirmation dialog.

.. uml::

    @startuml
    participant "GameEventHandler" as Handler
    participant "Game" as GameObj
    participant "GameRenderer" as Renderer
    participant "pygame" as Pygame
    participant "User" as User

    Handler -> GameObj : show_exit_confirmation()
    activate GameObj
    GameObj -> GameObj : Backup screen state (screen.copy())
    GameObj -> GameObj : Draw overlay, dialog background, text
    GameObj -> GameObj : Draw Yes/No buttons (initial state)
    GameObj -> Pygame : display.flip()

    loop waiting
        GameObj -> Pygame : event.get()
        alt event is MOUSEMOTION
            GameObj -> Pygame : mouse.get_pos()
            Pygame --> GameObj : mouse_pos
            GameObj -> GameObj : Check collision with Yes/No buttons
            GameObj -> GameObj : Redraw dialog with hover states if changed
            GameObj -> Pygame : display.flip()
        else event is MOUSEBUTTONDOWN
            User -> GameObj : Click
            GameObj -> Pygame : event.pos
            Pygame --> GameObj : click_pos
            alt Yes button clicked
                GameObj -> GameObj : confirm_exit = True
                GameObj -> GameObj : waiting = False
            else No button clicked
                GameObj -> GameObj : confirm_exit = False
                GameObj -> GameObj : waiting = False
            end
        else event is KEYDOWN
             User -> GameObj : Press Key
             alt key is 'Y'
                 GameObj -> GameObj : confirm_exit = True
                 GameObj -> GameObj : waiting = False
             else key is 'N' or ESCAPE
                 GameObj -> GameObj : confirm_exit = False
                 GameObj -> GameObj : waiting = False
             end
        else event is QUIT
            GameObj -> Pygame : quit()
            GameObj -> sys : exit()
            User <-- GameObj : Program terminates
            break
        end
        GameObj -> Pygame : time.wait(5)
        note right: Small delay to prevent high CPU usage
    end loop

    GameObj -> GameObj : Restore screen backup (blit backup surface)
    GameObj -> Renderer : draw()
    note right: Redraw original game screen
    GameObj -> Pygame : display.flip()
    GameObj --> Handler : confirm_exit (True or False)
    deactivate GameObj
    @enduml

 Sequence Diagram: Player Data Synchronization (Conceptual)

Shows the concept behind methods like `synchronize_player_positions` and `synchronize_player_money`.

.. uml::

    @startuml
    participant "Game" as GameObj
    participant "Player (UI)" as PlayerObj
    participant "GameLogic" as Logic

    GameObj -> GameObj : synchronize_player_positions()
    activate GameObj
    loop for player_obj in self.players
        opt player_obj is active (not bankrupt/exited)
            GameObj -> Logic : Find corresponding player_dict by name
            Logic --> GameObj : player_dict or None
            alt player_dict found
                alt player_obj.position != player_dict('position')
                    note right: Logic to reconcile position based on AI status or proximity
                    GameObj -> player_obj : position = reconciled_position
                    GameObj -> player_dict : position = reconciled_position
                end
            else Player not in Logic (Warning)
            end
        end
    end loop
    deactivate GameObj

    GameObj -> GameObj : synchronize_player_money()
    activate GameObj
    loop for player_obj in self.players
         GameObj -> Logic : Find corresponding player_dict by name
         Logic --> GameObj : player_dict or None
         alt player_dict found
             alt player_obj.money != player_dict('money')
                 GameObj -> player_obj : money = player_dict('money')
             end
         end
    end loop
    deactivate GameObj
    @enduml

 Sequence Diagram: AI Mood Update

Illustrates how the `update_ai_mood` method interacts with AI player controllers.

.. uml::

    @startuml
    participant "Caller" as Caller <<e.g., GameActions>>
    participant "Game" as GameObj
    participant "AIPlayer" as AIP <<Player>>
    participant "AIController" as AIC <<HardAIPlayer>>
    note right of AIC: Assumes Hard AI for mood

    Caller -> GameObj : update_ai_mood(ai_player_name, is_happy)
    activate GameObj
    GameObj -> GameObj : Find AI Player object by name (optional, not used in current code)
    GameObj -> GameObj : any_updated = False
    loop for player in self.players
        alt player.is_ai and hasattr(player, 'ai_controller') and hasattr(controller, 'update_mood')
            GameObj -> AIP : ai_controller
            AIP --> GameObj : controller_instance (AIC)
            GameObj -> AIC : update_mood(is_happy)
            activate AIC
            note right of AIC: Controller updates internal mood state
            AIC --> GameObj
            deactivate AIC
            GameObj -> GameObj : any_updated = True
        end
    end loop
    alt any_updated
        GameObj -> Board : add_message("All AI players are getting happier/angrier!")
        GameObj --> Caller : True
    else
        GameObj --> Caller : False
    end
    deactivate GameObj
    @enduml