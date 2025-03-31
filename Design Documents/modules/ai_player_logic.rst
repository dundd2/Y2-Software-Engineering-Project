AI Player Logic Module
======================

This module contains the logic for AI players in the game, implementing different difficulty levels and strategic decision-making processes for computer-controlled players.

Key Features
------------

* **Multi-level AI System**: Supports different difficulty levels (Easy and Hard)
* **Sophisticated Decision Making**: AI evaluates complex game states to make strategic choices
* **Property Valuation System**: Dynamic property value assessment for purchases and auctions
* **Strategic Development**: Intelligent house and hotel building strategies
* **Financial Planning**: AI manages its finances to avoid bankruptcy
* **Jail Strategy System**: Decision making for jail scenarios
* **Trade Evaluation**: Assessment of trade proposals from other players
* **Emotion System**: Hard AI implements an emotional state system that affects decision making

AI Player Types
---------------

The module implements two main types of AI players:

1. **EasyAIPlayer**: A more forgiving AI that makes predictable decisions, suitable for casual players
2. **HardAIPlayer**: A more challenging AI that makes strategically sound decisions with emotional variability

AI Strategy Components
----------------------

Each AI player type implements various strategic components:

* **Property Purchasing**: Evaluates whether to buy an unowned property
* **Auction Bidding**: Calculates appropriate bid amounts based on property valuation
* **Property Development**: Decides when to build houses and hotels
* **Mortgage Management**: Strategic decisions about mortgaging and unmortgaging properties
* **Trade Evaluation**: Assesses the value of proposed trades
* **Emergency Cash Management**: Strategies for raising funds when needed
* **Jail Decision-Making**: Choosing between paying a fine, using a card, or rolling for doubles

Property Valuation System
-------------------------

The AI uses a sophisticated property valuation system that considers:

* **Base Property Value**: The listed price of the property
* **Color Group Completion**: Higher value for properties that complete a color group
* **Existing Ownership**: Value increases for properties in groups where the AI already owns properties
* **Station and Utility Synergy**: Value increases based on how many stations or utilities the AI already owns
* **Strategic Position**: Value adjustments based on board position and landing probability
* **Emotional Bias**: (Hard AI only) Value adjustments based on current emotional state

Class Documentation
-------------------

.. plantuml::

   @startuml
   
   class EasyAIPlayer {
     -difficulty : String
     -strategy : Dictionary
     +__init__(difficulty="easy")
     +get_group_properties(color_group, board_properties)
     +check_group_ownership(color_group, board_properties, player_name)
     +can_build_house(property, color_group_properties)
     +get_property_value(property_data, ai_player, board_properties)
     +handle_turn(ai_player, current_location, board_properties, is_first_round)
     +should_use_get_out_of_jail_card()
     +should_pay_jail_fine(ai_player)
     +should_mortgage_property(ai_player, required_money)
     +handle_ai_turn(ai_player, board_properties)
     +get_location_type(position, board_properties)
     +get_property_name(position, board_properties)
     +get_auction_bid(current_minimum, property_data, ai_player, board_properties)
     +handle_jail_strategy(ai_player, jail_free_cards)
     +handle_property_development(ai_player, board_properties)
     +handle_emergency_cash(ai_player, required_amount, board_properties)
     +consider_trade_offer(ai_player, offered_properties, requested_properties, cash_difference, board_properties)
     +should_buy_property(property_data, player_money, owned_properties)
     +make_auction_bid(property_data, current_bid, player_money, owned_properties)
     +should_develop_property(property_data, player_money, owned_properties)
     +should_mortgage_property(property_data, player_money)
     +should_unmortgage_property(property_data, player_money)
     +should_sell_houses(property_data, player_money, target_amount)
     +get_development_priority(properties)
}}}}}}}}}}}}}}}}}
   
   class HardAIPlayer {
     -difficulty : String
     -mood_modifier : Float
     -easy_ai : EasyAIPlayer
     +__init__()
     +update_mood(is_happy)
     +get_adjusted_probability(base_probability)
     +get_property_value(property_data, ai_player, board_properties)
     +get_auction_bid(current_minimum, property_data, ai_player, board_properties)
     +handle_jail_strategy(ai_player, jail_free_cards)
     +should_mortgage_property(ai_player, required_money)
     +handle_property_development(ai_player, board_properties)
     +should_buy_property(property_data, player_money, owned_properties)
}}}}}}}
   
   HardAIPlayer --> EasyAIPlayer : uses
   
   @enduml

