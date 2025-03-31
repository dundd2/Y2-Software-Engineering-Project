Game Actions Module
===================

This module contains the GameActions class that implements various game actions and commands that players can execute during the game, such as rolling dice, buying properties, and ending turns.

Key Features
------------

* **Action Execution**: Processing player-initiated game actions
* **Command Pattern**: Implementation of the command pattern for game operations
* **Action Validation**: Verification that actions are valid in the current game state
* **Player Interaction**: Handling player decisions and inputs
* **Game State Updates**: Modifying game state based on action results
* **AI Action Integration**: Support for AI-triggered game actions

GameActions Class
-----------------

The GameActions class encapsulates game action functionality:

.. plantuml::

   @startuml
   
   class GameActions {
     -game : Game
     -game_logic : GameLogic
     -available_actions : Dict
     
     +__init__(game, game_logic)
     +execute_action(action_name, parameters)
     +get_available_actions(player, game_state)
     +handle_roll_dice()
     +handle_buy_property(property_data)
     +handle_pass_property(property_data)
     +handle_end_turn()
     +handle_mortgage_property(property_data)
     +handle_unmortgage_property(property_data)
     +handle_build_house(property_data)
     +handle_build_hotel(property_data)
     +handle_auction_bid(amount)
     +handle_trade_offer(offer_data)
     +handle_trade_response(response)
     +handle_use_jail_card()
     +handle_pay_jail_fine()
     +handle_draw_card(card_type)
}}}}}}}}
   
   @enduml

Action Execution System
-----------------------

The module implements an action execution system:

.. plantuml::

   @startuml
   
   title Action Execution System
   
   start
   
   :Receive Action Request;
   
   :Extract Action Name and Parameters;
   
   :Look Up Action Handler;
   
   if (Action Exists?) then (Yes)
     :Check Action Preconditions;
     
     if (Action Valid?) then (Yes)
       :Execute Action Handler;
       
       :Process Action Results;
       
       :Update Game State;
       
       :Trigger Action Callbacks;
       
       :Return Success Result;
     else (No)
       :Log Invalid Action;
       
       :Return Error Result;
     endif
   else (No)
     :Log Unknown Action;
     
     :Return Error Result;
   endif
   
   stop
   
   @enduml

Available Actions
-----------------

The module provides a variety of player actions:

.. plantuml::

   @startuml
   
   title Available Game Actions
   
   package "Turn Actions" {
     class "Roll Dice" as RollDice {
       Move player based on
       dice roll result
}}}}}}}}}}}}}}}}
     
     class "End Turn" as EndTurn {
       Complete current turn
       and move to next player
}}}
   }
   
   package "Property Actions" {
     class "Buy Property" as BuyProperty {
       Purchase an unowned property
       player has landed on

     
     class "Pass Property" as PassProperty {
       Decline to purchase property
       and trigger auction
}}}}}}}}}}}}}}}}}}}
     
     class "Mortgage Property" as Mortgage {
       Mortgage owned property
       to receive funds
}}}}}}}}}}}}}}}}
     
     class "Unmortgage Property" as Unmortgage {
       Pay to unmortgage
       a property
}}}}}}}}}}
   }
   
   package "Development Actions" {
     class "Build House" as BuildHouse {
       Build a house on
       a property
}}}}}}}}}}
     
     class "Build Hotel" as BuildHotel {
       Upgrade from 4 houses
       to a hotel
}}}}}}}}}}
     
     class "Sell House" as SellHouse {
       Sell a house from
       a property
}}}}}}}}}}
     
     class "Sell Hotel" as SellHotel {
       Downgrade from hotel
       to 4 houses
}}}}}}}}}}}
   }
   
   package "Special Actions" {
     class "Auction Bid" as Bid {
       Place bid during
       property auction
}}}}}}}}}}}}}}}}
     
     class "Trade Offer" as TradeOffer {
       Initiate trade with
       another player
}}}}}}}}}}}}}}
     
     class "Use Jail Card" as UseJailCard {
       Use get out of jail
       free card
}}}}}}}}}
     
     class "Pay Jail Fine" as PayJailFine {
       Pay fine to exit jail
}
   }
   
   class GameActions {
     +execute_action(action_name, parameters)

   
   GameActions --> RollDice : provides
   GameActions --> EndTurn : provides
   GameActions --> BuyProperty : provides
   GameActions --> PassProperty : provides
   GameActions --> Mortgage : provides
   GameActions --> Unmortgage : provides
   GameActions --> BuildHouse : provides
   GameActions --> BuildHotel : provides
   GameActions --> SellHouse : provides
   GameActions --> SellHotel : provides
   GameActions --> Bid : provides
   GameActions --> TradeOffer : provides
   GameActions --> UseJailCard : provides
   GameActions --> PayJailFine : provides
   
   @enduml

Action Validation
-----------------

The module validates actions before execution:

.. plantuml::

   @startuml
   
   title Action Validation Process
   
   start
   
   :Receive Action Request;
   
   :Determine Current Game State;
   
   :Get Current Player;
   
   :Check Basic Preconditions;
   note right
     - Is it the player's turn?
     - Is action allowed in current state?
     - Is player not bankrupt?
   end note
   
   if (Basic Preconditions Met?) then (Yes)
     :Check Action-Specific Conditions;
     
     if (Action?) then (Buy Property)
       :Verify Player Landed on Property;
       :Verify Property is Unowned;
       :Verify Player Can Afford Property;
     else if (Action?) then (Build House)
       :Verify Player Owns Property;
       :Verify Player Owns Color Group;
       :Verify Even Development Rule;
       :Verify Houses Available in Bank;
       :Verify Player Can Afford House;
     else if (Action?) then (End Turn)
       :Verify Player Has Completed Movement;
       :Verify Required Actions Completed;
     else if (Action?) then (Other Actions)
       :Check Other Action-Specific Rules;
     endif
     
     if (Action-Specific Conditions Met?) then (Yes)
       :Action is Valid;
     else (No)
       :Action is Invalid;
       :Generate Error Message;
     endif
   else (No)
     :Action is Invalid;
     :Generate Error Message;
   endif
   
   :Return Validation Result;
   
   stop
   
   @enduml

Roll Dice Action
----------------

The roll dice action is a core gameplay mechanic:

.. plantuml::

   @startuml
   
   title Roll Dice Action Flow
   
   start
   
   :Player Requests Roll Dice;
   
   :Validate Player Can Roll;
   note right
     Validate that:
     - It's player's turn
     - Player hasn't rolled yet
   end note
   
   if (Player in Jail?) then (Yes)
     :Process Jail Roll;
     
     if (Doubles Rolled?) then (Yes)
       :Release from Jail;
     else (No)
       :Increment Jail Turn Count;
       
       if (Jail Turns >= 3?) then (Yes)
         :Force Pay Jail Fine;
         :Release from Jail;
       endif
     endif
   endif
   
   if (Can Move?) then (Yes)
     :Generate Dice Values;
     
     :Animate Dice Roll;
     
     :Calculate Total Steps;
     
     :Move Player on Board;
     
     :Handle Landing Square;
     note right
       Process effects of
       the landing square
     end note
     
     if (Doubles Rolled?) then (Yes)
       :Grant Extra Turn;
       
       if (Doubles Count == 3?) then (Yes)
         :Send to Jail;
       endif
     endif
   endif
   
   :Update Game State;
   
   stop
   
   @enduml

Property Purchase Action
------------------------

The buy property action allows players to acquire properties:

.. plantuml::

   @startuml
   
   title Buy Property Action Flow
   
   start
   
   :Player Requests Buy Property;
   
   :Validate Purchase Eligibility;
   note right
     Validate that:
     - Property is unowned
     - Player is on property
     - Player can afford price
   end note
   
   if (Valid Purchase?) then (Yes)
     :Deduct Property Price from Player;
     
     :Assign Property to Player;
     
     :Add Property to Player's Portfolio;
     
     :Update Property Display;
     
     :Play Purchase Sound;
     
     :Create Notification;
     
     if (Player is AI?) then (Yes)
       :Display AI Decision Explanation;
     endif
     
     :Check for Property Group Completion;
     
     if (Group Completed?) then (Yes)
       :Show Group Completion Notification;
     endif
     
     :Update Available Actions;
   else (No)
     :Show Error Message;
   endif
   
   stop
   
   @enduml

Integration with Game Module
----------------------------

The GameActions module integrates with several other components:

.. plantuml::

   @startuml
   
   title GameActions Integration
   
   class GameActions {
     +execute_action(action_name, parameters)
     +handle_roll_dice()
     +handle_buy_property(property_data)
     +handle_end_turn()
}}}}}}}}}}}}}}}}}}
   
   class Game {
     -game_actions : GameActions
     -game_logic : GameLogic
     -current_player : Player
     -state : String
     
     +handle_action(action_name)
     +process_turn()
     +update_state()
}}}}}}}}}}}}}}}
   
   class GameLogic {
     +roll_dice()
     +move_player(player, steps)
     +handle_property_landing(player, property)
     +transfer_property(property, player)
}}}}}}}}}}}}}}}}
   
   class Player {
     +money : int
     +properties : List
     +position : int
     +pay(amount)
     +receive(amount)
     +add_property(property)
}}}
   
   class Property {
     +owner : Player
     +price : int
     +calculate_rent(dice_roll)
}}}}}}
   
   class GameEventHandler {
     +handle_click(position)
     +is_button_clicked(button_name)
}}}}}}}}}}}
   
   Game *-- GameActions
   Game *-- GameLogic
   GameActions --> GameLogic : uses
   GameActions --> Player : modifies
   GameActions --> Property : manages
   GameEventHandler --> GameActions : triggers
   
   @enduml

Action Result Processing
------------------------

The module handles action results and updates game state:

.. plantuml::

   @startuml
   
   title Action Result Processing
   
   start
   
   :Execute Game Action;
   
   :Generate Action Result;
   note right
     Result contains:
     - Success/failure status
     - Effect descriptions
     - State changes
     - Messages for players
   end note
   
   :Process Result in Game;
   
   if (Action Successful?) then (Yes)
     :Apply State Changes;
     
     :Update UI Elements;
     
     :Play Sound Effects;
     
     :Display Notifications;
     
     :Update Available Actions;
     
     if (Game State Change Needed?) then (Yes)
       :Change Game State;
     endif
     
     if (Next Player Needed?) then (Yes)
       :Update Current Player;
     endif
   else (No)
     :Display Error Message;
     
     :Log Error;
     
     :Play Error Sound;
   endif
   
   stop
   
   @enduml

Class Documentation
-----------------

.. automodule:: src.GameActions
   :members:
   :undoc-members:
   :show-inheritance: