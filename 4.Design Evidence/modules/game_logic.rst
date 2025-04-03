Game Logic Module
=================

This module implements the core rules and mechanics of the Property Tycoon game. It manages player turns, property transactions, rent calculation, card draws, auctions, and game state progression according to the established rules. The central class, `GameLogic`, orchestrates these elements.

High-Level Design
-----------------

Use Case Diagram
~~~~~~~~~~~~~~~~

Illustrates the main actions managed or initiated by the Game Logic.

.. uml::
   :caption: Game Logic Use Cases

   left to right direction
   actor Player as HumanPlayer
   actor AI as AIPlayer

   rectangle "Game Logic" {
     (Start Game)
     (Play Turn)
     (Roll Dice)
     (Move Player)
     (Handle Landed Space)
     (Buy Property)
     (Auction Property)
     (Pay Rent)
     (Draw Card)
     (Manage Property)
     (Handle Jail)
     (Check Game Over)
     (Handle Bankruptcy)
   }

   HumanPlayer -- (Play Turn)
   AIPlayer -- (Play Turn)
   (Play Turn) ..> (Roll Dice) : include
   (Roll Dice) ..> (Move Player) : include
   (Move Player) ..> (Handle Landed Space) : include
   (Handle Landed Space) ..> (Buy Property) : extends
   (Handle Landed Space) ..> (Auction Property) : extends
   (Handle Landed Space) ..> (Pay Rent) : extends
   (Handle Landed Space) ..> (Draw Card) : extends
   (Handle Landed Space) ..> (Handle Jail) : extends
   (Play Turn) ..> (Handle Jail) : include
   HumanPlayer -- (Manage Property)
   AIPlayer -- (Manage Property) 
   (Play Turn) ..> (Check Game Over) : include
   (Pay Rent) ..> (Handle Bankruptcy) : extends
   (Draw Card) ..> (Handle Bankruptcy) : extends

Dependency Diagram
~~~~~~~~~~~~~~~~~~

Shows the primary dependencies of the Game Logic module.

.. uml::
   :caption: Game Logic Dependencies

   package "Game Logic Module" {
     (GameLogic)
     (pot_luck_cards)
     (opportunity_knocks_cards)
   }

   package "External Libraries" {
     (pygame)
     (random)
   }

   package "Internal Modules" {
     (Loadexcel) as LE
     (Ai_Player_Logic) as AIPL {
        (EasyAIPlayer)
        (HardAIPlayer)
     }
     (Sound_Manager) as SM
     (Game)
   }

   ' Dependencies
   (GameLogic) ..> (pygame) : uses for timing (auction)
   (GameLogic) ..> (random) : uses extensively
   (GameLogic) ..> LE : uses load_property_data
   (GameLogic) ..> AIPL : uses AIPlayer classes
   (GameLogic) ..> SM : uses for sounds
   (GameLogic) ..> (Game) : uses for UI callbacks (popups, etc.)

Detailed Design
---------------

Class and Data Structures
~~~~~~~~~~~~~~~~~~~~~~~~~

**GameLogic Class**

The core class managing the game state and rules.

