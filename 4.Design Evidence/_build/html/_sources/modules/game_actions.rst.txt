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

 GameActions Class Diagram

Shows the `GameActions` class and its primary collaborators.

.. uml::

    class GameActions {
        - game : Game
        + __init__(game: Game)
        + play_turn() : bool
        + handle_buy_decision(wants_to_buy: bool)
        + start_auction(property_data: dict)
        + handle_jail_turn(player: dict) : bool
        + handle_voluntary_exit(player_name: str, final_assets: int) : bool or dict
        + calculate_player_assets(player: dict) : int
        + handle_ai_turn(ai_player: dict) : dict or None
        + handle_bankruptcy(player: dict) : bool
        + add_to_free_parking(amount: int)
        + collect_free_parking(player: dict) : bool
        + handle_fine_payment(player: dict, amount: int, reason: str) : bool
        + show_time_stats()
        + show_exit_confirmation() : bool
        + check_one_player_remains() : bool
        + check_game_over() : bool
        + check_and_trigger_ai_turn()
        + end_full_game() : dict
        + end_abridged_game() : dict
    }

    note bottom of GameActions
      Methods ending with '_confirmation', '_remains',
      '_game_over', etc. delegate to the game object
    end note

    class Game {
        + logic : GameLogic
        + players : List<Player>
        + board : Board
        + renderer : GameRenderer
        + state : str
        + current_property : dict
        + dice_values : tuple
        + free_parking_pot : int
        + game_over : bool
        + dice_animation : bool
        + current_player_is_ai : bool
        + update_current_player()
        + move_player(player: Player, steps: int)
        + wait_for_animations()
        + check_game_over() : bool
        + get_jail_choice(player: dict) : str
        + synchronize_free_parking_pot()
        + show_exit_confirmation() : bool
        + check_one_player_remains() : bool
        + check_and_trigger_ai_turn()
        + end_full_game() : dict
        + end_abridged_game() : dict
    }

    class GameLogic {
        + players : List<dict>
        + properties : Dict<str, dict>
        + current_player_index : int
        + free_parking_fund : int
        + completed_circuits : Dict<str, int>
        + jail_free_cards : Dict<str, int>
        + current_auction : dict or None
        + ai_player : AIPlayer
        + play_turn() : tuple or None
        + auction_property(position: int) : str
        + remove_player(player_name: str, voluntary: bool) : bool
        + process_auction_bid(bidder: dict, amount: int) : tuple(bool, str)
        + process_auction_pass(player: dict) : tuple(bool, str)
        + check_auction_end() : str or None
        + get_ai_auction_bid(player: dict, property: dict, current_bid: int) : int or None
    }

    note right of GameLogic::players
      Player data dictionaries
    end note
    
    note right of GameLogic::properties
      Property data dictionaries
    end note
    
    note right of GameLogic::ai_player
      Reference to AI logic
    end note

    class Player {
        + name : str
        + is_ai : bool
        + is_moving : bool
        + in_jail : bool
        + stay_in_jail : bool
        + bankrupt : bool
        + use_jail_card() : str or None
        + handle_voluntary_exit()
    }

    class Board {
        + add_message(message: str)
        + update_ownership(properties: dict)
        + update_board_positions()
    }

    class GameRenderer {
        + draw()
    }

    interface AIPlayer {
       + should_buy_property(property: dict, money: int, owned: list) : bool
       + get_ai_auction_bid(player: dict, property: dict, current_bid: int) : int or None
    }

    class Sound_Manager {
        + play_sound(sound_name: str)
    }

    GameActions o-- Game : uses
    GameActions ..> GameLogic : uses via game.logic
    GameActions ..> Player : uses via game.players
    GameActions ..> Board : uses via game.board
    GameActions ..> GameRenderer : uses via game.renderer
    GameActions ..> Sound_Manager : uses
    GameActions ..> AIPlayer : uses via game.logic.ai_player
    GameActions ..> pygame : uses for events, time

 Activity Diagram: Player Turn Flow

This diagram shows the possible paths and decisions within a single player's turn, managed by `GameActions`.

.. uml::

    start
    if (Player in Jail?) then (yes)
        :Handle Jail Turn (handle_jail_turn);
        if (Left Jail?) then (yes)
            :Roll Dice (play_turn);
            goto ProcessRoll
        else (no)
           if (Chose to Stay?) then (yes)
              :End Turn;
              stop
           else (no)
              :Roll Dice (play_turn);
              if (Rolled Doubles?) then (yes)
                 :Leave Jail;
                 goto ProcessRoll
              else (no)
                 :End Turn;
                 stop
              endif
           endif
        endif
    else (no)
        :Roll Dice (play_turn);
    endif

    :ProcessRoll;
    :Move Player Animation (game.move_player);
    :Wait for Animation (game.wait_for_animations);
    :Update Board Positions (game.board.update_board_positions);
    if (Passed Go?) then (yes)
      :Collect £200 (handled in game logic);
      :Display Message (game.board.add_message);
    endif
    :Land on Square (handled in game logic);

    if (Landed on Ownable Property?) then (yes)
      if (Property Owned?) then (yes)
        if (Owned by Another Player?) then (yes)
          :Pay Rent (handled in game logic);
          if (Bankrupt?) then (yes)
            :Handle Bankruptcy (handle_bankruptcy);
            :End Turn;
            stop
          endif
        else (no, owned by self)
          note right: Do nothing specific here
        endif
      else (no, unowned)
        if (Can Afford?) then (yes)
           if (Is AI?) then (yes)
              :AI Decides Buy/Pass (handle_ai_turn);
           else (no)
              :Player Decides Buy/Pass (UI interaction);
           endif
           :Handle Buy Decision (handle_buy_decision);
           if (Auction Started?) then (yes)
              :Enter Auction State;
              goto HandleAuction
           endif
        else (no)
           :Start Auction (start_auction);
           :Enter Auction State;
           goto HandleAuction
        endif
      endif
    else if (Landed on Card Square?) then (yes)
        :Draw Card (handled in game logic);
        :Execute Card Action (handled in game logic);
         if (Bankrupt?) then (yes)
            :Handle Bankruptcy (handle_bankruptcy);
            :End Turn;
            stop
         endif
    else if (Landed on Tax Square?) then (yes)
        :Pay Tax (handle_fine_payment);
         if (Bankrupt?) then (yes)
            :Handle Bankruptcy (handle_bankruptcy);
            :End Turn;
            stop
         endif
    else if (Landed on Go To Jail?) then (yes)
        :Go To Jail (handled in game logic);
    else if (Landed on Free Parking?) then (yes)
        :Collect Free Parking (collect_free_parking);
    else (Other squares like GO, Just Visiting)
        note right: Do nothing specific here
    endif

    :HandleAuction;
    if (Auction Active?) then (yes)
       :Process Auction Bids/Passes (handle_ai_turn / UI interaction);
       if (Auction Ended?) then (yes)
          :Update Ownership (game.board.update_ownership);
          :Return to Roll State;
       else (no)
          :Wait for Next Bidder;
          stop ' Auction continues in next iteration/event
       endif
    endif

    if (Rolled Doubles and not in Jail?) then (yes)
        :Roll Again;
        repeat while (Rolled Doubles?) is (yes) not (3 times)
    else (no)
       :End Turn;
       stop
    endif

 Sequence Diagram: `play_turn` (Human Player, Normal Roll)

Illustrates the sequence for a human player rolling the dice outside of jail.

.. uml::

    participant "UI/EventHandler" as UI
    participant "GameActions" as Actions
    participant "Game" as GameObj
    participant "GameLogic" as Logic
    participant "Player" as PlayerObj
    participant "Board" as BoardObj
    participant "Sound_Manager" as SM

    UI -> Actions : play_turn()
    activate Actions
    Actions -> GameObj : Check game_over, dice_animation, player.is_moving
    GameObj --> Actions : false
    Actions -> GameObj : logic.players(current_player_index)
    GameObj --> Actions : current_player_data
    Actions -> GameObj : players (find Player object)
    GameObj --> Actions : player_obj
    Actions -> GameObj : update_current_player()
    GameObj --> Actions
    Actions -> PlayerObj : Check in_jail
    PlayerObj --> Actions : false
    Actions -> GameObj : state
    GameObj --> Actions : "ROLL"
    Actions -> GameObj : dice_animation = True
    GameObj --> Actions
    Actions -> SM : play_sound("dice_roll")
    SM --> Actions
    Actions -> Logic : play_turn()
    Logic --> Actions : dice1, dice2
    Actions -> GameObj : dice_values = (dice1, dice2)
    GameObj --> Actions
    Actions -> GameObj : move_player(player_obj, steps)
    GameObj --> Actions
    Actions -> GameObj : wait_for_animations()
    GameObj --> Actions
    Actions -> BoardObj : update_board_positions()
    BoardObj --> Actions
    opt Passed Go
        Actions -> BoardObj : add_message("PASSED GO!")
        BoardObj --> Actions
        Actions -> SM : play_sound("collect_money")
        SM --> Actions
    end
    Actions -> BoardObj : add_message(f"{name} rolled {d1+d2}")
    BoardObj --> Actions
    opt Rolled Doubles
        Actions -> BoardObj : add_message("Doubles! Roll again!")
        BoardObj --> Actions
    end
    Actions -> GameObj : renderer.draw()
    GameObj --> Actions
    note right: Game state might change here based on landing square (handled by Logic)
    Actions --> UI
    deactivate Actions

 Sequence Diagram: `handle_buy_decision` (Player Buys)

Shows the flow when a player decides to buy a property.

