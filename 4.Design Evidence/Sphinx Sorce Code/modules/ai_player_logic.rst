AI Player Logic Module
======================

This module defines the logic and strategies for Artificial Intelligence (AI) players within the Property Tycoon game. It provides different AI personalities or difficulty levels, encapsulating the decision-making processes for various game situations like buying properties, bidding in auctions, managing assets, and handling jail time.

The AI Player Logic module provides:

*   **EasyAIPlayer:** A baseline AI implementing straightforward decision rules based on predefined strategy parameters (e.g., bid multipliers, development thresholds).
*   **HardAIPlayer:** A more complex AI that builds upon the Easy AI logic but introduces a 'mood' or 'emotion' system. This mood modifier influences decisions, making the AI more aggressive or conservative depending on hunman player's selection.
*   Methods for evaluating property value from the AI's perspective.
*   Logic for deciding whether to buy properties, bid in auctions, develop properties, mortgage/unmortgage assets, and handle jail situations.
*   Helper functions for analyzing property groups and ownership.

.. automodule:: src.Ai_Player_Logic
   :members:
   :undoc-members:
   :show-inheritance:

High-Level Design
-----------------

 Use Case Diagram (AI Decision Making)

Illustrates the primary decision points where the Game Logic interacts with the AI Player Logic module.

.. uml::

    @startuml
    actor "Game Logic" as GameLogic

    rectangle "AI Player Logic Module" {
      GameLogic -- (Request Purchase Decision)
      GameLogic -- (Request Auction Bid)
      GameLogic -- (Request Jail Action)
      GameLogic -- (Request Development Decision)
      GameLogic -- (Request Mortgage Decision)
      GameLogic -- (Request Trade Evaluation)

      (Request Purchase Decision) ..> (Evaluate Property Value) : include
      (Request Purchase Decision) ..> (Check Affordability) : include
      (Request Purchase Decision) ..> (Apply Strategy/Mood) : include

      (Request Auction Bid) ..> (Evaluate Property Value) : include
      (Request Auction Bid) ..> (Check Affordability) : include
      (Request Auction Bid) ..> (Apply Strategy/Mood) : include

      (Request Jail Action) ..> (Check Resources) : include
      (Request Jail Action) ..> (Apply Strategy/Mood) : include

      (Request Development Decision) ..> (Check Affordability) : include
      (Request Development Decision) ..> (Check Group Ownership) : include
      (Request Development Decision) ..> (Apply Strategy/Mood) : include

      (Request Mortgage Decision) ..> (Evaluate Financial Need) : include
      (Request Mortgage Decision) ..> (Prioritize Properties) : include
      (Request Mortgage Decision) ..> (Apply Strategy/Mood) : include

      (Request Trade Evaluation) ..> (Evaluate Property Value) : include
      (Request Trade Evaluation) ..> (Apply Strategy/Mood) : include
    }

    note right of "AI Player Logic Module"
      Decisions for HardAIPlayer
      are influenced by an internal
      'mood' state.
    end note
    @enduml

 Domain Model (AI Logic Concepts)

Shows the core concepts involved in the AI's decision-making process.

.. uml::

   @startuml
    class AIPlayerLogic {
       difficulty : String
    }

    class EasyAIPlayerLogic {
       strategy : Map
       decide_purchase()
       decide_bid()
       decide_jail()
       decide_development()
       decide_mortgage()
    }

    class HardAIPlayerLogic {
       easy_ai : EasyAIPlayerLogic
       mood_modifier : Float
       update_mood()
       decide_purchase()
       decide_bid()
       decide_jail()
       decide_development()
    }

    class PropertyData {
       name : String
       price : Integer
       group : String
       owner : String
       houses : Integer
       is_mortgaged : Boolean
       is_station : Boolean
       is_utility : Boolean
    }

    class PlayerData {
       name : String
       money : Integer
       properties : PropertyData[]
       in_jail : Boolean
       jail_free_cards : Integer
    }

    note right of EasyAIPlayerLogic : Predefined parameters

    note right of HardAIPlayerLogic : Uses base logic

    EasyAIPlayerLogic --> AIPlayerLogic
    HardAIPlayerLogic --> AIPlayerLogic
    AIPlayerLogic .. PropertyData
    AIPlayerLogic .. PlayerData
    HardAIPlayerLogic *-- EasyAIPlayerLogic
   @enduml

Detailed Design
---------------

 AI Player Class Diagram