EasyAIPlayer Class
------------------

The ``EasyAIPlayer`` class implements a more forgiving AI strategy with the following key methods:

* ``get_property_value``: Calculates the perceived value of a property
* ``should_buy_property``: Determines whether to purchase a property
* ``make_auction_bid``: Calculates appropriate auction bid amounts
* ``handle_jail_strategy``: Decides how to handle being in jail
* ``handle_property_development``: Evaluates development opportunities
* ``handle_emergency_cash``: Raises funds when needed
* ``check_group_ownership``: Checks if a complete color group is owned
* ``should_sell_houses``: Determines when to sell houses to raise funds

HardAIPlayer Class
------------------

The ``HardAIPlayer`` class extends the EasyAIPlayer with an emotional intelligence system:

* **Emotion System**: Maintains a mood modifier that affects decision making
* **Enhanced Valuation**: Adjusts property valuation based on emotional state
* **Dynamic Bidding**: More aggressive or conservative bidding based on mood
* **Emotional Responses**: Can make "irrational" decisions based on emotion
* **Mood Tracking**: Mood ranges from angry (+0.3) to happy (-0.3)
* **Player Interaction**: Players can influence the AI's mood through taunting

Key methods include:
* ``update_mood``: Changes the AI's emotional state
* ``get_adjusted_probability``: Adjusts decision probabilities based on mood
* ``get_property_value``: Overrides basic valuation with emotional factors
* ``get_auction_bid``: Makes emotionally influenced bidding decisions
* ``handle_jail_strategy``: Jail decisions affected by emotional state
* ``should_buy_property``: Purchase decisions with emotional influence

Decision-Making Process
-----------------------

The AI's decision-making process involves several steps:

1. **Situation Assessment**: Analyzing the current game state
2. **Option Generation**: Identifying possible actions
3. **Option Evaluation**: Calculating the expected value of each action
4. **Action Selection**: Choosing the action with the highest expected value
5. **Emotional Adjustment**: (Hard AI only) Modifying decisions based on emotional state

For property purchases, the AI considers:
* Current cash reserves
* Property's intrinsic value
* Potential for completing color groups
* Expected return on investment
* Emotional biases (Hard AI)

For development decisions, the AI evaluates:
* Cash availability
* Return on investment for houses/hotels
* Risk of landing on expensive properties
* Strategic value of blocking other players
* Emotional tendencies toward risk (Hard AI)

Difficulty Adjustment
---------------------

.. plantuml::

   @startuml
   
   title AI Difficulty Adjustment and Decision Flow
   
   start
   
   if (AI Type?) then (Easy AI)
     :Use Conservative Strategies;
     :Apply Static Decision Thresholds;
     :Predictable Decision Making;
   else (Hard AI)
     :Initialize Emotion System;
     :Apply Dynamic Decision Thresholds;
     
     repeat
       :Update Emotional State;
       :Adjust Base Probabilities;
       :Apply Emotional Multipliers;
     
       if (mood_modifier > 0) then (Angry)
         :More Aggressive Bidding;
         :Higher Risk Tolerance;
         :More Impulsive Decisions;
       else (Happy)
         :More Conservative Bidding;
         :Lower Risk Tolerance;
         :More Calculated Decisions;
       endif
     repeat while (Game Continues)
   endif
   
   stop
   
   @enduml

Hard AI Emotion System
----------------------

The Hard AI implements an emotional system that makes its behavior less predictable:

* **Mood Modifier**: A value ranging from -0.3 (happy) to +0.3 (angry)
* **Decision Impact**: Emotional state affects bidding, purchases, and strategy
* **Player Interaction**: Human players can taunt the AI to make it happier or angrier
* **Strategy Adjustment**:
  * Happy AI: More conservative, less likely to take risks
  * Angry AI: More aggressive, more likely to make impulsive decisions

.. plantuml::

   @startuml
   
   title Hard AI Emotion System
   
   state "Neutral\nMood: 0.0" as Neutral
   state "Slightly Happy\nMood: -0.15" as SlightlyHappy
   state "Happy\nMood: -0.3" as Happy
   state "Slightly Angry\nMood: 0.15" as SlightlyAngry
   state "Angry\nMood: 0.3" as Angry
   
   [*] -> Neutral
   
   Neutral -down-> SlightlyHappy : Player praises
   Neutral -up-> SlightlyAngry : Player taunts
   
   SlightlyHappy -down-> Happy : Player praises
   SlightlyHappy -up-> Neutral : Player taunts
   
   Happy -up-> SlightlyHappy : Player taunts
   
   SlightlyAngry -up-> Angry : Player taunts
   SlightlyAngry -down-> Neutral : Player praises
   
   Angry -down-> SlightlyAngry : Player praises
   
   note right of Happy
     Decision effects:
     * Property value adjustments: -30%
     * Bidding aggression: -30%
     * Risk tolerance: -30%
   end note
   
   note right of Angry
     Decision effects:
     * Property value adjustments: +30%
     * Bidding aggression: +30%
     * Risk tolerance: +30%
   end note
   
   @enduml