.. uml::

    participant "UI/EventHandler or AI" as Initiator
    participant "GameActions" as Actions
    participant "Game" as GameObj
    participant "GameLogic" as Logic
    participant "Board" as BoardObj
    participant "Sound_Manager" as SM

    Initiator -> Actions : handle_buy_decision(wants_to_buy=True)
    activate Actions
    Actions -> GameObj : logic.players(current_player_index)
    GameObj --> Actions : current_player_data
    Actions -> GameObj : current_property
    GameObj --> Actions : property_data
    alt player_money >= property_price
        Actions -> current_player_data : money -= price
        Actions -> property_data : owner = player_name
        Actions -> Logic : properties(pos).owner = player_name ' Update global property
        Logic --> Actions
        Actions -> BoardObj : add_message(f"{name} bought {prop_name}...")
        BoardObj --> Actions
        Actions -> SM : play_sound("buy_property")
        SM --> Actions
        Actions -> GameObj : state = "ROLL" ' Assuming no auction was pending
        GameObj --> Actions
        Actions -> BoardObj : update_ownership(logic.properties)
        BoardObj --> Actions
        Actions -> GameObj : renderer.draw()
        GameObj --> Actions
    else Not enough money
        Actions -> BoardObj : add_message("Not enough money...")
        BoardObj --> Actions
        Actions -> Actions : start_auction(property_data)
        activate Actions
        ' ... Auction sequence starts ...
        Actions --> Actions
        deactivate Actions
    end
    Actions --> Initiator
    deactivate Actions

 Sequence Diagram: `start_auction`

Details the process of initiating a property auction.

.. uml::

    participant "GameActions" as Actions
    participant "Game" as GameObj
    participant "GameLogic" as Logic
    participant "Board" as BoardObj

    Actions -> Actions : start_auction(property_data)
    activate Actions
    Actions -> Logic : Check if any player completed circuit
    Logic --> Actions : any_eligible
    opt not any_eligible
        Actions -> BoardObj : add_message("No eligible players...")
        BoardObj --> Actions
        Actions -> GameObj : state = "ROLL"
        GameObj --> Actions
        Actions --> Actions : return
        deactivate Actions
    end
    Actions -> GameObj : Check if any player.is_moving
    GameObj --> Actions : any_moving
    opt any_moving
        Actions -> GameObj : pending_auction_property = property_data
        GameObj --> Actions
        Actions -> GameObj : waiting_for_animation = True
        GameObj --> Actions
        Actions --> Actions : return
        deactivate Actions
    end
    Actions -> Logic : Get active player count
    Logic --> Actions : count
    opt count <= 1
        Actions -> GameObj : state = "ROLL"
        GameObj --> Actions
        Actions --> Actions : return
        deactivate Actions
    end
    Actions -> Logic : auction_property(property_data('position'))
    Logic --> Actions : result ("auction_in_progress" or error)
    alt result == "auction_in_progress"
        Actions -> GameObj : state = "AUCTION"
        GameObj --> Actions
        Actions -> GameObj : auction_bid_amount = ""
        GameObj --> Actions
        Actions -> BoardObj : add_message("Auction started!")
        BoardObj --> Actions
    else Error starting auction
        Actions -> BoardObj : add_message("Failed to start auction...")
        BoardObj --> Actions
        Actions -> GameObj : state = "ROLL"
        GameObj --> Actions
    end
    Actions -> GameObj : renderer.draw()
    GameObj --> Actions
    Actions --> Actions : (caller)
    deactivate Actions

 Sequence Diagram: `handle_ai_turn` (Auction Decision)

Shows the AI making a decision during an auction.

.. uml::

    participant "Game (run_game loop)" as GameLoop
    participant "GameActions" as Actions
    participant "Game" as GameObj
    participant "GameLogic" as Logic
    participant "AIPlayer" as AIController
    participant "Board" as BoardObj

    GameLoop -> Actions : handle_ai_turn(ai_player_data)
    activate Actions
    Actions -> GameObj : state
    GameObj --> Actions : "AUCTION"
    Actions -> Logic : current_auction
    Logic --> Actions : auction_data
    alt auction_data is not None and AI is current bidder
        Actions -> Logic : get_ai_auction_bid(ai_player_data, prop, current_bid)
        activate Logic
        Logic -> AIController : get_ai_auction_bid(...) ' Delegate to specific AI logic
        AIController --> Logic : bid_amount or None
        Logic --> Actions : bid_amount
        deactivate Logic
        alt bid_amount is valid
            Actions -> BoardObj : add_message(f"AI bids {bid_amount}")
            BoardObj --> Actions
            Actions -> Logic : process_auction_bid(ai_player_data, bid_amount)
            Logic --> Actions : success, message
            Actions -> BoardObj : add_message(message)
            BoardObj --> Actions
        else bid_amount is None
            Actions -> BoardObj : add_message("AI passes")
            BoardObj --> Actions
            Actions -> Logic : process_auction_pass(ai_player_data)
            Logic --> Actions : success, message
            Actions -> BoardObj : add_message(message)
            BoardObj --> Actions
        end
        Actions -> Logic : check_auction_end()
        Logic --> Actions : result
        opt result == "auction_completed"
            Actions -> GameObj : state = "ROLL"
            GameObj --> Actions
            Actions -> BoardObj : update_ownership(Logic.properties)
            BoardObj --> Actions
        end
    end
    Actions --> GameLoop : None
    deactivate Actions