Details the structure of `EasyAIPlayer` and `HardAIPlayer`, their methods, and relationship.

.. uml::

    @startuml
    interface AIPlayer {
       + get_property_value(property_data, ai_player, board_properties) : float
       + get_auction_bid(current_minimum, property_data, ai_player, board_properties) : int
       + handle_jail_strategy(ai_player, jail_free_cards) : str
       + handle_property_development(ai_player, board_properties) : Property
       + should_buy_property(property_data, player_money, owned_properties) : bool
       + should_mortgage_property(property_data, player_money) : bool
       + consider_trade_offer() : bool
    }

    class EasyAIPlayer {
       + difficulty : str
       + strategy : Map<String, float>
       + __init__(difficulty)
       + get_group_properties(color_group, board_properties) : List<PropertyData>
       + check_group_ownership(color_group, board_properties, player_name) : bool
       + can_build_house(property, color_group_properties) : bool
       + get_property_value(property_data, ai_player, board_properties) : float
       + handle_turn(ai_player, current_location, board_properties, is_first_round) : Map
       + should_use_get_out_of_jail_card() : bool
       + should_pay_jail_fine(ai_player) : bool
       + should_mortgage_property(ai_player, required_money) : List<Property>
       + handle_ai_turn(ai_player, board_properties) : bool
       + get_location_type(position, board_properties) : str
       + get_property_name(position, board_properties) : str
       + get_auction_bid(current_minimum, property_data, ai_player, board_properties) : int
       + handle_jail_strategy(ai_player, jail_free_cards) : str
       + handle_property_development(ai_player, board_properties) : Map
       + handle_emergency_cash(ai_player, required_amount, board_properties) : List<Property>
       + consider_trade_offer() : bool
       + should_buy_property(property_data, player_money, owned_properties) : bool
       + make_auction_bid(property_data, current_bid, player_money, owned_properties) : int
       + should_develop_property(property_data, player_money, owned_properties) : bool
       + should_mortgage_property(property_data, player_money) : bool
       + should_unmortgage_property(property_data, player_money) : bool
       + should_sell_houses(property_data, player_money, target_amount) : bool
       + get_development_priority(properties) : List<Property>
    }

    class HardAIPlayer {
       + difficulty : str
       + mood_modifier : float
       - easy_ai : EasyAIPlayer
       + __init__()
       + update_mood(is_happy)
       + get_adjusted_probability(base_probability) : float
       + get_property_value(property_data, ai_player, board_properties) : float
       + get_auction_bid(current_minimum, property_data, ai_player, board_properties) : int
       + handle_jail_strategy(ai_player, jail_free_cards) : str
       + should_mortgage_property(ai_player, required_money) : list
       + handle_property_development(ai_player, board_properties) : dict
       + should_buy_property(property_data, player_money, owned_properties) : bool
    }

    note right of EasyAIPlayer::strategy
      Contains parameters like:
      - max_bid_multiplier
      - development_threshold
      - jail_stay_threshold
      - mortgage_threshold
    end note

    note right of EasyAIPlayer::handle_turn
      More complex than interface suggests
    end note

    note right of EasyAIPlayer::should_mortgage_property
      Returns list of props to mortgage
    end note

    note right of EasyAIPlayer::handle_ai_turn
      Simplified decision logic?
    end note

    note right of EasyAIPlayer::handle_property_development
      Returns property dict
    end note

    note right of EasyAIPlayer::make_auction_bid
      Seems redundant with get_auction_bid?
    end note

    note right of EasyAIPlayer::should_mortgage_property
      Different signature than above
    end note

    note right of HardAIPlayer::get_property_value
      Wraps EasyAI
    end note

    note right of HardAIPlayer::get_auction_bid
      Wraps EasyAI
    end note

    note right of HardAIPlayer::handle_jail_strategy
      Wraps EasyAI
    end note

    note right of HardAIPlayer::should_mortgage_property
      Delegates to EasyAI
    end note

    note right of HardAIPlayer::handle_property_development
      Wraps EasyAI
    end note

    note right of HardAIPlayer::should_buy_property
      Wraps EasyAI
    end note

    note bottom of HardAIPlayer
      HardAIPlayer uses an instance of EasyAIPlayer
      to get baseline decisions, then modifies them
      based on the `mood_modifier`.
    end note

    HardAIPlayer o-- EasyAIPlayer : uses
    EasyAIPlayer ..|> AIPlayer
    HardAIPlayer ..|> AIPlayer

    AIPlayer ..> "Property" : uses data
    AIPlayer ..> "Player" : uses data
    @enduml