AI Integration with Player Module
---------------------------------

.. plantuml::

   @startuml
   
   title AI Player Integration with Player Module
   
   class Player {
     +name : String
     +position : int
     +money : int
     +properties : List
     +is_ai : Boolean
     +ai_difficulty : String
     +ai_controller : EasyAIPlayer or HardAIPlayer
     +__init__(name, player_number, is_ai, ai_difficulty)
     +pay(amount)
     +receive(amount)
     +buy_property(property)
     +handle_jail_turn()
     +handle_ai_decisions()
     +...()
}}}}}}
   
   class EasyAIPlayer {
     +handle_turn()
     +handle_jail_strategy()
     +should_buy_property()
     +...()
}}}}}}
   
   class HardAIPlayer {
     +mood_modifier : Float
     +update_mood()
     +handle_turn()
     +...()
}}}}}}
   
   Player "1" *-- "0..1" EasyAIPlayer : if is_ai=true and\nai_difficulty="easy"
   Player "1" *-- "0..1" HardAIPlayer : if is_ai=true and\nai_difficulty="hard"
   
   @enduml

AI Property Valuation Logic
---------------------------

.. plantuml::

   @startuml
   
   title AI Property Valuation Process
   
   start
   
   :Get Base Property Price;
   :Initialize Value Multiplier = 1.0;
   
   if (Same Color Group Check) then (Has Properties)
     :Calculate Owned in Group;
     :Calculate Total in Group;
     :Apply Group Ownership Bonus;
     note right
       Bonus = 0.3 * (owned_in_group / total_in_group)
     end note
   endif
   
   if (Property Type Check) then (Station)
     :Count Owned Stations;
     :Apply Station Synergy Bonus;
     note right
       Bonus = 0.25 * owned_stations
     end note
   else if (Property Type Check) then (Utility)
     :Count Owned Utilities;
     :Apply Utility Synergy Bonus;
     note right
       Bonus = 0.2 * owned_utilities
     end note
   endif
   
   if (Available Money Check) then (Low Cash)
     :Apply Cash Shortage Penalty;
     note right
       Multiplier reduced if cash < 3x price
     end note
   endif
   
   if (Is Hard AI?) then (Yes)
     :Apply Emotional Adjustment;
     note right
       Adjustment = base_value * (1 + mood_modifier * 2)
     end note
   endif
   
   :Calculate Final Property Value;
   note right
     final_value = base_price * value_multiplier
   end note
   
   stop
   
   @enduml

AI Decision Tree for Property Purchase
--------------------------------------

.. plantuml::

   @startuml
   
   title AI Decision Tree for Property Purchase
   
   start
   
   if (Can Afford Property?) then (No)
     :Decline Purchase;
     stop
   endif
   
   :Calculate Property Value;
   
   if (Property Value >= Price?) then (Yes)
     if (Is Hard AI?) then (Yes)
       if (In Emotional State?) then (Angry)
         if (Random Check < Adjusted Probability) then (Yes)
           :Buy Property Even if Value < Price;
         else (No)
           :Buy Property;
         endif
       else if (In Emotional State?) then (Happy) 
         if (Random Check < Adjusted Probability) then (Yes)
           :Pass on Property Even if Value > Price;
         else (No)
           :Buy Property;
         endif
       else (Neutral)
         :Buy Property;
       endif
     else (Easy AI)
       :Buy Property;
     endif
   else (No)
     if (Is Hard AI?) then (Yes)
       if (In Emotional State?) then (Angry)
         if (Random Check < Adjusted Probability) then (Yes)
           :Buy Property Even if Value < Price;
         else (No)
           :Pass on Property;
         endif
       else (Not Angry)
         :Pass on Property;
       endif
     else (Easy AI)
       :Pass on Property;
     endif
   endif
   
   stop
   
   @enduml

Class Documentation
-----------------

.. automodule:: src.Ai_Player_Logic
   :members:
   :undoc-members:
   :show-inheritance: