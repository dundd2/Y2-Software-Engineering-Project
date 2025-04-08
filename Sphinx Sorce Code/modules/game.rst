Game Module
===========

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

.. automodule:: src.Game
   :members:
   :undoc-members:
   :show-inheritance:
   
Detailed Design
---------------

.. uml::
   :caption: Game Class Diagram

   @startuml
   skinparam classAttributeIconSize 0
   skinparam class {
       BackgroundColor White
       BorderColor Black
       ArrowColor Black
   }

   class Game {
       + screen: pygame.Surface
       + players: List<Player>
       + board: Board
       + logic: GameLogic
       + pot_luck_deck: CardDeck
       + opportunity_deck: CardDeck
       + state: str
       + game_mode: str
       + time_limit: int
       + start_time: int
       + game_over: bool
       + current_player_is_ai: bool
       + free_parking_pot: int
       + dice_images: Dict<int, pygame.Surface>
       + last_roll: tuple
       + current_property: Property
       + show_popup: bool
       + popup_message: str
       + show_card: bool
       + current_card: dict
       + game_paused: bool
       + renderer: GameRenderer
       + game_actions: GameActions
       + dev_manager: DevelopmentMode
       + emotion_uis: Dict<str, AIEmotionUI>
       
       + __init__(players: List, game_mode: str, time_limit: int, ai_difficulty: str)
       + add_message(text: str): void
       + finish_dice_animation(): void
       + check_game_over(): dict
       + handle_space(current_player: dict): tuple
       + handle_game_over(winner_name: str): void
       + get_jail_choice(player: dict): str
       + handle_card_action(card: Card, player: dict): void
       + show_card_popup(card_type: str, message: str): void
       + show_rent_popup(player: Player, owner: Player, property_name: str, rent_amount: int): void
       + show_tax_popup(player: Player, tax_name: str, tax_amount: int): void
       + handle_card_draw(player: dict, card_type: str): str
       + check_one_player_remains(): bool
       + check_time_limit(): bool
       + end_full_game(): dict
       + end_abridged_game(): dict
       + move_player(player: Player, spaces: int): int
       + wait_for_animations(): void
       + check_passing_go(player: Player, old_position: int): void
       + synchronize_player_positions(): void
       + synchronize_player_money(): void
       + synchronize_free_parking_pot(): void
       + show_exit_confirmation(): bool
       + check_and_trigger_ai_turn(recursion_depth: int): bool
       + update_ai_mood(ai_player_name: str, is_happy: bool): bool
       + update_current_player(): void
       + can_develop(player: dict): bool
       + handle_turn_end(force_end: bool): void
       + handle_key(event: Event): void
   }

   class Player {
   }

   class Board {
   }

   class GameLogic {
   }

   class CardDeck {
   }

   class Property {
   }

   class Card {
   }

   class GameRenderer {
   }

   class GameActions {
   }

   class DevelopmentMode {
   }

   class AIEmotionUI {
   }

   class Font_Manager {
   }

   class Sound_Manager {
   }

   Game "1" *-- "1..*" Player : has
   Game "1" *-- "1" Board : has
   Game "1" *-- "1" GameLogic : uses
   Game "1" *-- "2" CardDeck : has
   Game "1" *-- "1" GameActions : creates/uses
   Game "1" *-- "1" DevelopmentMode : creates/uses
   Game "1" *-- "0..*" AIEmotionUI : creates/uses
   Game "1" o-- "1" GameRenderer : has reference >
   note right of Game : Dependency Injected

   Game ..> Property : uses
   Game ..> Card : uses
   Game ..> Font_Manager : uses
   Game ..> Sound_Manager : uses
   Game ..> "pygame" : uses

   GameActions ..> Game : modifies state
   DevelopmentMode ..> Game : modifies state
   GameLogic ..> Game : reads state
   Board ..> Player : reads data
   AIEmotionUI ..> Player : reads data
   @enduml

.. uml::
   :caption: Game State Diagram

   @startuml
   skinparam state {
       BackgroundColor White
       BorderColor Black
       ArrowColor Black
   }

   [*] --> Initializing : Game Start
   Initializing --> ROLL : Initialization Complete

   state ActiveGameplay {
       state ROLL : Waiting for player to roll dice
       state DICE_ANIMATION : Showing dice roll animation
       state MOVING : Player token is moving
       state LANDED : Player movement finished
       state BUY : Player deciding to buy/auction
       state AUCTION : Property being auctioned
       state JAIL_CHOICE : Player choosing jail action
       state CARD_DRAW : Player drawing card
       state CARD_DISPLAY : Showing card info
       state ACTION_PENDING : Waiting for player action
       state DEVELOPMENT : Managing properties
       state POPUP_DISPLAY : Showing notification
   }

   ROLL --> DICE_ANIMATION : Player/AI rolls
   DICE_ANIMATION --> MOVING : Animation done
   MOVING --> LANDED : Movement complete

   LANDED --> BUY : Unowned property
   LANDED --> AUCTION : Cannot/won't buy
   LANDED --> JAIL_CHOICE : Go to Jail
   LANDED --> CARD_DRAW : Card space
   LANDED --> ACTION_PENDING : Owned/Tax space
   LANDED --> ROLL : Neutral space

   BUY --> AUCTION : Pass/Timeout
   BUY --> ACTION_PENDING : Purchase
   ACTION_PENDING --> ROLL : Complete
   ACTION_PENDING --> Bankrupt : Cannot pay

   AUCTION --> ACTION_PENDING : Winner buys
   AUCTION --> ROLL : No winner

   JAIL_CHOICE --> ROLL : Action taken
   JAIL_CHOICE --> Bankrupt : Cannot pay

   CARD_DRAW --> CARD_DISPLAY : Draw card
   CARD_DISPLAY --> ACTION_PENDING : Payment needed
   CARD_DISPLAY --> MOVING : Movement card
   CARD_DISPLAY --> JAIL_CHOICE : Jail card
   CARD_DISPLAY --> ROLL : Simple card

   ROLL --> DEVELOPMENT : Develop properties
   DEVELOPMENT --> ROLL : Complete

   ActiveGameplay --> POPUP_DISPLAY : Show message
   POPUP_DISPLAY --> ActiveGameplay : Dismiss

   ActiveGameplay --> GAME_OVER : Game ends
   GAME_OVER --> [*]

   note right of DEVELOPMENT
     Player can develop before
     rolling or after actions
   end note
   @enduml

.. uml::
   :caption: Game Initialization Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Caller" as MainFunc
   participant "Game.__init__" as Init
   participant "pygame" as Pygame
   participant "Font_Manager" as FM
   participant "GameLogic" as Logic
   participant "Board" as BoardClass
   participant "CardDeck" as DeckClass
   participant "GameActions" as ActionsClass
   participant "DevelopmentMode" as DevModeClass

   activate MainFunc
   MainFunc -> Init : Game(players, mode, time_limit, ai_diff)
   activate Init

   Init -> Pygame : display.get_surface()
   activate Pygame
   Pygame --> Init : surface
   deactivate Pygame

   Init -> FM : get_font()
   activate FM
   FM --> Init : font
   deactivate FM

   Init -> Init : Load assets
   Init -> Init : Set game parameters

   Init -> Logic : GameLogic()
   activate Logic
   Logic --> Init : logic instance
   Init -> Logic : game = self
   Init -> Logic : ai_difficulty = ai_diff
   Init -> Logic : game_start()
   Logic --> Init : success
   deactivate Logic

   Init -> BoardClass : Board(players)
   activate BoardClass
   BoardClass --> Init : board instance
   deactivate BoardClass

   Init -> DeckClass : CardDeck("POT_LUCK")
   activate DeckClass
   DeckClass --> Init : pot_luck_deck
   deactivate DeckClass

   Init -> DeckClass : CardDeck("OPPORTUNITY_KNOCKS")
   activate DeckClass
   DeckClass --> Init : opportunity_deck
   deactivate DeckClass

   Init -> Init : Initialize UI elements

   Init -> ActionsClass : GameActions(self)
   activate ActionsClass
   ActionsClass --> Init : game_actions
   deactivate ActionsClass

   Init -> DevModeClass : DevelopmentMode(self, game_actions)
   activate DevModeClass
   DevModeClass --> Init : dev_manager
   deactivate DevModeClass

   Init --> MainFunc : game instance
   deactivate Init
   deactivate MainFunc
   @enduml

.. uml::
   :caption: Dice Roll and Landing Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Game" as Game
   participant "GameLogic" as Logic
   participant "Player" as PlayerObj
   participant "Board" as BoardObj
   participant "Sound" as SM

   activate Game
   Game -> Game : finish_dice_animation()
   
   Game -> Logic : get_current_player()
   activate Logic
   Logic --> Game : player_data
   deactivate Logic
   
   Game -> PlayerObj : move(dice_sum)
   activate PlayerObj
   PlayerObj -> BoardObj : update_position()
   activate BoardObj
   BoardObj --> PlayerObj : success
   deactivate BoardObj
   PlayerObj --> Game : new_position
   deactivate PlayerObj
   
   Game -> Game : check_passing_go(player, old_pos)
   activate Game
   alt Passed GO
       Game -> BoardObj : add_message("PASSED GO!")
       activate BoardObj
       BoardObj --> Game
       deactivate BoardObj
       Game -> SM : play_sound("collect")
       activate SM
       SM --> Game
       deactivate SM
   end
   deactivate Game
   
   Game -> Game : handle_space(player)
   activate Game
   Game -> Logic : get_space_type()
   activate Logic
   Logic --> Game : space_type
   deactivate Logic
   
   alt Property Space
       Game -> Game : handle_property()
   else Card Space
       Game -> Game : handle_card_draw()
   else Tax Space
       Game -> Game : handle_tax()
   end
   deactivate Game
   
   deactivate Game
   @enduml

.. uml::
   :caption: Card Draw and Action Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Game" as Game
   participant "CardDeck" as Deck
   participant "GameLogic" as Logic
   participant "Board" as BoardObj
   participant "Sound" as SM

   activate Game
   Game -> Game : handle_card_draw(player, card_type)
   
   Game -> Deck : draw_card()
   activate Deck
   Deck --> Game : card_data
   deactivate Deck
   
   Game -> Game : show_card_popup(card_type, message)
   activate Game
   Game -> SM : play_sound("card_draw")
   activate SM
   SM --> Game
   deactivate SM
   deactivate Game
   
   Game -> Game : handle_card_action(card_data, player)
   activate Game
   
   alt Move Card
       Game -> Game : move_player()
   else Money Card
       Game -> Logic : update_player_money()
       activate Logic
       Logic --> Game
       deactivate Logic
   else Jail Card
       Game -> Logic : send_to_jail()
       activate Logic
       Logic --> Game
       deactivate Logic
   end
   
   Game -> BoardObj : add_message(card_result)
   activate BoardObj
   BoardObj --> Game
   deactivate BoardObj
   
   deactivate Game
   deactivate Game
   @enduml

.. uml::
   :caption: Time Limit Check Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Game" as Game
   participant "GameLogic" as Logic
   participant "Board" as BoardObj

   activate Game
   Game -> Game : check_time_limit()
   
   Game -> Game : get_elapsed_time()
   
   alt Time Expired
       Game -> Logic : get_player_rankings()
       activate Logic
       Logic --> Game : rankings
       deactivate Logic
       
       Game -> Game : end_abridged_game()
       activate Game
       Game -> BoardObj : add_message("Time's up!")
       activate BoardObj
       BoardObj --> Game
       deactivate BoardObj
       Game --> Game : winner_data
       deactivate Game
       
       Game -> Game : handle_game_over()
   end
   
   deactivate Game
   @enduml

.. uml::
   :caption: Turn End and AI Trigger Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Game" as Game
   participant "GameLogic" as Logic
   participant "GameActions" as Actions
   participant "Board" as BoardObj

   activate Game
   Game -> Game : handle_turn_end()
   
   Game -> Logic : update_current_player()
   activate Logic
   Logic --> Game : next_player
   deactivate Logic
   
   Game -> Game : check_and_trigger_ai_turn()
   activate Game
   
   alt Current Player is AI
       Game -> Actions : handle_ai_turn()
       activate Actions
       Actions -> Logic : process_ai_decision()
       activate Logic
       Logic --> Actions : decision
       deactivate Logic
       Actions --> Game : result
       deactivate Actions
   end
   
   Game -> BoardObj : update_board_positions()
   activate BoardObj
   BoardObj --> Game
   deactivate BoardObj
   
   deactivate Game
   deactivate Game
   @enduml

.. uml::
   :caption: Exit Confirmation Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Game" as Game
   participant "UI" as UI
   participant "Sound" as SM

   activate Game
   Game -> Game : show_exit_confirmation()
   
   Game -> UI : create_confirmation_dialog()
   activate UI
   UI --> Game : dialog
   deactivate UI
   
   Game -> SM : play_sound("popup")
   activate SM
   SM --> Game
   deactivate SM
   
   alt User Confirms
       Game -> Game : handle_game_over()
       Game --> Game : true
   else User Cancels
       Game --> Game : false
   end
   
   deactivate Game
   @enduml

.. uml::
   :caption: Player Data Synchronization Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Game" as Game
   participant "GameLogic" as Logic
   participant "Board" as BoardObj
   participant "Player" as PlayerObj

   activate Game
   Game -> Game : synchronize_player_data()
   
   Game -> Logic : get_player_states()
   activate Logic
   Logic --> Game : states
   deactivate Logic
   
   loop for each player
       Game -> PlayerObj : update_position()
       activate PlayerObj
       PlayerObj --> Game
       deactivate PlayerObj
       
       Game -> PlayerObj : update_money()
       activate PlayerObj
       PlayerObj --> Game
       deactivate PlayerObj
   end
   
   Game -> BoardObj : update_board_positions()
   activate BoardObj
   BoardObj --> Game
   deactivate BoardObj
   
   Game -> BoardObj : update_ownership()
   activate BoardObj
   BoardObj --> Game
   deactivate BoardObj
   
   deactivate Game
   @enduml

.. uml::
   :caption: AI Mood Update Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Game" as Game
   participant "AIEmotionUI" as EmotionUI
   participant "Sound" as SM

   activate Game
   Game -> Game : update_ai_mood(player_name, is_happy)
   
   alt Has Emotion UI
       Game -> EmotionUI : update_emotion(is_happy)
       activate EmotionUI
       EmotionUI --> Game
       deactivate EmotionUI
       
       Game -> SM : play_sound(mood_sound)
       activate SM
       SM --> Game
       deactivate SM
   end
   
   deactivate Game
   @enduml