Activity Diagram: Hard AI Auction Bid Decision

Illustrates the flow for `HardAIPlayer.get_auction_bid`, showing the interaction with `EasyAIPlayer` and the mood influence.

.. uml::

    @startuml
    participant "GameLogic" as Caller
    participant "HardAIPlayer" as HardAI
    participant "EasyAIPlayer" as EasyAI

    Caller -> HardAI : get_auction_bid(min_bid, property_data, player_data, board_props)
    activate HardAI
    HardAI -> EasyAI : get_auction_bid(min_bid, property_data, player_data, board_props)
    activate EasyAI
    EasyAI -> EasyAI : get_property_value(...)
    activate EasyAI
    EasyAI --> EasyAI : perceived_value
    deactivate EasyAI
    EasyAI --> HardAI : base_bid
    deactivate EasyAI
    
    alt base_bid is None
        HardAI -> HardAI : get_adjusted_probability(0.0)
        HardAI --> HardAI : angry_bid_chance
        
        alt //random()// < angry_bid_chance // Commented out random()
            HardAI -> HardAI : get_property_value(...)
            HardAI --> HardAI : perceived_value_hard
            HardAI -> HardAI : Calculate emotion_bid
            HardAI --> HardAI : emotion_bid
            HardAI --> Caller : emotion_bid
        else
            HardAI --> Caller : None
        end
    else
        HardAI -> HardAI : Calculate mood_multiplier
        HardAI --> HardAI : mood_multiplier
        HardAI -> HardAI : final_bid = base_bid * mood_multiplier
        HardAI -> HardAI : Calculate max_percentage based on mood
        HardAI --> HardAI : max_percentage
        HardAI -> HardAI : Cap final_bid by player_data.money * max_percentage
        HardAI --> HardAI : capped_final_bid
        HardAI --> Caller : capped_final_bid
    end
    
    deactivate HardAI
    @enduml

Sequence Diagram: Hard AI Purchase Decision (`should_buy_property`)

Shows `HardAIPlayer` deciding whether to buy, potentially overriding the `EasyAIPlayer` logic based on mood.

.. uml::

    @startuml
    participant "GameLogic" as Caller
    participant "HardAIPlayer" as HardAI
    participant "EasyAIPlayer" as EasyAI

    Caller -> HardAI : should_buy_property(property_data, player_money, owned_properties)
    activate HardAI
    HardAI -> EasyAI : should_buy_property(property_data, player_money, owned_properties)
    activate EasyAI
    EasyAI -> EasyAI : get_property_value(property_data, owned_properties, player_money)
    activate EasyAI
    EasyAI --> EasyAI : property_value
    deactivate EasyAI
    EasyAI --> HardAI : base_decision
    deactivate EasyAI
    
    alt not base_decision and player_money >= property_data.price
        HardAI -> HardAI : get_adjusted_probability(0.2)
        HardAI --> HardAI : buy_chance
        HardAI -> HardAI : Calculate max_price_ratio based on mood
        HardAI --> HardAI : max_price_ratio
        HardAI -> HardAI : can_afford = (player_money * max_price_ratio >= property_data.price)
        HardAI --> HardAI : can_afford_result
        
        alt can_afford_result and //random()// < buy_chance // Commented out random()
            HardAI --> Caller : True
            deactivate HardAI
        end
    else base_decision and mood_modifier < 0
        HardAI -> HardAI : Calculate pass_chance (-mood_modifier * 1.5)
        HardAI --> HardAI : pass_chance
        
        alt //random()// < pass_chance // Commented out random()
            HardAI --> Caller : False
            deactivate HardAI
        end
    end
    
    HardAI --> Caller : base_decision
    deactivate HardAI
    @enduml

Sequence Diagram: Updating AI Mood (`update_mood`)

Shows the simple process of adjusting the `mood_modifier`.

.. uml::

    @startuml
    participant "GameLogic" as Caller
    participant "HardAIPlayer" as HardAI

    Caller -> HardAI : update_mood(is_happy=True)
    activate HardAI
    
    alt is_happy is True
        HardAI -> HardAI : mood_modifier = max(-0.3, mood_modifier - 0.05)
    else is_happy is False
        HardAI -> HardAI : mood_modifier = min(0.3, mood_modifier + 0.05)
    end
    
    HardAI --> Caller : return
    deactivate HardAI
    @enduml