.. uml::
   :caption: GameLogic Class Diagram

   class GameLogic {
     + BANK_LIMIT: int = 50000
     + MAX_HOUSES_PER_PROPERTY: int = 4
     + MAX_HOTELS_PER_PROPERTY: int = 1
     + GAME_TOKENS: list
     - players: list<dict>
     note right: Player dictionaries
     - bank_money: int
     - free_parking_fund: int
     - current_player_index: int
     - properties: dict
     note right: Property dictionaries keyed by position
     - is_going_to_jail: bool
     - last_dice_roll: tuple
     - doubles_count: int
     - message_queue: list
     - bankrupted_players: list
     - voluntary_exits: list
     - jail_free_cards: dict
     - completed_circuits: dict
     - available_tokens: list
     - pot_luck_cards: list<dict>
     - opportunity_knocks_cards: list<dict>
     - ai_difficulty: str
     - ai_player: AIPlayer
     note right: Instance of Easy/Hard AI
     - game: Game
     note right: Reference to main Game object for callbacks
     - current_auction: dict
     note right: State for ongoing auction

     + __init__()
     + validate_bank_transaction(amount: int): bool
     + pay_from_bank(player: dict, amount: int): bool
     + pay_to_bank(player: dict, amount: int): bool
     + game_start(): bool
     + add_player(player: any): tuple<bool, str>
     + advance_to_next_player(): dict
     + play_turn(): tuple<int, int>
     + add_message(message: str)
     + handle_space(player: dict): tuple<str, str>
     + handle_jail(player: dict): str
     + try_leave_jail(player: dict, dice1: int, dice2: int): tuple<bool, str>
     + check_game_over(): tuple<bool, any>
     + calculate_space_rent(space: dict, player: dict): int
     + handle_card_draw(player: dict, card_type: str): tuple<str, str>
     + calculate_repair_cost(player: dict, house_cost: int, hotel_cost: int): int
     + check_property_group_completion(player_name: str): bool
     + buy_property(player: dict): bool
     + auction_property(position: str): str
     + process_auction_bid(player: dict, bid_amount: int): tuple<bool, str>
     + process_auction_pass(player: dict): tuple<bool, str>
     + check_auction_end(): str
     + move_to_next_bidder()
     + is_game_over(): bool
     + get_winner(): str
     + remove_player(player_name: str, voluntary: bool): bool
     + auction(property_data: dict)
     + placeBids(player_list: list, property_data: dict): tuple<dict, int>
     + get_ai_bid(player: dict, current_minimum: int, property_data: dict): int
     + get_human_bid(player: dict, current_minimum: int, property_data: dict): int
     + buy_property_after_auction(player: dict, property_data: dict): bool
     + handle_bankruptcy(player: dict): bool
     + can_build_house(property_data: dict, player: dict): tuple<bool, str>
     + can_build_hotel(property_data: dict, player: dict): tuple<bool, str>
     + build_house(property_data: dict, player: dict): bool
     + build_hotel(property_data: dict, player: dict): bool
     + sell_house(property_data: dict, player: dict): bool
     + sell_hotel(property_data: dict, player: dict): bool
     + mortgage_property(property_data: dict, player: dict): bool
     + unmortgage_property(property_data: dict, player: dict): bool
     + handle_rent_payment(landing_player: dict, property_data: dict): bool
     + calculate_house_difference(color_group_properties: list): int
     + handle_ai_turn(player: dict): any
     + process_ai_property_purchase(player: dict, property_data: dict): bool
     + get_ai_auction_bid(player: dict, property_data: dict, current_bid: int): int
     + handle_ai_bankruptcy_prevention(player: dict, amount_needed: int): bool
     + handle_buy_decision(player: dict, decision: str): str
     + handle_birthday_collection(birthday_player: dict): tuple<int, int, int>
     + handle_payment_to_bank(player: dict, amount: int, to_free_parking: bool): tuple<int, int, int>
     + handle_repair_assessment(player: dict, house_cost: int, hotel_cost: int): tuple<int, int, int>
   }

   note right of GameLogic::players
     List contains dictionaries representing players.
     Keys include: name, money, position, is_ai,
     properties (list), token, in_jail, jail_turns,
     bankrupt, exited.
   end note

   note right of GameLogic::properties
     Dictionary contains dictionaries representing properties,
     keyed by board position (string). Keys include: name,
     price, rent, group, owner, houses, house_cost,
     is_mortgaged, type, etc.
   end note

   note right of GameLogic::pot_luck_cards
     List contains dictionaries representing cards.
     Keys: text, action (lambda function).
   end note

   GameLogic *-- "players" : list<dict>
   GameLogic *-- "properties" : dict<str, dict>
   GameLogic *-- "pot_luck_cards" : list<dict>
   GameLogic *-- "opportunity_knocks_cards" : list<dict>
   GameLogic *-- "current_auction" : dict
   GameLogic ..> Ai_Player_Logic.AIPlayer : uses

**Simplified Game State**

Shows the main states the game can be in, focusing on turn progression and auctions.

.. uml::
   :caption: Simplified Game State Diagram

   [*] --> Initializing
   Initializing --> PlayerTurn : Game Setup Complete

   state PlayerTurn {
     [*] --> Roll
     Roll --> Move : Dice Values
     Move --> HandleSpace : Landing
     HandleSpace --> [*] : Complete

     HandleSpace --> Buy : Unowned Property
     HandleSpace --> PayRent : Owned Property
     HandleSpace --> DrawCard : Card Space
     HandleSpace --> Jail : Go To Jail

     Buy --> Auction : Decline Purchase
     Buy --> [*] : Purchase Complete
     Auction --> [*] : Complete

     PayRent --> [*] : Paid
     PayRent --> Bankruptcy : Cannot Pay

     DrawCard --> Move : Movement Card
     DrawCard --> PayBank : Payment Card
     DrawCard --> GetMoney : Receive Money
     DrawCard --> [*] : Effect Complete

     Jail --> Roll : Pay Fine/Use Card
     Jail --> [*] : Stay in Jail
   }

   PlayerTurn --> PlayerTurn : Next Player's Turn
   PlayerTurn --> GameOver : Single Player / Time Limit
   GameOver --> [*]

Activity Diagrams
~~~~~~~~~~~~~~~~~

**Play Turn Flow**

Illustrates the sequence of actions within a single player's turn.

.. uml::
   :caption: Activity Diagram: Play Turn

   @startuml
   start
   :Get Current Player;
   if (Player is Bankrupt or Exited?) then (yes)
     :Advance to Next Player;
     stop
   endif
   if (Player in Jail?) then (yes)
     :Roll Dice;
     :Try Leave Jail;
     if (Left Jail?) then (no)
       :Advance to Next Player;
       stop
     else (yes)
       note right: Continue turn
     endif
   else (no)
     :Roll Dice;
   endif

   :Record Dice Roll;
   if (Rolled Doubles?) then (yes)
     :Increment Doubles Count;
     if (Doubles Count == 3?) then (yes)
       :Go To Jail;
       :Advance to Next Player;
       stop
     endif
   else (no)
     :Reset Doubles Count;
   endif

   :Calculate New Position;
   if (Passed GO?) then (yes)
     :Collect £200;
     :Increment Lap Count;
   endif
   :Update Player Position;
   :Handle Landed Space Action;

   if (Action Result is Bankrupt?) then (yes)
      :Handle Bankruptcy;
      if (Game Over?) then (yes)
        stop
      endif
   endif

   if (Rolled Doubles? AND Not Sent to Jail?) then (yes)
      :Player Takes Another Turn;
      -> Get Current Player;
      note right: Loop back for the same player
   else (no)
      :Advance to Next Player;
   endif

   stop
   @enduml

**Handle Landed Space Flow**

Details the logic when a player lands on a specific board space.

.. uml::
   :caption: Activity Diagram: Handle Landed Space

   @startuml
   start
   :Get Space Data (from properties dict);
   switch (Space Type?)
   case ( Property / Station / Utility )
     if (Owned?) then (yes)
        if (Owner is Current Player?) then (no)
          :Calculate Rent;
          :Pay Rent to Owner;
          if (Cannot Pay?) then (yes)
            :Handle Bankruptcy;
          endif
        else (yes)
          :Landed on Own Property;
        endif
     else (no)
        if (Can be Bought? AND Passed GO?) then (yes)
          :Signal 'Can Buy' state;
          note right: Wait for player/AI decision (Buy/Auction)
        else (no)
          :Do Nothing (e.g., Corner Space);
        endif
     endif

   case ( Tax )
     :Pay Tax Amount to Bank;
     :Show Tax Popup (if UI);

   case ( Pot Luck / Opportunity Knocks )
     :Draw Card;
     :Execute Card Action;
      if (Action causes move?) then (yes)
        :Handle Landed Space (recursive);
      endif
      if (Action causes payment issue?) then (yes)
        :Handle Bankruptcy;
      endif

   case ( Go To Jail )
     :Send Player to Jail;

   case ( Free Parking )
     :Collect Free Parking Fund (if applicable);
     :Show Free Parking Popup (if UI);

   case ( Jail / Just Visiting )
     :Do Nothing;

   case ( GO )
     :Do Nothing (Handled by Pass GO logic);

   endswitch
   stop
   @enduml

**Auction Flow (Simplified)**

Outlines the basic steps of the property auction process using the `current_auction` state.

.. uml::
   :caption: Activity Diagram: Auction Process

   @startuml
    start
    :Initiate Auction (auction_property);
    :Set up current_auction state;
    :Identify Eligible Players;
    if (No Eligible Players?) then (yes)
      :End Auction (Unsold);
      stop
    endif
    :Set Current Bidder Index;
    :Set Minimum Bid;
    :Start Auction Timer;

    repeat
      :Wait for Current Bidder Action (Bid/Pass);
      if (Action is Bid?) then (yes)
        :Process Bid (process_auction_bid);
        if (Bid Valid?) then (yes)
          :Update Highest Bid/Bidder;
          :Update Minimum Bid;
          :Move to Next Bidder (move_to_next_bidder);
        else (no)
          :Inform Player of Invalid Bid;
        endif
      else (Action is Pass?)
        :Process Pass (process_auction_pass);
        :Move to Next Bidder (move_to_next_bidder);
      endif

      :Check Auction End Conditions (check_auction_end);
      partition CheckEnd {
         if (Timeout? OR Only 1 Bidder Left? OR All Passed?) then (yes)
           :Mark Auction Completed;
           break
         endif
      }

    repeat while (Auction Not Completed?) is (true)

    :Finalize Auction;
    if (Highest Bidder Exists?) then (yes)
      :Transfer Money (Player to Bank);
      :Assign Property Ownership;
    else (no)
      :Property Remains Unsold;
    endif
    :Clear current_auction state;
    stop
    @enduml

Sequence Diagrams
~~~~~~~~~~~~~~~~~

**Player Buys Property**

.. uml::
   :caption: Sequence Diagram: Player Buys Property

   @startuml
   actor User/AI
   participant "game:Game" as GameUI
   participant "logic:GameLogic" as Logic
   participant "properties:dict" as Props

   User/AI -> GameUI : Indicate Buy Decision
   GameUI -> Logic : handle_buy_decision(player, "buy")
   activate Logic
   Logic -> Logic : Get player position
   Logic -> Props : Get property_data(position)
   alt Player can afford and property available
     Logic -> Logic : player('money') -= price
     Logic -> Logic : bank_money += price
     Logic -> Props : property_data('owner') = player('name')
     Logic -> Logic : check_property_group_completion(player('name'))
     Logic --> GameUI : return "purchase_completed"
   else Cannot afford or property unavailable
     Logic --> GameUI : return "Error/Auction"
     note right: Or starts auction
   end
   deactivate Logic
   GameUI -> GameUI : Update UI (show ownership)
   @enduml

**Rent Payment**

.. uml::
   :caption: Sequence Diagram: Rent Payment

   @startuml
   participant "landing_player:dict" as Lander
   participant "logic:GameLogic" as Logic
   participant "owning_player:dict" as Owner
   participant "properties:dict" as Props
   participant "game:Game" as GameUI

   Logic -> Logic : handle_space(Lander) 
   note right: Called after move
   activate Logic
   Logic -> Props : Get property_data(Lander('position'))
   Logic -> Logic : calculate_space_rent(property_data, Lander)
   Logic -> Owner : Find owner player dict
   alt Lander can afford rent
     Logic -> Lander : money -= rent
     Logic -> Owner : money += rent
     Logic -> Logic : add_message(...)
     Logic -> GameUI : show_rent_popup(Lander, Owner, ...)
     Logic --> Lander : return None
     note right: Rent paid
   else Lander cannot afford rent
     Logic -> Logic : handle_bankruptcy(Lander)
     Logic --> Lander : return "bankrupt"
   end
   deactivate Logic
   @enduml

**Card Draw**

.. uml::
   :caption: Sequence Diagram: Card Draw

   @startuml
   participant "player:dict" as Player
   participant "logic:GameLogic" as Logic
   participant "cards:list" as Cards
   participant "game:Game" as GameUI

   Logic -> Logic : handle_space(Player)
   note right: Called after move to card space
   activate Logic
   Logic -> Cards : card = cards.pop(0)
   Logic -> Logic : add_message(card('text'))
   Logic -> GameUI : show_card_popup(card_type, card('text'))
   alt Card is "Get Out of Jail Free"
     Logic -> Logic : jail_free_cards(Player('name')) += 1
   else Card has action
     Logic -> card : action(Player, bank, parking, self)
     note right: Execute lambda
     note right: Lambda might modify Player money, position, bank, parking
     note right: Lambda might call other Logic methods (e.g., handle_payment_to_bank)
     opt Action resulted in move
        Logic -> Logic : handle_space(Player)
        note right: Handle new space
     endopt
   end
   Logic -> Cards : cards.append(card)
   note right: Put card back at end
   Logic --> Player : return result, message
   deactivate Logic
   @enduml

**Auction Bid Process**

.. uml::
   :caption: Sequence Diagram: Auction Bid

   @startuml
   actor User/AI
   participant "game:Game" as GameUI
   participant "logic:GameLogic" as Logic
   participant "auction_state:dict" as Auction

   User/AI -> GameUI : Submit Bid Amount
   GameUI -> Logic : process_auction_bid(player, bid_amount)
   activate Logic
   Logic -> Auction : Get current_auction state
   alt Bid is valid (>= min_bid, <= player_money, player active)
     Logic -> Auction : current_bid = bid_amount
     Logic -> Auction : highest_bidder = player
     Logic -> Auction : minimum_bid = bid_amount + 10
     Logic -> Logic : add_message(...)
     Logic -> Logic : move_to_next_bidder()
     Logic --> GameUI : return True, "Bid accepted"
   else Bid is invalid
     Logic --> GameUI : return False, "Error message"
   end
   deactivate Logic
   GameUI -> GameUI : Update Auction UI
   @enduml

Key Classes/Data Overview
-------------------------

*   **GameLogic**: The main orchestrator class holding game state and rules logic.
*   **Player Dictionary**: Represents a player's state (money, position, properties, AI status, jail status, etc.).
*   **Property Dictionary**: Represents a property's state (owner, houses, mortgage status, rent levels, etc.), keyed by board position.
*   **Card Dictionary**: Represents a Pot Luck or Opportunity Knocks card, containing its text and an action (lambda function) to execute.
*   **Auction Dictionary (`current_auction`)**: Holds the state of an ongoing auction (property, bidders, current bid, etc.).

API Documentation
-----------------

.. automodule:: src.Game_Logic
   :members:
   :undoc-members:
   :show-inheritance: