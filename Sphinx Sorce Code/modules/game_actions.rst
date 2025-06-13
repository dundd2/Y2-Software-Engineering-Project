Game Actions Module
===================

The Game Actions module provides a collection of possible actions that players can perform or that occur during the game. It acts as a high-level controller, orchestrating interactions between the player (human or AI), the game state (`Game`), the core rules (`GameLogic`), the visual representation (`Board`, `GameRenderer`), and other services like sound (`Sound_Manager`). It translates user input or AI decisions into concrete game state changes.

The Game Actions module is responsible for:

*   Executing a player's turn (`play_turn`), including dice rolling and movement initiation.
*   Handling the decision process when a player lands on an unowned property (`handle_buy_decision`).
*   Initiating property auctions (`start_auction`).
*   Managing the options and outcomes for a player in jail (`handle_jail_turn`).
*   Processing AI player turns, including purchase and auction decisions (`handle_ai_turn`).
*   Handling player bankruptcy (`handle_bankruptcy`) and voluntary exits (`handle_voluntary_exit`).
*   Managing the Free Parking pot (`add_to_free_parking`, `collect_free_parking`).
*   Handling fines (`handle_fine_payment`).
*   Delegating checks for game end conditions (`check_one_player_remains`, `check_game_over`).
*   Coordinating with the main game loop for AI turn triggers (`check_and_trigger_ai_turn`).
*   Initiating the end-game sequences (`end_full_game`, `end_abridged_game`).

.. automodule:: src.GameActions
   :members:
   :undoc-members:
   :show-inheritance:

Detailed Design
---------------

.. uml::
   :caption: GameActions Class Diagram

   @startuml
   skinparam classAttributeIconSize 0
   skinparam class {
       BackgroundColor White
       BorderColor Black
       ArrowColor Black
   }

   class GameActions {
       - game: Game
       + __init__(game: Game)
       + play_turn(): void
       + handle_buy_decision(wants_to_buy: bool): void
       + start_auction(property_data: Property): void
       + handle_jail_turn(player: Player): void
       + handle_voluntary_exit(player_name: str): void
       + calculate_player_assets(player: Player): int
       + handle_ai_turn(ai_player: Player): void
       + handle_bankruptcy(player: Player): void
       + add_to_free_parking(amount: int): void
       + collect_free_parking(player: Player): void
       + handle_fine_payment(player: Player, amount: int, reason: str): void
       + show_time_stats(): void
       + show_exit_confirmation(): bool
       + check_one_player_remains(): bool
       + check_game_over(): bool
       + check_and_trigger_ai_turn(): void
       + end_full_game(): void
       + end_abridged_game(): void
   }

   class Game {
       + logic: GameLogic
       + players: List<Player>
       + board: Board
       + renderer: GameRenderer
       + state: GameState
       + current_property: Property
       + dice_values: List<int>
       + free_parking_pot: int
       + update_current_player(): void
       + move_player(player: Player, steps: int): void
       + wait_for_animations(): void
       + check_game_over(): bool
   }

   class GameLogic {
       + players: List<Player>
       + properties: List<Property>
       + current_player_index: int
       + play_turn(): Tuple[int, int]
       + auction_property(position: int): bool
       + remove_player(player_name: str, voluntary: bool): void
   }

   class Player {
       + name: str
       + is_ai: bool
       + in_jail: bool
       + bankrupt: bool
   }

   class Board {
       + add_message(message: str): void
       + update_ownership(properties: List<Property>): void
       + update_board_positions(): void
   }

   class GameRenderer {
       + draw(): void
   }

   class Sound_Manager {
       + play_sound(sound_name: str): void
   }

   GameActions o-- "1" Game : contains
   GameActions --> "1" GameLogic : uses
   GameActions --> "*" Player : manages
   GameActions --> "1" Board : updates
   GameActions --> "1" GameRenderer : uses
   GameActions --> "1" Sound_Manager : uses
   @enduml

.. uml::
   :caption: Player Turn Flow Activity Diagram

   @startuml
   skinparam ActivityBackgroundColor White
   skinparam ActivityBorderColor Black
   skinparam ArrowColor Black

   start
   if (Player in Jail?) then (yes)
       :Handle Jail Turn;
       if (Left Jail?) then (yes)
           :Roll Dice;
           note right: Continue turn
       else (no)
           :End Turn;
           stop
       endif
   else (no)
       :Roll Dice;
   endif

   :Move Player;
   :Handle Landing Square;
   
   if (Landed on Property?) then (yes)
     if (Property Owned?) then (yes)
       if (By Other Player?) then (yes)
         :Pay Rent;
         if (Bankrupt?) then (yes)
           :Handle Bankruptcy;
           stop
         endif
       endif
     else (no)
       if (Can Afford?) then (yes)
         if (Is AI?) then (yes)
           :AI Decision;
         else (no)
           :Player Decision;
         endif
         if (Buy?) then (yes)
           :Buy Property;
         else (no)
           :Start Auction;
         endif
       else (no)
         :Start Auction;
       endif
     endif
   else if (Card Square?) then (yes)
     :Draw Card;
     :Execute Action;
   else if (Tax?) then (yes)
     :Pay Tax;
   endif
   
   if (Rolled Doubles?) then (yes)
     :Roll Again;
   else (no)
     :End Turn;
   endif
   
   stop
   @enduml

.. uml::
   :caption: Play Turn Sequence (Human Player, Normal Roll)

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "UI" as UI
   participant "GameActions" as Actions
   participant "Game" as GameObj
   participant "GameLogic" as Logic
   participant "Player" as PlayerObj
   participant "Board" as BoardObj
   participant "Sound" as SM

   activate UI
   UI -> Actions : play_turn()
   activate Actions
   
   Actions -> GameObj : Check game state
   activate GameObj
   GameObj --> Actions : State OK
   deactivate GameObj
   
   Actions -> PlayerObj : Check in_jail
   activate PlayerObj
   PlayerObj --> Actions : Not in jail
   deactivate PlayerObj
   
   Actions -> GameObj : Set dice_animation = true
   Actions -> SM : play_sound("dice_roll")
   activate SM
   deactivate SM
   
   Actions -> Logic : play_turn()
   activate Logic
   Logic --> Actions : dice values
   deactivate Logic
   
   Actions -> GameObj : Set dice_values
   Actions -> GameObj : move_player()
   Actions -> GameObj : wait_for_animations()
   Actions -> BoardObj : update_board_positions()
   
   opt Passed Go
       Actions -> BoardObj : add_message("PASSED GO!")
       Actions -> SM : play_sound("collect_money")
   end
   
   Actions -> BoardObj : add_message("Player rolled X")
   Actions -> GameObj : renderer.draw()
   
   Actions --> UI
   deactivate Actions
   deactivate UI
   @enduml

.. uml::
   :caption: Handle Buy Decision Sequence (Player Buys)

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "Initiator" as Initiator
   participant "GameActions" as Actions
   participant "Game" as GameObj
   participant "GameLogic" as Logic
   participant "Board" as BoardObj
   participant "Sound" as SM

   activate Initiator
   Initiator -> Actions : handle_buy_decision(true)
   activate Actions
   
   Actions -> GameObj : Get current player
   activate GameObj
   GameObj --> Actions : player_data
   deactivate GameObj
   
   Actions -> GameObj : Get current_property
   activate GameObj
   GameObj --> Actions : property_data
   deactivate GameObj
   
   alt Can afford
       Actions -> Actions : Update player money
       Actions -> Actions : Set property owner
       Actions -> Logic : Update property data
       activate Logic
       deactivate Logic
       
       Actions -> BoardObj : add_message("Player bought...")
       activate BoardObj
       deactivate BoardObj
       
       Actions -> SM : play_sound("buy_property")
       activate SM
       deactivate SM
       
       Actions -> GameObj : state = "ROLL"
       Actions -> BoardObj : update_ownership()
       Actions -> GameObj : renderer.draw()
   else Cannot afford
       Actions -> BoardObj : add_message("Not enough money")
       Actions -> Actions : start_auction()
   end
   
   Actions --> Initiator
   deactivate Actions
   deactivate Initiator
   @enduml

.. uml::
   :caption: Start Auction Sequence

   @startuml
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20
   
   participant "GameActions" as Actions
   participant "Game" as GameObj
   participant "GameLogic" as Logic
   participant "Board" as BoardObj

   activate Actions
   
   Actions -> Logic : Check eligible players
   activate Logic
   Logic --> Actions : eligible_status
   deactivate Logic
   
   opt No eligible players
       Actions -> BoardObj : add_message("No eligible players")
       activate BoardObj
       deactivate BoardObj
       Actions -> GameObj : state = "ROLL"
       activate GameObj
       deactivate GameObj
       Actions --> Actions : return
   end
   
   Actions -> GameObj : Check players moving
   activate GameObj
   GameObj --> Actions : movement_status
   deactivate GameObj
   
   opt Players still moving
       Actions -> GameObj : Set pending auction
       activate GameObj
       deactivate GameObj
       Actions --> Actions : return
   end
   
   Actions -> Logic : auction_property()
   activate Logic
   Logic --> Actions : result
   deactivate Logic
   
   alt Auction started
       Actions -> GameObj : state = "AUCTION"
       Actions -> BoardObj : add_message("Auction started!")
   else Failed to start
       Actions -> BoardObj : add_message("Failed to start auction")
       Actions -> GameObj : state = "ROLL"
   end
   
   Actions -> GameObj : renderer.draw()
   
   deactivate Actions
   @enduml